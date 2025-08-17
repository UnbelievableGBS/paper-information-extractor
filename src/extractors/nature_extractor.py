"""
Nature journal extractor - clean implementation
No special cases, just straightforward extraction logic
"""

import re
from typing import Optional, List
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
        """Extract authors from Nature paper with role detection"""
        authors = []
        
        try:
            # Find author list
            author_list = soup.find('ul', class_='c-author-list') or soup.find('div', class_='c-author-list')
            if not author_list:
                return authors
            
            # Get author elements
            author_elements = author_list.find_all('li') or author_list.find_all('span', class_='author')
            
            # Get affiliations mapping
            affiliations_map = self._extract_affiliations_mapping(soup)
            
            # Detect co-first authors from footnotes
            co_first_symbols = self._detect_co_first_authors(soup)
            
            for i, author_elem in enumerate(author_elements):
                author_name = self.clean_text(author_elem.get_text())
                
                # Clean author name (remove superscripts)
                clean_name = re.sub(r'[0-9\*\†\‡\§\¶\#]+', '', author_name).strip()
                if not clean_name:
                    continue
                
                # Determine roles
                roles = []
                if i == 0:  # First author
                    roles.append(AuthorRole.FIRST)
                
                # Check for co-first author indicators
                if any(symbol in author_name for symbol in co_first_symbols):
                    if AuthorRole.FIRST not in roles:
                        roles.append(AuthorRole.CO_FIRST)
                
                # Check for corresponding author (usually indicated by email or special marker)
                if self._is_corresponding_author(author_elem, soup):
                    roles.append(AuthorRole.CORRESPONDING)
                
                if not roles:
                    roles.append(AuthorRole.REGULAR)
                
                # Get affiliations for this author
                author_affiliations = self._get_author_affiliations(author_elem, affiliations_map)
                
                author = Author(
                    name=clean_name,
                    affiliations=author_affiliations,
                    roles=roles
                )
                
                authors.append(author)
        
        except Exception as e:
            self.logger.error(f"Error extracting authors: {e}")
        
        return authors
    
    def _extract_affiliations_mapping(self, soup) -> dict:
        """Extract affiliations mapping from Nature paper"""
        affiliations = {}
        
        # Look for affiliations section
        affiliations_section = soup.find('section', {'data-title': 'Author information'}) or \
                             soup.find('div', class_='affiliations')
        
        if affiliations_section:
            affil_items = affiliations_section.find_all(['li', 'p'])
            for item in affil_items:
                text = self.clean_text(item.get_text())
                if text:
                    # Extract affiliation number/marker and text
                    match = re.match(r'^(\d+)\s*(.+)', text)
                    if match:
                        number, affiliation = match.groups()
                        affiliations[number] = affiliation
        
        return affiliations
    
    def _detect_co_first_authors(self, soup) -> List[str]:
        """Detect co-first author symbols from footnotes"""
        co_first_symbols = []
        
        # Look for footnotes mentioning equal contribution
        footnotes = soup.find_all(['p', 'div'], text=re.compile(r'contributed equally|equal contribution', re.I))
        
        for footnote in footnotes:
            text = footnote.get_text()
            # Extract symbols (usually superscript numbers or letters)
            symbols = re.findall(r'[0-9\*\†\‡\§\¶\#]', text)
            co_first_symbols.extend(symbols)
        
        return co_first_symbols
    
    def _is_corresponding_author(self, author_elem, soup) -> bool:
        """Check if author is corresponding author"""
        # Look for email in author element or nearby
        author_text = author_elem.get_text()
        
        # Check for email patterns
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', author_text):
            return True
        
        # Check for corresponding author indicators
        if re.search(r'corresponding|contact|email', author_text, re.I):
            return True
        
        return False
    
    def _get_author_affiliations(self, author_elem, affiliations_map: dict) -> List[str]:
        """Get affiliations for specific author"""
        affiliations = []
        
        # Extract affiliation numbers from author element
        author_text = author_elem.get_text()
        affil_numbers = re.findall(r'\d+', author_text)
        
        for number in affil_numbers:
            if number in affiliations_map:
                affiliations.append(affiliations_map[number])
        
        return affiliations
    
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