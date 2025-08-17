#!/usr/bin/env python3
"""
Test the enhanced Science.org paper extraction with complete paper information
"""

from science_paper_extractor import SciencePaperExtractor
import json

def test_enhanced_extraction():
    """Test the enhanced extraction functionality"""
    try:
        extractor = SciencePaperExtractor()
        
        # Test URL from user requirements
        test_url = "https://www.science.org/doi/10.1126/scitranslmed.adn2601"
        print(f"🔬 Testing Enhanced Extraction")
        print(f"📄 Paper URL: {test_url}")
        print("=" * 80)
        
        # Extract complete paper information
        paper_info = extractor.extract_paper_info(test_url)
        
        if not paper_info:
            print("❌ Failed to extract paper information")
            return None
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return None
    
    # Display complete paper information
    print("📝 COMPLETE PAPER INFORMATION:")
    print(f"Title: {paper_info.get('title', 'N/A')}")
    print(f"DOI: {paper_info.get('doi', 'N/A')}")
    print(f"Journal: {paper_info.get('journal', 'N/A')}")
    print(f"Abstract: {paper_info.get('abstract', 'N/A')[:200]}...")
    print(f"Total Authors: {len(paper_info.get('authors', []))}")
    
    print("\n👥 DETAILED AUTHOR INFORMATION:")
    print("=" * 80)
    
    authors = paper_info.get('authors', [])
    corresponding_count = 0
    
    for i, author in enumerate(authors, 1):
        print(f"\n🧑‍🔬 Author {i}:")
        # Show both regular and formatted names
        formatted_name = author.get('full_name_formatted', author.get('full_name', 'N/A'))
        print(f"  📛 Full Name: {formatted_name}")
        print(f"  🏷️  Given Name: {author.get('given_name', 'N/A')}")
        print(f"  🏷️  Family Name: {author.get('family_name', 'N/A')}")
        print(f"  🔗 ORCID: {author.get('orcid', 'N/A')}")
        
        if author.get('email'):
            print(f"  📧 Email: {author.get('email')}")
        
        if author.get('is_corresponding'):
            print(f"  ⭐ Corresponding Author: YES")
            corresponding_count += 1
        else:
            print(f"  ⭐ Corresponding Author: No")
            
        if author.get('affiliations'):
            print(f"  🏛️  Affiliations: {author.get('affiliations')}")
        
        if author.get('roles'):
            print(f"  👔 Roles: {author.get('roles')}")
            
        if author.get('profile_link'):
            print(f"  🔗 Profile: {author.get('profile_link')}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  • Total Authors: {len(authors)}")
    print(f"  • Corresponding Authors: {corresponding_count}")
    print(f"  • Authors with ORCID: {sum(1 for a in authors if a.get('orcid'))}")
    print(f"  • Authors with Affiliations: {sum(1 for a in authors if a.get('affiliations'))}")
    print(f"  • Authors with Roles: {sum(1 for a in authors if a.get('roles'))}")
    
    # Test Excel export
    print(f"\n📄 EXCEL EXPORT TEST:")
    try:
        filename = extractor.export_to_excel(authors, 'enhanced_extraction_test.xlsx')
        if filename:
            print(f"✅ Excel export successful: {filename}")
        else:
            print("❌ Excel export failed")
    except Exception as e:
        print(f"❌ Excel export error: {e}")
    
    return paper_info

if __name__ == "__main__":
    test_enhanced_extraction()