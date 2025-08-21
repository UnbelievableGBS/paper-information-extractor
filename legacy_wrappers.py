"""
Compatibility wrappers for the old functions.
Keep existing code working while using the new clean architecture.
"Never break userspace" - this is how we do it.
"""

from paper_extractor import extract_paper as unified_extract
import json


def parse_nature_authors(url: str):
    """Legacy Nature extractor wrapper - maintains old interface"""
    try:
        result_json = unified_extract(url)
        result_dict = json.loads(result_json)
        
        # Transform to old format for backward compatibility
        return {
            "title": result_dict["title"],
            "url": result_dict["url"], 
            "authors": result_dict["authors"],
            "countries": result_dict["countries"],
            "publication_date": result_dict["publication_date"],
            "abstract": result_dict["abstract"],
            "contributions": result_dict["contributions"]
        }
    except Exception as e:
        print(f"Error processing Nature paper: {e}")
        return {
            "title": "Unknown Title",
            "url": url,
            "authors": [],
            "countries": [],
            "publication_date": None,
            "abstract": None,
            "contributions": None
        }


def parse_science_authors(url: str):
    """Legacy Science extractor wrapper - maintains old interface"""
    try:
        result_json = unified_extract(url)
        result_dict = json.loads(result_json)
        
        # Transform to old format
        return {
            "authors": result_dict["authors"],
            "notes": result_dict["notes"],
            "abstract": result_dict["abstract"],
            "publication_date": result_dict["publication_date"],
            "title": result_dict["title"],
            "url": result_dict["url"]
        }
    except Exception as e:
        print(f"Error processing Science paper: {e}")
        return {
            "authors": [],
            "notes": {},
            "abstract": None,
            "publication_date": None,
            "title": "Unknown Title",
            "url": url
        }


def scrape_aps_authors(url: str):
    """Legacy APS extractor wrapper - maintains old interface"""
    try:
        result_json = unified_extract(url)
        result_dict = json.loads(result_json)
        
        # Return JSON string like the old function did
        return json.dumps({
            'authors': result_dict["authors"],
            'publication_date': result_dict["publication_date"],
            'abstract': result_dict["abstract"],
            'title': result_dict["title"],
            'url': result_dict["url"]
        }, indent=4)
    except Exception as e:
        print(f"Error processing APS paper: {e}")
        return json.dumps({
            'authors': [],
            'publication_date': None,
            'abstract': None,
            'title': "Unknown Title",
            'url': url
        }, indent=4)


# Direct function aliases for drop-in replacement
chatgpt_nature_extractor_parse = parse_nature_authors
chatgpt_science_extractor_parse = parse_science_authors  
deepseek_aps_extractor_scrape = scrape_aps_authors