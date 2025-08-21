"""
Base extractor - the ONE way to extract papers.
All the HTTP/parsing bullshit goes here. Once.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
from typing import Dict, List, Optional, Any
from paper_model import Paper, Author


class BaseExtractor:
    """Base extractor that handles all the common crap"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        }
    
    def _fetch_html(self, url: str) -> BeautifulSoup:
        """Fetch HTML with retry logic. Anti-bot crap handled here."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))
                
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                    continue
                else:
                    raise
    
    def _clean_text(self, text: str) -> str:
        """Clean text - remove extra whitespace bullshit"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Try selectors until one works. Simple."""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return self._clean_text(elem.get_text())
        return None
    
    def _extract_countries_from_affiliations(self, affiliations: List[str]) -> List[str]:
        """Extract countries from affiliation strings"""
        countries = set()
        country_patterns = [
            (r',\s*([A-Z]{2,3})$', lambda m: m.group(1)),  # USA, UK, etc.
            (r',\s*([A-Z][a-z]+)$', lambda m: m.group(1)),  # China, Japan, etc.
            (r',\s*(United States)$', lambda m: 'USA'),
            (r',\s*(United Kingdom)$', lambda m: 'UK')
        ]
        
        for aff in affiliations:
            for pattern, extractor in country_patterns:
                match = re.search(pattern, aff)
                if match:
                    countries.add(extractor(match))
                    break
        
        return list(countries)
    
    def extract_paper(self, url: str) -> Paper:
        """Main extraction method. Subclasses override this."""
        raise NotImplementedError("Subclasses must implement this")


class JournalConfig:
    """Configuration for journal-specific selectors. No special cases."""
    
    def __init__(self, 
                 title_selectors: List[str],
                 abstract_selectors: List[str],
                 date_selectors: List[str],
                 author_container_selector: str,
                 affiliation_selectors: List[str]):
        self.title_selectors = title_selectors
        self.abstract_selectors = abstract_selectors  
        self.date_selectors = date_selectors
        self.author_container_selector = author_container_selector
        self.affiliation_selectors = affiliation_selectors


# Journal configurations - all the site-specific crap in one place
JOURNAL_CONFIGS = {
    'nature': JournalConfig(
        title_selectors=['h1.c-article-title'],
        abstract_selectors=['.c-article-section__content p'],
        date_selectors=['.c-article-info-details time'],
        author_container_selector='.c-article-author-affiliation',
        affiliation_selectors=['.c-article-author-affiliation__address']
    ),
    
    'science': JournalConfig(
        title_selectors=['h1.article-title', 'h1[property="headline"]', 'h1.core-title'],
        abstract_selectors=['section#abstract div[role="paragraph"]'],
        date_selectors=['div.core-date-published span[property="datePublished"]'],
        author_container_selector='.core-authors',
        affiliation_selectors=['.affiliations [property="name"]']
    ),
    
    'aps': JournalConfig(
        title_selectors=['h1.title', 'h1[data-behavior="title"]', 'h1.article-title'],
        abstract_selectors=['#abstract-section-content p'],
        date_selectors=['.pub-info-wrapper strong'],
        author_container_selector='.authors-wrapper',
        affiliation_selectors=['.no-bullet li']
    )
}