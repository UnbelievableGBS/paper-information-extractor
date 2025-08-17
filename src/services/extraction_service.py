"""
Unified extraction service - the main business logic layer
Clean service pattern with no special cases
"""

from typing import Optional, List, Dict, Type
import logging

from ..models import ExtractionResult, JournalType
from ..core import BaseExtractor
from ..extractors import NatureExtractor, ScienceExtractor, APSExtractor


class ExtractionService:
    """
    Main service for paper extraction
    
    Simple design: Factory pattern + Service layer
    No complex inheritance hierarchy - just clean composition
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._extractors: Dict[JournalType, BaseExtractor] = {}
        self._setup_extractors()
    
    def _setup_extractors(self):
        """Initialize all extractors - simple registration"""
        extractors = [
            NatureExtractor(),
            ScienceExtractor(),
            APSExtractor()
        ]
        
        for extractor in extractors:
            self._extractors[extractor.journal_type] = extractor
    
    def extract_paper(self, input_text: str, journal_hint: Optional[str] = None) -> ExtractionResult:
        """
        Main extraction method - unified interface
        
        Args:
            input_text: URL or paper title
            journal_hint: Optional journal type hint
            
        Returns:
            ExtractionResult with paper data or error
        """
        input_text = input_text.strip()
        
        # Try journal hint first if provided
        if journal_hint:
            extractor = self._get_extractor_by_hint(journal_hint)
            if extractor:
                self.logger.info(f"Using hinted extractor: {extractor.journal_type.value}")
                return extractor.extract_from_input(input_text)
        
        # Auto-detect from URL
        if input_text.startswith('http'):
            extractor = self._detect_extractor_from_url(input_text)
            if extractor:
                self.logger.info(f"Detected extractor from URL: {extractor.journal_type.value}")
                return extractor.extract_from_input(input_text)
            else:
                return ExtractionResult(
                    success=False,
                    error=f"Unsupported journal URL: {input_text}"
                )
        
        # Search across all journals for title
        return self._search_all_journals(input_text)
    
    def _get_extractor_by_hint(self, hint: str) -> Optional[BaseExtractor]:
        """Get extractor by journal hint"""
        hint_lower = hint.lower()
        
        for journal_type, extractor in self._extractors.items():
            if hint_lower in journal_type.value.lower():
                return extractor
        
        return None
    
    def _detect_extractor_from_url(self, url: str) -> Optional[BaseExtractor]:
        """Detect appropriate extractor from URL"""
        for extractor in self._extractors.values():
            if extractor.can_handle_url(url):
                return extractor
        
        return None
    
    def _search_all_journals(self, title: str) -> ExtractionResult:
        """Search title across all journals"""
        self.logger.info(f"Searching all journals for: {title}")
        
        errors = []
        
        # Try each extractor in priority order
        priority_order = [
            JournalType.NATURE,  # Usually most accessible
            JournalType.SCIENCE,
            JournalType.APS
        ]
        
        for journal_type in priority_order:
            extractor = self._extractors[journal_type]
            
            try:
                self.logger.info(f"Trying {journal_type.value} search...")
                result = extractor.extract_from_input(title)
                
                if result.success:
                    self.logger.info(f"Successfully found paper in {journal_type.value}")
                    return result
                else:
                    errors.append(f"{journal_type.value}: {result.error}")
            
            except Exception as e:
                error_msg = f"{journal_type.value}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        # All searches failed
        return ExtractionResult(
            success=False,
            error=f"Paper not found in any journal. Errors: {'; '.join(errors)}"
        )
    
    def get_supported_journals(self) -> List[str]:
        """Get list of supported journal types"""
        return [journal_type.value for journal_type in self._extractors.keys()]
    
    def get_extractor_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about available extractors"""
        info = {}
        
        for journal_type, extractor in self._extractors.items():
            info[journal_type.value] = {
                'name': journal_type.value.title(),
                'base_url': extractor.base_url,
                'class': extractor.__class__.__name__
            }
        
        return info
    
    def __del__(self):
        """Clean up extractors"""
        for extractor in self._extractors.values():
            try:
                extractor.__del__()
            except:
                pass