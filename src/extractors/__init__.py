"""
Extractors package - journal-specific implementations
"""

from .nature_extractor import NatureExtractor
from .science_extractor import ScienceExtractor
from .aps_extractor import APSExtractor

__all__ = ['NatureExtractor', 'ScienceExtractor', 'APSExtractor']