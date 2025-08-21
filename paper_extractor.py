"""
The ONE paper extractor. Factory pattern without the enterprise bullshit.
"""

from urllib.parse import urlparse
from typing import Optional
from base_extractor import BaseExtractor, JOURNAL_CONFIGS
from paper_model import Paper, Author
from bs4 import BeautifulSoup
import re


class UnifiedPaperExtractor(BaseExtractor):
    """The extractor that handles all journals. No special cases."""
    
    def __init__(self):
        super().__init__()
    
    def _detect_journal(self, url: str) -> str:
        """Detect journal type from URL. Simple."""
        domain = urlparse(url).netloc.lower()
        
        if 'nature.com' in domain:
            return 'nature'
        elif 'science.org' in domain:
            return 'science'
        elif 'aps.org' in domain:
            return 'aps'
        else:
            raise ValueError(f"Unsupported journal domain: {domain}")
    
    def _extract_nature_authors(self, soup: BeautifulSoup) -> tuple:
        """Nature-specific author extraction"""
        authors = []
        all_affiliations = []
        
        # Build affiliation map
        aff_map = {}
        author_aff_map = {}
        
        aff_list = soup.select("ol.c-article-author-affiliation__list > li")
        for li in aff_list:
            aff_id = li.get("id")
            address = li.select_one(".c-article-author-affiliation__address")
            authors_list = li.select_one(".c-article-author-affiliation__authors-list")
            
            if address and authors_list:
                complete_address = address.get_text(strip=True)
                all_affiliations.append(complete_address)
                aff_map[aff_id] = complete_address
                
                # Map authors to affiliations
                authors_text = authors_list.get_text(strip=True)
                for author_part in re.split(r',\s*|\s*&\s*', authors_text):
                    author_name = author_part.strip()
                    if author_name:
                        if author_name not in author_aff_map:
                            author_aff_map[author_name] = []
                        author_aff_map[author_name].append(complete_address)
        
        # Get corresponding authors
        corresponding_authors = set()
        corr_auths = soup.select("#corresponding-author-list a")
        for a in corr_auths:
            corresponding_authors.add(a.get_text(strip=True))
        
        # Extract authors with roles
        authors_list = soup.select("ol.c-article-authors-search > li")
        for idx, li in enumerate(authors_list):
            name = li.select_one(".js-search-name").get_text(strip=True)
            author_affiliations = author_aff_map.get(name, [])
            
            # Determine role
            role = "Other Author"
            if idx == 0:
                role = "First Author"
            if name in corresponding_authors:
                if idx == 0:
                    role = "First/Corresponding Author"
                else:
                    role = "Corresponding Author"
            
            authors.append(Author(
                name=name,
                affiliations=author_affiliations,
                role=role,
                is_corresponding=name in corresponding_authors
            ))
        
        return authors, all_affiliations
    
    def _extract_science_authors(self, soup: BeautifulSoup) -> tuple:
        """Science-specific author extraction"""
        authors = []
        all_affiliations = []
        
        author_divs = soup.select(".core-authors .core-lnk")
        
        for author_div in author_divs:
            author_info = {}
            
            # Author name and marks
            heading = author_div.find("div", class_="heading")
            if heading:
                given = heading.find("span", {"property": "givenName"})
                family = heading.find("span", {"property": "familyName"})
                name = f"{given.get_text(' ', strip=True)} {family.get_text(' ', strip=True)}" if given and family else None
                
                if name:
                    marks = [sup.get_text(strip=True) for sup in heading.find_all("sup")]
                    
                    # Determine if corresponding author
                    is_corresponding = "*" in marks
                    
                    # Get affiliations
                    content = author_div.find("div", class_="content")
                    affiliations = []
                    if content:
                        affiliations = [aff.get_text(" ", strip=True) for aff in content.select(".affiliations [property='name']")]
                        all_affiliations.extend(affiliations)
                    
                    authors.append(Author(
                        name=name,
                        affiliations=affiliations,
                        marks=marks,
                        is_corresponding=is_corresponding,
                        role="Corresponding Author" if is_corresponding else "Author"
                    ))
        
        return authors, all_affiliations
    
    def _extract_aps_authors(self, soup: BeautifulSoup) -> tuple:
        """APS-specific author extraction"""
        authors = []
        all_affiliations = []
        
        authors_wrapper = soup.find('div', class_='authors-wrapper')
        if not authors_wrapper:
            return authors, all_affiliations
        
        # Extract affiliation map
        affil_dict = {}
        role_dict = {}
        
        details_section = authors_wrapper.find('details')
        if details_section:
            # Affiliations
            affil_list = details_section.find('ul', class_='no-bullet')
            if affil_list:
                for item in affil_list.find_all('li'):
                    sup = item.find('sup')
                    if sup:
                        num = sup.text.strip()
                        sup.decompose()
                        affil_text = item.get_text(strip=True)
                        affil_dict[num] = affil_text
                        all_affiliations.append(affil_text)
            
            # Roles
            contrib_notes = details_section.find('ul', class_='contrib-notes')
            if contrib_notes:
                for note in contrib_notes.find_all('li'):
                    sup = note.find('sup')
                    if sup:
                        symbol = sup.text.strip()
                        sup.decompose()
                        note_text = note.get_text(strip=True)
                        role_dict[symbol] = note_text
        
        # Process authors from the main line
        authors_line = authors_wrapper.find('p')
        if authors_line:
            current_author = {'name': '', 'affiliations': [], 'roles': []}
            
            for element in authors_line.children:
                if isinstance(element, str) and element.strip() == '':
                    continue
                    
                if element.name == 'a':
                    if '/search/field/author/' in element.get('href', ''):
                        # Save previous author
                        if current_author['name']:
                            authors.append(Author(
                                name=current_author['name'],
                                affiliations=current_author['affiliations'],
                                role=', '.join(current_author['roles']) if current_author['roles'] else "Author"
                            ))
                        
                        # Start new author
                        current_author = {
                            'name': element.text.strip(),
                            'affiliations': [],
                            'roles': []
                        }
                        
                elif element.name == 'sup':
                    # Handle markers
                    marks = [m.strip() for m in element.text.split(',')]
                    for mark in marks:
                        if mark.isdigit() and affil_dict.get(mark):
                            current_author['affiliations'].append(affil_dict[mark])
                        elif role_dict.get(mark):
                            current_author['roles'].append(role_dict[mark])
                
                elif isinstance(element, str) and 'and' in element.lower():
                    if current_author['name']:
                        authors.append(Author(
                            name=current_author['name'],
                            affiliations=current_author['affiliations'],
                            role=', '.join(current_author['roles']) if current_author['roles'] else "Author"
                        ))
            
            # Add last author
            if current_author['name']:
                authors.append(Author(
                    name=current_author['name'],
                    affiliations=current_author['affiliations'],
                    role=', '.join(current_author['roles']) if current_author['roles'] else "Author"
                ))
        
        return authors, all_affiliations
    
    def _extract_contributions(self, soup: BeautifulSoup, journal: str) -> Optional[str]:
        """Extract contributions section"""
        if journal == 'nature':
            contrib = soup.select_one('#contributions + p')
            if contrib:
                return contrib.get_text(" ", strip=True)
        return None
    
    def extract_paper(self, url: str) -> Paper:
        """Extract paper from any supported journal"""
        journal = self._detect_journal(url)
        config = JOURNAL_CONFIGS[journal]
        
        soup = self._fetch_html(url)
        
        # Extract basic info using selectors
        title = self._extract_by_selectors(soup, config.title_selectors) or "Unknown Title"
        abstract = self._extract_by_selectors(soup, config.abstract_selectors)
        
        # Handle date extraction (journal-specific logic)
        pub_date = None
        if journal == 'aps':
            pub_wrapper = soup.find('div', class_='pub-info-wrapper')
            if pub_wrapper:
                pub_strong = pub_wrapper.find('strong')
                if pub_strong and 'Published' in pub_strong.get_text():
                    date_match = re.search(r'Published\\s+(.+)', pub_strong.get_text(strip=True))
                    if date_match:
                        pub_date = date_match.group(1).strip()
        else:
            pub_date = self._extract_by_selectors(soup, config.date_selectors)
        
        # Extract authors (journal-specific)
        if journal == 'nature':
            authors, all_affiliations = self._extract_nature_authors(soup)
        elif journal == 'science':
            authors, all_affiliations = self._extract_science_authors(soup)
        elif journal == 'aps':
            authors, all_affiliations = self._extract_aps_authors(soup)
        else:
            authors, all_affiliations = [], []
        
        # Extract countries
        countries = self._extract_countries_from_affiliations(all_affiliations)
        
        # Extract contributions
        contributions = self._extract_contributions(soup, journal)
        
        return Paper(
            title=title,
            url=url,
            authors=authors,
            abstract=abstract,
            publication_date=pub_date,
            contributions=contributions,
            countries=countries
        )


def extract_paper(url: str) -> str:
    """Main function - extract any paper and return JSON"""
    extractor = UnifiedPaperExtractor()
    paper = extractor.extract_paper(url)
    return paper.to_json()


# Factory function for easy use
def get_extractor() -> UnifiedPaperExtractor:
    """Get the extractor instance"""
    return UnifiedPaperExtractor()