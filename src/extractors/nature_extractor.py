"""
Nature journal extractor - clean implementation
No special cases, just straightforward extraction logic
"""

import re
import time
from typing import Optional, List, Dict
from urllib.parse import urljoin

from ..core import BaseExtractor
from ..models import Paper, Author, AuthorRole, JournalType, ExtractionResult


class NatureExtractor(BaseExtractor):
    """Nature journal paper extractor"""
    
    @property
    def journal_type(self) -> JournalType:
        return JournalType.NATURE
    
    @property
    def base_url(self) -> str:
        return "https://www.nature.com"
    
    def can_handle_url(self, url: str) -> bool:
        """Check if this extractor can handle the URL"""
        return 'nature.com' in url and '/articles/' in url
    
    def search_paper(self, title: str) -> Optional[str]:
        """Search Nature.com for a paper by title"""
        try:
            search_url = f"{self.base_url}/search"
            params = {'q': title}
            
            soup = self.make_request(search_url)
            
            # Look for article links
            article_links = soup.find_all('a', href=re.compile(r'/articles/'))
            for link in article_links:
                href = link.get('href')
                if href and '/articles/' in href:
                    if href.startswith('/'):
                        return f"{self.base_url}{href}"
                    return href
            
            return None
            
        except Exception as e:
            self.logger.error(f"Nature search failed: {e}")
            return None
    
    def extract_paper_info(self, url: str) -> ExtractionResult:
        """Extract paper information from Nature URL"""
        start_time = time.time()
        
        try:
            soup = self.make_request(url)
            
            # Extract components
            title = self._extract_title(soup)
            abstract = self._extract_abstract(soup)
            authors = self._extract_authors(soup)
            
            # Extract metadata
            doi = self._extract_doi(soup)
            pub_date = self._extract_publication_date(soup)
            contributions = self._extract_contributions(soup)
            
            paper = Paper(
                title=title,
                abstract=abstract,
                authors=authors,
                journal=self.journal_type,
                url=url,
                doi=doi,
                publication_date=pub_date,
                contributions=contributions
            )
            
            extraction_time = time.time() - start_time
            
            result = ExtractionResult(
                success=True,
                paper=paper,
                extraction_time=extraction_time
            )
            
            if not self.validate_extraction(result):
                return ExtractionResult(
                    success=False,
                    error="Validation failed - incomplete data extracted",
                    extraction_time=extraction_time
                )
            
            return result
            
        except Exception as e:
            extraction_time = time.time() - start_time
            self.logger.error(f"Nature extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                extraction_time=extraction_time
            )
    
    def _extract_title(self, soup) -> str:
        """Extract title from Nature paper"""
        selectors = [
            'h1.c-article-title',
            'h1[data-test="article-title"]',
            'h1.article-title',
            'h1'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return self.clean_text(title_elem.get_text())
        
        return ""
    
    def _extract_abstract(self, soup) -> str:
        """Extract abstract from Nature paper"""
        selectors = [
            'div[data-test="abstract-section"] p',
            '#Abs1-content p',
            'section[data-title="Abstract"] p',
            'div.c-article-section__content p',
            'div.abstract p'
        ]
        
        for selector in selectors:
            paragraphs = soup.select(selector)
            if paragraphs:
                return ' '.join(self.clean_text(p.get_text()) for p in paragraphs)
        
        return ""
    
    def _extract_authors(self, soup) -> List[Author]:
        """Extract authors from Nature paper using detailed author search section"""
        authors = []
        
        try:
            # Get affiliations mapping first
            affiliations_map = self._extract_affiliations_mapping(soup)
            
            # Get corresponding authors with emails
            corresponding_authors = self._extract_corresponding_authors(soup)
            
            # Find the detailed author list section
            authors_list = soup.select("ol.c-article-authors-search > li")
            
            for i, li in enumerate(authors_list):
                # Extract author name
                name_elem = li.select_one(".js-search-name")
                if not name_elem:
                    continue
                
                clean_name = self.clean_text(name_elem.get_text())
                if not clean_name:
                    continue
                
                # Extract affiliation IDs from li id attribute
                li_id = li.get("id", "")
                aff_ids = [part for part in li_id.split("-") if part.startswith("Aff")]
                
                # Get affiliations for this author
                author_affiliations = []
                for aff_id in aff_ids:
                    if aff_id in affiliations_map:
                        author_affiliations.append(affiliations_map[aff_id])
                
                # Extract external links
                external_links = {}
                for a in li.select("a.c-article-identifiers__item"):
                    href = a.get("href", "")
                    if "pubmed" in href.lower():
                        external_links["PubMed"] = href
                    elif "scholar.google" in href.lower():
                        external_links["Google Scholar"] = href
                
                # Extract ORCID if available
                orcid = None
                orcid_link = li.find('a', href=lambda x: x and 'orcid.org' in x)
                if orcid_link:
                    orcid_url = orcid_link.get('href', '')
                    orcid_match = re.search(r'(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', orcid_url)
                    if orcid_match:
                        orcid = orcid_match.group(1)
                
                # Determine roles
                roles = []
                if i == 0:  # First author
                    roles.append(AuthorRole.FIRST)
                
                # Check if this is a corresponding author
                corr_author = next((ca for ca in corresponding_authors if ca["name"] == clean_name), None)
                if corr_author:
                    roles.append(AuthorRole.CORRESPONDING)
                
                if not roles:
                    roles.append(AuthorRole.REGULAR)
                
                # Create author object
                author = Author(
                    name=clean_name,
                    email=corr_author["email"] if corr_author else None,
                    orcid=orcid,
                    affiliations=author_affiliations,
                    roles=roles,
                    external_links=external_links if external_links else None
                )
                
                authors.append(author)
        
        except Exception as e:
            self.logger.error(f"Error extracting authors: {e}")
        
        return authors
    
    def _extract_affiliations_mapping(self, soup) -> dict:
        """Extract clean affiliations mapping from Nature paper using reference approach"""
        affiliations = {}
        
        # Use the same approach as reference implementation
        aff_list = soup.select("ol.c-article-author-affiliation__list > li")
        
        for li in aff_list:
            aff_id = li.get("id")
            
            # Extract clean address
            address_elem = li.select_one(".c-article-author-affiliation__address")
            if address_elem:
                clean_address = self.clean_text(address_elem.get_text())
                if clean_address:
                    affiliations[aff_id] = clean_address
        
        return affiliations
    
    def _extract_corresponding_authors(self, soup) -> List[Dict[str, str]]:
        """Extract corresponding authors with email addresses"""
        corresponding_authors = []
        
        # Extract from corresponding author list
        corr_auths = soup.select("#corresponding-author-list a")
        for a in corr_auths:
            name = self.clean_text(a.get_text())
            email = a.get("href", "").replace("mailto:", "")
            if name and email:
                corresponding_authors.append({
                    "name": name,
                    "email": email
                })
        
        return corresponding_authors
    
    def _extract_contributions(self, soup) -> Optional[str]:
        """Extract author contributions section"""
        try:
            # Look for contributions section using the same approach as reference
            contrib_elem = soup.select_one("#contributions + p")
            if contrib_elem:
                return self.clean_text(contrib_elem.get_text())
        except Exception as e:
            self.logger.error(f"Error extracting contributions: {e}")
        
        return None
    
    
    def _extract_doi(self, soup) -> Optional[str]:
        """Extract DOI from Nature paper"""
        # Try meta tag first
        doi_meta = soup.find('meta', {'name': 'citation_doi'})
        if doi_meta:
            return doi_meta.get('content', '')
        
        # Extract from page text
        page_text = soup.get_text()
        return self.extract_doi_from_text(page_text)
    
    def _extract_publication_date(self, soup) -> Optional[str]:
        """Extract publication date from Nature paper"""
        # Try time element
        time_elem = soup.find('time', {'datetime': True})
        if time_elem:
            datetime_str = time_elem.get('datetime', '')
            if 'T' in datetime_str:
                return datetime_str.split('T')[0]
            return datetime_str
        
        # Try meta tag
        date_meta = soup.find('meta', {'name': 'citation_publication_date'})
        if date_meta:
            return date_meta.get('content', '')
        
        return None