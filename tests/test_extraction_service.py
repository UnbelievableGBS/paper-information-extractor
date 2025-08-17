"""
Test the extraction service - simple, focused tests
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src import ExtractionService, JournalType


class TestExtractionService:
    """Test extraction service functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service = ExtractionService()
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        assert self.service is not None
        
        # Check extractors are loaded
        supported = self.service.get_supported_journals()
        assert len(supported) == 3
        assert "nature" in supported
        assert "science" in supported
        assert "aps" in supported
    
    def test_get_extractor_info(self):
        """Test extractor info retrieval"""
        info = self.service.get_extractor_info()
        
        assert isinstance(info, dict)
        assert len(info) == 3
        
        for journal in ["nature", "science", "aps"]:
            assert journal in info
            assert "name" in info[journal]
            assert "base_url" in info[journal]
            assert "class" in info[journal]
    
    def test_url_detection(self):
        """Test URL detection for different journals"""
        test_urls = [
            ("https://www.nature.com/articles/s41467-025-61342-8", True),
            ("https://www.science.org/doi/10.1126/science.abc123", True),
            ("https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.010344", True),
            ("https://example.com/paper", False)
        ]
        
        for url, should_detect in test_urls:
            # Try to detect extractor
            extractor = self.service._detect_extractor_from_url(url)
            
            if should_detect:
                assert extractor is not None
                assert extractor.can_handle_url(url)
            else:
                assert extractor is None
    
    def test_journal_hint_parsing(self):
        """Test journal hint functionality"""
        hints = [
            ("nature", "nature"),
            ("Nature", "nature"),
            ("NATURE", "nature"),
            ("science", "science"),
            ("aps", "aps"),
            ("invalid", None)
        ]
        
        for hint, expected in hints:
            extractor = self.service._get_extractor_by_hint(hint)
            
            if expected:
                assert extractor is not None
                assert extractor.journal_type.value == expected
            else:
                assert extractor is None
    
    @pytest.mark.integration
    def test_extraction_with_mock_data(self):
        """Test extraction with mock data (integration test)"""
        # This would require mock data or actual network access
        # For now, just test the interface
        
        result = self.service.extract_paper("test title")
        
        # Should return a result object
        assert hasattr(result, 'success')
        assert hasattr(result, 'error') or hasattr(result, 'paper')
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self.service, '__del__'):
            self.service.__del__()