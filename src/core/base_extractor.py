"""
Base extractor - abstract interface for all journal extractors
Clean abstraction following the "good taste" principle
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urlparse

from ..models import Paper, ExtractionResult, JournalType


class BaseExtractor(ABC):
    """
    Abstract base class for journal extractors
    
    Design principle: Clean interface, no special cases
    Each extractor implements the same contract
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with reasonable defaults"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        })
    
    def __del__(self):
        """Clean up session resources"""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass
    
    # =================== Abstract Interface ===================
    
    @property
    @abstractmethod
    def journal_type(self) -> JournalType:
        """Return the journal type this extractor handles"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL for this journal"""
        pass
    
    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """Check if this extractor can handle the given URL"""
        pass
    
    @abstractmethod
    def search_paper(self, title: str) -> Optional[str]:
        """Search for a paper by title and return URL"""
        pass
    
    @abstractmethod
    def extract_paper_info(self, url: str) -> ExtractionResult:
        """Extract paper information from URL"""
        pass
    
    # =================== Common Implementation ===================
    
    def make_request(self, url: str, timeout: int = 15) -> BeautifulSoup:
        """
        Make HTTP request with proper error handling
        Common implementation - no special cases needed
        """
        try:
            time.sleep(1)  # Be respectful
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            raise
    
    def extract_from_input(self, input_text: str) -> ExtractionResult:
        """
        Universal entry point - handles both URLs and titles
        This is the public interface
        """
        input_text = input_text.strip()
        
        # Determine if input is URL or title
        if input_text.startswith('http') and self.can_handle_url(input_text):
            return self.extract_paper_info(input_text)
        else:
            # Search by title
            paper_url = self.search_paper(input_text)
            if paper_url:
                return self.extract_paper_info(paper_url)
            else:
                return ExtractionResult(
                    success=False,
                    error=f"Could not find paper: {input_text}"
                )
    
    def validate_extraction(self, result: ExtractionResult) -> bool:
        """Validate extraction result - basic sanity checks"""
        if not result.success or not result.paper:
            return False
        
        paper = result.paper
        
        # Basic validation - title and authors must exist
        if not paper.title or not paper.authors:
            return False
        
        # Author validation
        for author in paper.authors:
            if not author.name:
                return False
        
        return True
    
    # =================== Utility Methods ===================
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text - remove extra whitespace"""
        if not text:
            return ""
        return " ".join(text.split())
    
    def extract_doi_from_text(self, text: str) -> Optional[str]:
        """Extract DOI from text using common patterns"""
        import re
        
        patterns = [
            r'10\.\d{4,9}/[-._;()/:\w\[\]]+',
            r'doi:\s*10\.\d{4,9}/[-._;()/:\w\[\]]+',
            r'DOI:\s*10\.\d{4,9}/[-._;()/:\w\[\]]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                doi = match.group(0)
                # Clean up DOI
                if doi.lower().startswith('doi:'):
                    doi = doi[4:].strip()
                return doi
        
        return None
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower()
        except:
            return ""