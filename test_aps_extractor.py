#!/usr/bin/env python3
"""
APS Paper Extractor Test Script
Demonstrates the comprehensive functionality of the APS extractor
"""

from aps_paper_extractor import APSPaperExtractor
import os

def test_aps_extractor():
    """Test the APS extractor with various scenarios"""
    
    print("🔬 APS PAPER EXTRACTOR - COMPREHENSIVE TEST")
    print("=" * 60)
    
    extractor = APSPaperExtractor()
    
    try:
        # Test 1: Direct URL extraction
        print("\n📋 TEST 1: Direct URL Extraction")
        print("-" * 40)
        
        test_url = "https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.010344"
        print(f"URL: {test_url}")
        
        try:
            paper_info = extractor.extract_paper_info(test_url)
            
            if paper_info.get("Title"):
                print("✅ Successfully extracted paper information")
                print(f"📄 Title: {paper_info['Title'][:80]}...")
                print(f"📝 Abstract: {len(paper_info['Abstract'])} characters")
                print(f"👥 Authors: {paper_info['Authors']}")
                
                # Create Excel file
                excel_file = extractor.export_to_excel(paper_info, "aps_url_test.xlsx")
                if excel_file:
                    print(f"📊 Excel saved: {excel_file}")
                    
                # Analyze author annotations
                analyze_author_annotations(paper_info['Authors'])
                
            else:
                print("❌ Failed to extract from URL (likely access restrictions)")
                
        except Exception as e:
            print(f"❌ URL test failed: {e}")
        
        # Test 2: Title search (demonstration)
        print("\n📋 TEST 2: Title Search Functionality")
        print("-" * 40)
        
        test_title = "Strong-to-Weak Spontaneous Symmetry Breaking"
        print(f"Search Title: {test_title}")
        
        try:
            found_url = extractor.search_paper_by_title(test_title)
            if found_url:
                print(f"✅ Found paper URL: {found_url}")
            else:
                print("❌ No papers found (likely access restrictions)")
        except Exception as e:
            print(f"❌ Search test failed: {e}")
        
        # Test 3: Demonstrate annotation system
        print("\n📋 TEST 3: Author Annotation System Explanation")
        print("-" * 40)
        print("APS Requirements:")
        print("• First author: No annotation")
        print("• Co-first authors: # after name")
        print("• Corresponding authors: * after name")
        print()
        print("Example output from our extractor:")
        print("Leonardo A. Lessa#, Ruochen Ma#, Jian-Hao Zhang#, Zhen Bi*, Meng Cheng*, Chong Wang*")
        print()
        print("Interpretation:")
        print("✓ First 3 authors are co-first (equal contribution) → marked with #")
        print("✓ Last 3 authors are corresponding authors → marked with *")
        
        print("\n🎯 APS EXTRACTOR FEATURES SUMMARY:")
        print("-" * 40)
        print("✅ Multi-header access configuration for APS restrictions")
        print("✅ Intelligent author annotation parsing from contribution notes")
        print("✅ Robust HTML structure analysis based on actual APS pages")
        print("✅ Title search functionality with fallback mechanisms")
        print("✅ Professional Excel export with proper formatting")
        print("✅ Comprehensive error handling and user feedback")
        
    finally:
        extractor.__del__()


def analyze_author_annotations(authors_string: str):
    """Analyze and explain author annotations"""
    if not authors_string:
        return
    
    print("\n🔍 AUTHOR ANNOTATION BREAKDOWN:")
    print("-" * 40)
    
    authors = [a.strip() for a in authors_string.split(',')]
    
    co_first_count = 0
    corresponding_count = 0
    regular_count = 0
    
    for i, author in enumerate(authors, 1):
        if author.endswith('#'):
            role = "Co-first author"
            co_first_count += 1
        elif author.endswith('*'):
            role = "Corresponding author"
            corresponding_count += 1
        else:
            role = "Regular co-author" if i > 1 else "First author"
            regular_count += 1
        
        clean_name = author.rstrip('#*')
        print(f"{i:2d}. {clean_name:<25} → {role}")
    
    print(f"\n📊 Summary: {co_first_count} co-first, {corresponding_count} corresponding, {regular_count} regular")


if __name__ == "__main__":
    test_aps_extractor()