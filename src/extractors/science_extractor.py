"""
Science.org extractor - clean implementation
Handles the complex author-affiliation mapping without special cases
"""

import re
import time
from typing import Optional, List, Dict

from ..core import BaseExtractor
from ..models import Paper, Author, AuthorRole, JournalType, ExtractionResult


class ScienceExtractor(BaseExtractor):
    """Science.org paper extractor"""
    
    @property
    def journal_type(self) -> JournalType:
        return JournalType.SCIENCE
    
    @property
    def base_url(self) -> str:
        return "https://www.science.org"
    
    def can_handle_url(self, url: str) -> bool:
        """Check if this extractor can handle the URL"""
        return 'science.org' in url and '/doi/' in url
    
    def search_paper(self, title: str) -> Optional[str]:
        """Search Science.org for a paper by title"""
        try:
            search_url = f"{self.base_url}/action/doSearch"
            params = {
                'query': title,
                'searchType': 'quick',
                'target': 'default'
            }
            
            soup = self.make_request(search_url)
            
            # Look for DOI links in search results
            doi_links = soup.find_all('a', href=re.compile(r'/doi/10\.1126/'))
            
            for link in doi_links:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        return f"{self.base_url}{href}"
                    return href
            
            return None
            
        except Exception as e:
            self.logger.error(f"Science search failed: {e}")
            return None
    
    def extract_paper_info(self, url: str) -> ExtractionResult:
        """Extract paper information from Science.org URL"""
        start_time = time.time()
        
        try:
            # Try multiple access methods for Science.org
            soup = self._try_access_methods(url)
            
            if not soup:
                raise Exception("Could not access Science.org page")
            
            # Extract components
            title = self._extract_title(soup)
            abstract = self._extract_abstract(soup)
            authors = self._extract_authors_with_affiliations(soup)
            
            # Extract metadata
            doi = self._extract_doi(soup)
            pub_date = self._extract_publication_date(soup)
            
            paper = Paper(
                title=title,
                abstract=abstract,
                authors=authors,
                journal=self.journal_type,
                url=url,
                doi=doi,
                publication_date=pub_date
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
            self.logger.error(f"Science extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                extraction_time=extraction_time
            )
    
    def _try_access_methods(self, url: str):
        """Try multiple access methods for Science.org"""
        methods = [
            self._try_direct_access,
            self._try_alternative_headers,
            self._try_with_delay
        ]
        
        for method in methods:
            try:
                return method(url)
            except Exception as e:
                self.logger.debug(f"Access method failed: {e}")
                continue
        
        return None
    
    def _try_direct_access(self, url: str):
        """Try direct access"""
        return self.make_request(url)
    
    def _try_alternative_headers(self, url: str):
        """Try with Firefox headers"""
        original_headers = self.session.headers.copy()
        try:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            })
            return self.make_request(url)
        finally:
            self.session.headers = original_headers
    
    def _try_with_delay(self, url: str):
        """Try with longer delay"""
        time.sleep(3)
        return self.make_request(url)
    
    def _extract_title(self, soup) -> str:
        """Extract title from Science.org paper"""
        # Try multiple selectors
        selectors = [
            'h1.highwire-cite-title',
            'h1.article-title',
            'meta[name="citation_title"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem:
                    return elem.get('content', '')
            else:
                elem = soup.select_one(selector)
                if elem:
                    return self.clean_text(elem.get_text())
        
        return ""
    
    def _extract_abstract(self, soup) -> str:
        """Extract abstract from Science.org paper"""
        selectors = [
            'div.section.abstract p',
            'div.abstract-content p',
            'section[data-behavior="abstract"] p',
            'div.highwire-markup p'
        ]
        
        for selector in selectors:
            paragraphs = soup.select(selector)
            if paragraphs:
                return ' '.join(self.clean_text(p.get_text()) for p in paragraphs)
        
        return ""
    
    def _extract_authors_with_affiliations(self, soup) -> List[Author]:
        """Extract authors with detailed affiliation mapping"""
        authors = []
        
        try:
            # Find the core authors section
            authors_section = soup.find('section', class_='core-authors') or \
                            soup.find('div', class_='authors')
            
            if not authors_section:
                return authors
            
            # Extract authors using property-based approach
            author_divs = authors_section.find_all('div', {'property': 'author'})
            
            for i, author_div in enumerate(author_divs):
                author_data = self._parse_author_div(author_div, i)
                if author_data:
                    authors.append(author_data)
            
            # If no property-based authors found, try alternative approach
            if not authors:
                authors = self._extract_authors_alternative(authors_section)
        
        except Exception as e:
            self.logger.error(f"Error extracting Science.org authors: {e}")
        
        return authors
    
    def _parse_author_div(self, author_div, index: int) -> Optional[Author]:
        """Parse individual author div"""
        try:
            # Extract name
            name_elem = author_div.find('span', {'property': 'name'}) or \
                       author_div.find('a', {'property': 'url'})
            
            if not name_elem:
                return None
            
            name = self.clean_text(name_elem.get_text())
            
            # Extract ORCID
            orcid = None
            orcid_link = author_div.find('a', href=re.compile(r'orcid\.org'))
            if orcid_link:
                orcid_url = orcid_link.get('href', '')
                orcid_match = re.search(r'(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', orcid_url)
                if orcid_match:
                    orcid = orcid_match.group(1)
            
            # Extract email
            email = None
            email_elem = author_div.find('a', href=re.compile(r'mailto:'))
            if email_elem:
                email_href = email_elem.get('href', '')
                if email_href.startswith('mailto:'):
                    email = email_href[7:]  # Remove 'mailto:'
            
            # Extract affiliations
            affiliations = []
            affil_elems = author_div.find_all('span', {'property': 'affiliation'})
            for affil_elem in affil_elems:
                affil_text = self.clean_text(affil_elem.get_text())
                if affil_text:
                    affiliations.append(affil_text)
            
            # Determine roles
            roles = []
            if index == 0:
                roles.append(AuthorRole.FIRST)
            
            if email:  # Corresponding author typically has email
                roles.append(AuthorRole.CORRESPONDING)
            
            if not roles:
                roles.append(AuthorRole.REGULAR)
            
            return Author(
                name=name,
                email=email,
                orcid=orcid,
                affiliations=affiliations,
                roles=roles
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing author div: {e}")
            return None
    
    def _extract_authors_alternative(self, authors_section) -> List[Author]:
        """Alternative author extraction method"""
        authors = []
        
        try:
            # Look for author links
            author_links = authors_section.find_all('a', href=re.compile(r'/author/'))
            
            for i, link in enumerate(author_links):
                name = self.clean_text(link.get_text())
                if not name:
                    continue
                
                roles = []
                if i == 0:
                    roles.append(AuthorRole.FIRST)
                else:
                    roles.append(AuthorRole.REGULAR)
                
                author = Author(
                    name=name,
                    roles=roles
                )
                
                authors.append(author)
        
        except Exception as e:
            self.logger.error(f"Error in alternative author extraction: {e}")
        
        return authors
    
    def _extract_doi(self, soup) -> Optional[str]:
        """Extract DOI from Science.org paper"""
        # Try meta tag
        doi_meta = soup.find('meta', {'name': 'citation_doi'})
        if doi_meta:
            return doi_meta.get('content', '')
        
        # Extract from URL or page text
        page_text = soup.get_text()
        return self.extract_doi_from_text(page_text)
    
    def _extract_publication_date(self, soup) -> Optional[str]:
        """Extract publication date from Science.org paper"""
        # Try meta tag
        date_meta = soup.find('meta', {'name': 'citation_publication_date'})
        if date_meta:
            return date_meta.get('content', '')
        
        # Try to find date in page text
        date_patterns = [
            r'Published:?\s+(\d{1,2}\s+\w+\s+\d{4})',
            r'(\d{1,2}\s+\w+\s+\d{4})'
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                return match.group(1)
        
        return None