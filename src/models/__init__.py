"""
Models package - clean data structures
"""

from .paper import Paper, Author, AuthorRole, JournalType, ExtractionResult

__all__ = ['Paper', 'Author', 'AuthorRole', 'JournalType', 'ExtractionResult']