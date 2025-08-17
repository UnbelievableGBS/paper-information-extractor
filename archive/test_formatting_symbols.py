#!/usr/bin/env python3
"""
Test formatting symbols (#, *) in all output formats
"""

from science_paper_extractor import SciencePaperExtractor
import json

def test_formatting_symbols():
    """Test that formatting symbols appear correctly in all outputs"""
    extractor = SciencePaperExtractor()
    
    # Test URL
    test_url = "https://www.science.org/doi/10.1126/scitranslmed.adn2601"
    print(f"🔍 TESTING FORMATTING SYMBOLS")
    print(f"📄 URL: {test_url}")
    print("=" * 80)
    
    # Extract paper information
    paper_info = extractor.extract_paper_info(test_url)
    authors = paper_info.get('authors', [])
    
    if not authors:
        print("❌ No authors found")
        return
    
    print(f"✅ Found {len(authors)} authors")
    
    # Test 1: Console output formatting
    print(f"\n📺 TEST 1: CONSOLE OUTPUT FORMATTING")
    print("-" * 40)
    
    for i, author in enumerate(authors):
        formatted_name = author.get('full_name_formatted', author.get('full_name', ''))
        original_name = author.get('full_name', '')
        is_corresponding = author.get('is_corresponding', False)
        
        # Check for symbols
        has_first_symbol = '#' in formatted_name
        has_corresponding_symbol = '*' in formatted_name
        
        print(f"Author {i+1}:")
        print(f"  Original name: {original_name}")
        print(f"  Formatted name: {formatted_name}")
        print(f"  Is first author (index 0): {i == 0}")
        print(f"  Is corresponding: {is_corresponding}")
        print(f"  Has '#' symbol: {has_first_symbol}")
        print(f"  Has '*' symbol: {has_corresponding_symbol}")
        
        # Validation
        if i == 0 and not has_first_symbol:
            print(f"  ❌ ERROR: First author should have '#' symbol")
        elif i == 0 and has_first_symbol:
            print(f"  ✅ CORRECT: First author has '#' symbol")
        
        if is_corresponding and not has_corresponding_symbol:
            print(f"  ❌ ERROR: Corresponding author should have '*' symbol")
        elif is_corresponding and has_corresponding_symbol:
            print(f"  ✅ CORRECT: Corresponding author has '*' symbol")
        
        print()
    
    # Test 2: Excel export formatting
    print(f"\n📊 TEST 2: EXCEL EXPORT FORMATTING")
    print("-" * 35)
    
    excel_filename = 'test_formatting_symbols.xlsx'
    result_filename = extractor.export_to_excel(authors, excel_filename)
    
    if result_filename:
        print(f"✅ Excel file created: {result_filename}")
        
        # Verify that formatted names are in the Excel file
        # This is indirect verification - the names should include symbols
        first_author = authors[0] if authors else None
        if first_author:
            formatted_name = first_author.get('full_name_formatted', '')
            if '#' in formatted_name:
                print(f"✅ First author in Excel should have '#': {formatted_name}")
            else:
                print(f"❌ First author missing '#' symbol: {formatted_name}")
        
        corresponding_authors = [a for a in authors if a.get('is_corresponding')]
        for author in corresponding_authors:
            formatted_name = author.get('full_name_formatted', '')
            if '*' in formatted_name:
                print(f"✅ Corresponding author in Excel should have '*': {formatted_name}")
            else:
                print(f"❌ Corresponding author missing '*' symbol: {formatted_name}")
    else:
        print("❌ Excel export failed")
    
    # Test 3: JSON serialization (for web app)
    print(f"\n🌐 TEST 3: JSON SERIALIZATION (Web App)")
    print("-" * 40)
    
    try:
        # Convert to JSON to simulate web app data transfer
        json_data = json.dumps(authors, indent=2)
        parsed_data = json.loads(json_data)
        
        print("✅ JSON serialization successful")
        
        # Check that formatted names are preserved
        for i, author in enumerate(parsed_data):
            formatted_name = author.get('full_name_formatted', '')
            original_name = author.get('full_name', '')
            
            print(f"JSON Author {i+1}: {formatted_name}")
            
            if i == 0 and '#' not in formatted_name:
                print(f"  ❌ ERROR: First author JSON missing '#' symbol")
            if author.get('is_corresponding') and '*' not in formatted_name:
                print(f"  ❌ ERROR: Corresponding author JSON missing '*' symbol")
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
    
    # Test 4: Symbol validation
    print(f"\n✔️ TEST 4: SYMBOL VALIDATION SUMMARY")
    print("-" * 35)
    
    first_authors = [a for i, a in enumerate(authors) if i == 0]
    corresponding_authors = [a for a in authors if a.get('is_corresponding')]
    
    print(f"First authors: {len(first_authors)}")
    print(f"Corresponding authors: {len(corresponding_authors)}")
    
    # Count symbols
    first_with_hash = sum(1 for i, a in enumerate(authors) if i == 0 and '#' in a.get('full_name_formatted', ''))
    corresponding_with_star = sum(1 for a in authors if a.get('is_corresponding') and '*' in a.get('full_name_formatted', ''))
    
    print(f"First authors with '#': {first_with_hash}/{len(first_authors)}")
    print(f"Corresponding authors with '*': {corresponding_with_star}/{len(corresponding_authors)}")
    
    # Overall validation
    all_correct = (
        first_with_hash == len(first_authors) and 
        corresponding_with_star == len(corresponding_authors)
    )
    
    if all_correct:
        print(f"\n🎉 ALL TESTS PASSED: Formatting symbols are correctly applied!")
    else:
        print(f"\n❌ TESTS FAILED: Some formatting symbols are missing")
    
    return all_correct

if __name__ == "__main__":
    test_formatting_symbols()