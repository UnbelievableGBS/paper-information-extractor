"""
Paper data structure - the ONE way to represent paper information.
No special cases. No bullshit.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json


@dataclass
class Author:
    """Single author representation"""
    name: str
    affiliations: List[str] = field(default_factory=list)
    role: Optional[str] = None  # "First Author", "Corresponding Author", etc.
    is_corresponding: bool = False
    orcid: Optional[str] = None
    email: Optional[str] = None
    marks: List[str] = field(default_factory=list)  # †, *, etc.


@dataclass
class Paper:
    """THE paper data structure. Everything goes through this."""
    title: str
    url: str
    authors: List[Author] = field(default_factory=list)
    abstract: Optional[str] = None
    publication_date: Optional[str] = None
    contributions: Optional[str] = None
    countries: List[str] = field(default_factory=list)
    notes: Dict[str, str] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON - the format everyone expects"""
        data = {
            "title": self.title,
            "url": self.url,
            "authors": [
                {
                    "name": author.name,
                    "affiliations": author.affiliations,
                    "role": author.role,
                    "is_corresponding": author.is_corresponding,
                    "orcid": author.orcid,
                    "email": author.email,
                    "marks": author.marks
                } for author in self.authors
            ],
            "abstract": self.abstract,
            "publication_date": self.publication_date,
            "contributions": self.contributions,
            "countries": self.countries,
            "notes": self.notes
        }
        return json.dumps(data, indent=4, ensure_ascii=False)
    
    def get_corresponding_authors(self) -> List[Author]:
        """Get all corresponding authors"""
        return [a for a in self.authors if a.is_corresponding]
    
    def get_first_author(self) -> Optional[Author]:
        """Get first author (if any)"""
        return self.authors[0] if self.authors else None