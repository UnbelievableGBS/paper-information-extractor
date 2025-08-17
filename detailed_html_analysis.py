#!/usr/bin/env python3
"""
Detailed HTML Content Analysis - examining what we actually receive
"""

from science_paper_extractor import SciencePaperExtractor
from bs4 import BeautifulSoup
import re
import json

def detailed_content_analysis():
    """Analyze the actual HTML content we receive"""
    extractor = SciencePaperExtractor()
    test_url = "https://www.science.org/doi/10.1126/scitranslmed.adn2601"
    
    print(f"🔍 DETAILED CONTENT ANALYSIS")
    print(f"📄 URL: {test_url}")
    print("=" * 80)
    
    # Get the soup object
    try:
        soup = extractor._try_direct_access(test_url)
        if not soup:
            print("❌ Could not access the page")
            return
    except Exception as e:
        print(f"❌ Error accessing page: {e}")
        return
    
    print("✅ Successfully accessed page")
    
    # 1. Show the raw HTML structure we actually got
    print(f"\n📄 RAW HTML STRUCTURE OVERVIEW")
    print("-" * 40)
    
    html_content = str(soup)
    print(f"Total HTML length: {len(html_content)} characters")
    
    # Show first 2000 characters
    print(f"\nFirst 2000 characters of HTML:")
    print("-" * 30)
    print(html_content[:2000])
    print("..." if len(html_content) > 2000 else "")
    
    # 2. Analyze the body content
    body = soup.find('body')
    if body:
        print(f"\n🏗️ BODY CONTENT ANALYSIS")
        print("-" * 25)
        
        body_text = body.get_text().strip()
        print(f"Body text length: {len(body_text)} characters")
        
        if body_text:
            print(f"\nBody text content (first 1000 chars):")
            print("-" * 30)
            print(body_text[:1000])
            print("..." if len(body_text) > 1000 else "")
        else:
            print("❌ Body has no visible text content")
    
    # 3. Look for JavaScript content
    print(f"\n🔧 JAVASCRIPT ANALYSIS")
    print("-" * 20)
    
    script_tags = soup.find_all('script')
    print(f"Found {len(script_tags)} script tags")
    
    for i, script in enumerate(script_tags):
        script_type = script.get('type', 'text/javascript')
        src = script.get('src', '')
        content = script.get_text().strip()
        
        print(f"\nScript {i+1}:")
        print(f"  Type: {script_type}")
        print(f"  Src: {src if src else 'Inline script'}")
        
        if content:
            print(f"  Content length: {len(content)} characters")
            
            # Look for specific patterns in script content
            if 'author' in content.lower():
                print("  ✓ Contains 'author' keyword")
            if 'orcid' in content.lower():
                print("  ✓ Contains 'orcid' keyword")
            if 'email' in content.lower():
                print("  ✓ Contains 'email' keyword")
            if 'affiliation' in content.lower():
                print("  ✓ Contains 'affiliation' keyword")
            
            # Show first 500 characters of inline scripts
            if not src and len(content) > 100:
                print(f"  Content preview: {content[:500]}...")
        else:
            print("  No inline content")
    
    # 4. Look for data attributes that might contain JSON
    print(f"\n📊 DATA ATTRIBUTES ANALYSIS")
    print("-" * 30)
    
    elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
    print(f"Found {len(elements_with_data)} elements with data- attributes")
    
    for i, elem in enumerate(elements_with_data[:10]):  # First 10
        data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
        print(f"\nElement {i+1}: <{elem.name}>")
        for attr, value in data_attrs.items():
            value_preview = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
            print(f"  {attr}: {value_preview}")
    
    # 5. Look for JSON-LD or other structured data
    print(f"\n📋 STRUCTURED DATA ANALYSIS")
    print("-" * 30)
    
    # JSON-LD scripts
    json_scripts = soup.find_all('script', type='application/ld+json')
    print(f"Found {len(json_scripts)} JSON-LD scripts")
    
    for i, script in enumerate(json_scripts):
        content = script.get_text().strip()
        print(f"\nJSON-LD {i+1}:")
        print(f"  Length: {len(content)} characters")
        try:
            data = json.loads(content)
            print(f"  Valid JSON: ✓")
            print(f"  Type: {data.get('@type', 'Unknown')}")
            if 'author' in data:
                print(f"  Contains author data: ✓")
            if 'name' in data:
                print(f"  Name: {data.get('name', '')[:100]}...")
        except:
            print(f"  Valid JSON: ❌")
        
        print(f"  Content: {content[:300]}...")
    
    # 6. Look for meta tags with useful information
    print(f"\n🏷️ META TAGS ANALYSIS")
    print("-" * 20)
    
    meta_tags = soup.find_all('meta')
    relevant_metas = []
    
    for meta in meta_tags:
        name = meta.get('name', meta.get('property', meta.get('itemprop', '')))
        content = meta.get('content', '')
        
        if any(keyword in name.lower() for keyword in ['author', 'title', 'description', 'citation', 'doi']):
            relevant_metas.append((name, content))
    
    print(f"Found {len(relevant_metas)} relevant meta tags:")
    for name, content in relevant_metas[:15]:  # First 15
        content_preview = content[:150] + "..." if len(content) > 150 else content
        print(f"  {name}: {content_preview}")
    
    # 7. Look for any hidden content or text
    print(f"\n👁️ HIDDEN CONTENT ANALYSIS")
    print("-" * 25)
    
    # Check for elements with display:none or visibility:hidden
    hidden_patterns = [
        '[style*="display:none"]',
        '[style*="display: none"]',
        '[style*="visibility:hidden"]',
        '[style*="visibility: hidden"]',
        '.hidden',
        '.invisible'
    ]
    
    for pattern in hidden_patterns:
        elements = soup.select(pattern)
        if elements:
            print(f"Found {len(elements)} elements matching {pattern}")
            for i, elem in enumerate(elements[:3]):
                text = elem.get_text().strip()[:200]
                if text:
                    print(f"  Hidden element {i+1} text: {text}...")
    
    # 8. Check for any server-side rendered content that might have author info
    print(f"\n🔍 CONTENT SEARCH FOR AUTHOR KEYWORDS")
    print("-" * 40)
    
    full_html = str(soup)
    keywords = ['orcid', 'author', 'affiliation', 'email', 'mailto', '@', 'university', 'department']
    
    for keyword in keywords:
        matches = len(re.findall(keyword, full_html, re.IGNORECASE))
        if matches > 0:
            print(f"  '{keyword}': {matches} occurrences")
    
    # 9. Check for any iframe or embed content
    print(f"\n🖼️ EMBEDDED CONTENT ANALYSIS")
    print("-" * 30)
    
    iframes = soup.find_all('iframe')
    embeds = soup.find_all('embed')
    objects = soup.find_all('object')
    
    print(f"Found {len(iframes)} iframes, {len(embeds)} embeds, {len(objects)} objects")
    
    for i, iframe in enumerate(iframes[:5]):
        src = iframe.get('src', '')
        print(f"  Iframe {i+1}: {src}")
    
    # 10. Final assessment
    print(f"\n📈 FINAL ASSESSMENT")
    print("-" * 20)
    
    body_text_len = len(body.get_text().strip()) if body else 0
    script_count = len(script_tags)
    has_json_ld = len(json_scripts) > 0
    
    print(f"Body text length: {body_text_len}")
    print(f"Script tags: {script_count}")
    print(f"Has JSON-LD: {has_json_ld}")
    
    if body_text_len < 1000 and script_count > 5:
        print("\n🎯 CONCLUSION: This appears to be a JavaScript-heavy SPA (Single Page Application)")
        print("   The content is likely loaded dynamically after page load.")
        print("   Author information is probably fetched via AJAX/API calls.")
    elif has_json_ld:
        print("\n🎯 CONCLUSION: Content may be in JSON-LD structured data")
    else:
        print("\n🎯 CONCLUSION: Unable to determine content loading mechanism")

if __name__ == "__main__":
    detailed_content_analysis()