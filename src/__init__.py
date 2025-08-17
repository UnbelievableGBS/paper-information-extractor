"""
Paper Information Extractor - Main Package

Clean, layered architecture for academic paper extraction
Supports Nature, Science.org, and APS journals
"""

from .models import Paper, Author, AuthorRole, JournalType, ExtractionResult
from .services import ExtractionService, ExportService
from .utils import setup_logging

__version__ = "1.0.0"
__all__ = [
    'Paper', 'Author', 'AuthorRole', 'JournalType', 'ExtractionResult',
    'ExtractionService', 'ExportService', 'setup_logging'
]