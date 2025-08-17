"""
Data models for paper information
Clean, simple data structures - good taste principle
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JournalType(Enum):
    """Supported journal types"""
    NATURE = "nature"
    SCIENCE = "science"
    APS = "aps"


class AuthorRole(Enum):
    """Author role types"""
    FIRST = "first"
    CO_FIRST = "co_first"
    CORRESPONDING = "corresponding"
    REGULAR = "regular"


@dataclass
class Author:
    """Author information model"""
    name: str
    email: Optional[str] = None
    orcid: Optional[str] = None
    affiliations: List[str] = None
    roles: List[AuthorRole] = None
    external_links: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.affiliations is None:
            self.affiliations = []
        if self.roles is None:
            self.roles = []
    
    @property
    def formatted_name(self) -> str:
        """Format name with role annotations for specific journals"""
        annotations = []
        if AuthorRole.CO_FIRST in self.roles:
            annotations.append("#")
        if AuthorRole.CORRESPONDING in self.roles:
            annotations.append("*")
        
        return f"{self.name}{''.join(annotations)}"
    
    @property
    def is_corresponding(self) -> bool:
        return AuthorRole.CORRESPONDING in self.roles
    
    @property
    def is_first_author(self) -> bool:
        return AuthorRole.FIRST in self.roles or AuthorRole.CO_FIRST in self.roles


@dataclass
class Paper:
    """Paper information model - the core data structure"""
    title: str
    abstract: str
    authors: List[Author]
    journal: JournalType
    url: str
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    contributions: Optional[str] = None
    extracted_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now()
    
    @property
    def author_count(self) -> int:
        return len(self.authors)
    
    @property
    def corresponding_authors(self) -> List[Author]:
        return [author for author in self.authors if author.is_corresponding]
    
    @property
    def first_authors(self) -> List[Author]:
        return [author for author in self.authors if author.is_first_author]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "title": self.title,
            "abstract": self.abstract,
            "authors": [
                {
                    "name": author.name,
                    "email": author.email,
                    "orcid": author.orcid,
                    "affiliations": author.affiliations,
                    "roles": [role.value for role in author.roles],
                    "formatted_name": author.formatted_name,
                    "external_links": author.external_links
                }
                for author in self.authors
            ],
            "journal": self.journal.value,
            "url": self.url,
            "doi": self.doi,
            "publication_date": self.publication_date,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "contributions": self.contributions,
            "extracted_at": self.extracted_at.isoformat() if self.extracted_at else None,
            "metadata": {
                "author_count": self.author_count,
                "corresponding_count": len(self.corresponding_authors),
                "first_author_count": len(self.first_authors)
            }
        }
    
    def get_formatted_authors_string(self, style: str = "default") -> str:
        """Get formatted authors string for different output styles"""
        if style == "nature":
            return self._format_nature_style()
        elif style == "aps":
            return self._format_aps_style()
        else:
            return ", ".join(author.formatted_name for author in self.authors)
    
    def _format_nature_style(self) -> str:
        """Nature journal author formatting"""
        lines = []
        for author in self.authors:
            affiliations_str = "; ".join(author.affiliations) if author.affiliations else ""
            if affiliations_str:
                lines.append(f"{author.formatted_name} ({affiliations_str})")
            else:
                lines.append(author.formatted_name)
        return "\n".join(lines)
    
    def _format_aps_style(self) -> str:
        """APS journal author formatting"""
        return ", ".join(author.formatted_name for author in self.authors)


@dataclass
class ExtractionResult:
    """Result of paper extraction operation"""
    success: bool
    paper: Optional[Paper] = None
    error: Optional[str] = None
    extraction_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        result = {
            "success": self.success,
            "extraction_time": self.extraction_time
        }
        
        if self.success and self.paper:
            result["data"] = self.paper.to_dict()
        else:
            result["error"] = self.error
            
        return result