#!/usr/bin/env python3
"""
Deep HTML Structure Analysis for Science.org Papers
Analyzes the HTML structure to understand how author information is organized
"""

from science_paper_extractor import SciencePaperExtractor
from bs4 import BeautifulSoup
import re

def analyze_html_structure():
    """Perform deep analysis of Science.org HTML structure"""
    extractor = SciencePaperExtractor()
    
    # Test URL
    test_url = "https://www.science.org/doi/10.1126/scitranslmed.adn2601"
    print(f"🔍 DEEP HTML ANALYSIS")
    print(f"📄 URL: {test_url}")
    print("=" * 80)
    
    # Try to access the page using our extraction methods
    access_methods = [
        ("Direct Access", extractor._try_direct_access),
        ("Alternative Headers", extractor._try_alternative_headers),
        ("With Delay", extractor._try_with_delay)
    ]
    
    soup = None
    successful_method = None
    
    for method_name, method in access_methods:
        try:
            print(f"🔄 Trying {method_name}...")
            soup = method(test_url)
            if soup:
                successful_method = method_name
                print(f"✅ Successfully accessed page using {method_name}")
                break
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
    
    if not soup:
        print("❌ Could not access the page with any method")
        return
    
    print(f"\n📊 SUCCESSFUL ACCESS METHOD: {successful_method}")
    print("=" * 80)
    
    # Start detailed HTML analysis
    print("\n🏗️ OVERALL PAGE STRUCTURE ANALYSIS")
    print("-" * 50)
    
    # 1. Root HTML structure
    print("1. ROOT HTML STRUCTURE:")
    html_tag = soup.find('html')
    if html_tag:
        print(f"   HTML tag attributes: {html_tag.attrs}")
    
    # 2. Head section analysis
    head = soup.find('head')
    if head:
        print(f"\n2. HEAD SECTION:")
        print(f"   Title: {soup.title.get_text() if soup.title else 'None'}")
        
        # Meta tags
        meta_tags = head.find_all('meta')
        print(f"   Meta tags count: {len(meta_tags)}")
        
        important_metas = ['description', 'keywords', 'author', 'citation_title', 'citation_author', 'citation_doi']
        for meta in meta_tags:
            name = meta.get('name', meta.get('property', ''))
            if any(imp in name.lower() for imp in important_metas):
                content = meta.get('content', '')[:100] + '...' if len(meta.get('content', '')) > 100 else meta.get('content', '')
                print(f"   {name}: {content}")
    
    # 3. Body structure
    body = soup.find('body')
    if body:
        print(f"\n3. BODY STRUCTURE:")
        print(f"   Body classes: {body.get('class', [])}")
        print(f"   Body ID: {body.get('id', 'None')}")
        
        # Direct children of body
        direct_children = [child for child in body.children if child.name]
        print(f"   Direct children count: {len(direct_children)}")
        for i, child in enumerate(direct_children[:10]):  # First 10 children
            classes = child.get('class', [])
            child_id = child.get('id', '')
            print(f"   Child {i+1}: <{child.name}> class={classes} id='{child_id}'")
    
    # 4. Navigation and header analysis
    print(f"\n4. NAVIGATION & HEADER ANALYSIS:")
    print("-" * 40)
    
    nav_elements = soup.find_all(['nav', 'header'])
    for i, nav in enumerate(nav_elements):
        classes = nav.get('class', [])
        nav_id = nav.get('id', '')
        print(f"   {nav.name.upper()} {i+1}: class={classes} id='{nav_id}'")
    
    # 5. Main content area analysis
    print(f"\n5. MAIN CONTENT AREA ANALYSIS:")
    print("-" * 40)
    
    main_elements = soup.find_all(['main', 'article', 'section'])
    for i, main in enumerate(main_elements[:5]):  # First 5 main elements
        classes = main.get('class', [])
        main_id = main.get('id', '')
        print(f"   {main.name.upper()} {i+1}: class={classes} id='{main_id}'")
    
    # 6. CRITICAL: Author section deep analysis
    print(f"\n🧑‍🔬 AUTHOR SECTION DEEP ANALYSIS")
    print("=" * 50)
    
    # Look for different author section patterns
    author_patterns = [
        ('section.core-authors', 'Core Authors Section'),
        ('section[class*="author"]', 'Author Class Sections'),
        ('div[class*="author"]', 'Author Div Containers'),
        ('[data-author]', 'Data Author Attributes'),
        ('section:contains("Author")', 'Sections containing "Author"'),
    ]
    
    for pattern, description in author_patterns:
        try:
            elements = soup.select(pattern)
            if elements:
                print(f"\n✓ FOUND: {description} ({len(elements)} elements)")
                for i, elem in enumerate(elements[:3]):  # First 3 matches
                    print(f"   Element {i+1}:")
                    print(f"     Tag: <{elem.name}>")
                    print(f"     Classes: {elem.get('class', [])}")
                    print(f"     ID: {elem.get('id', 'None')}")
                    
                    # Show first 200 chars of text content
                    text_content = elem.get_text()[:200].strip().replace('\n', ' ')
                    print(f"     Text preview: {text_content}...")
                    
                    # Show structure of first few children
                    children = [child for child in elem.children if child.name]
                    print(f"     Direct children: {len(children)}")
                    for j, child in enumerate(children[:3]):
                        child_classes = child.get('class', [])
                        print(f"       Child {j+1}: <{child.name}> class={child_classes}")
            else:
                print(f"❌ NOT FOUND: {description}")
        except Exception as e:
            print(f"❌ ERROR with {description}: {e}")
    
    # 7. Email link analysis
    print(f"\n📧 EMAIL LINKS ANALYSIS")
    print("-" * 30)
    
    email_patterns = [
        ('a[href^="mailto:"]', 'Mailto Links'),
        ('a[property="email"]', 'Property Email Links'),
        ('a[aria-label="Email address"]', 'Aria Label Email Links'),
        ('a:contains("@")', 'Links containing @'),
    ]
    
    for pattern, description in email_patterns:
        try:
            elements = soup.select(pattern)
            if elements:
                print(f"\n✓ FOUND: {description} ({len(elements)} elements)")
                for i, elem in enumerate(elements[:5]):  # First 5 matches
                    href = elem.get('href', '')
                    text = elem.get_text().strip()
                    aria_label = elem.get('aria-label', '')
                    property_attr = elem.get('property', '')
                    
                    print(f"   Email Link {i+1}:")
                    print(f"     HREF: {href}")
                    print(f"     Text: {text}")
                    print(f"     Aria-label: {aria_label}")
                    print(f"     Property: {property_attr}")
                    
                    # Analyze parent context
                    parent = elem.parent
                    if parent:
                        parent_classes = parent.get('class', [])
                        print(f"     Parent: <{parent.name}> class={parent_classes}")
            else:
                print(f"❌ NOT FOUND: {description}")
        except Exception as e:
            print(f"❌ ERROR with {description}: {e}")
    
    # 8. ORCID links analysis
    print(f"\n🔗 ORCID LINKS ANALYSIS")
    print("-" * 25)
    
    orcid_links = soup.find_all('a', href=re.compile(r'orcid\.org'))
    if orcid_links:
        print(f"✓ FOUND: {len(orcid_links)} ORCID links")
        for i, link in enumerate(orcid_links[:5]):
            href = link.get('href', '')
            classes = link.get('class', [])
            orcid_id = re.search(r'(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', href)
            orcid_id = orcid_id.group(1) if orcid_id else 'Not found'
            
            print(f"   ORCID {i+1}:")
            print(f"     HREF: {href}")
            print(f"     ORCID ID: {orcid_id}")
            print(f"     Classes: {classes}")
            
            # Parent context
            parent = link.parent
            if parent:
                parent_text = parent.get_text()[:100].strip().replace('\n', ' ')
                print(f"     Parent text: {parent_text}...")
    else:
        print("❌ NO ORCID links found")
    
    # 9. Affiliation structure analysis
    print(f"\n🏛️ AFFILIATION STRUCTURE ANALYSIS")
    print("-" * 35)
    
    affiliation_patterns = [
        ('div[property="affiliation"]', 'Property Affiliation Divs'),
        ('span[property="name"]', 'Property Name Spans'),
        ('.affiliation', 'Affiliation Class'),
        ('.affiliations', 'Affiliations Class'),
        ('div:contains("University")', 'Divs containing University'),
        ('div:contains("Department")', 'Divs containing Department'),
    ]
    
    for pattern, description in affiliation_patterns:
        try:
            elements = soup.select(pattern)
            if elements:
                print(f"✓ FOUND: {description} ({len(elements)} elements)")
                for i, elem in enumerate(elements[:3]):
                    text = elem.get_text().strip()[:150]
                    classes = elem.get('class', [])
                    property_attr = elem.get('property', '')
                    print(f"   Affiliation {i+1}: {text}...")
                    print(f"     Classes: {classes}, Property: {property_attr}")
            else:
                print(f"❌ NOT FOUND: {description}")
        except Exception as e:
            print(f"❌ ERROR with {description}: {e}")
    
    # 10. Schema.org and structured data analysis
    print(f"\n📊 STRUCTURED DATA ANALYSIS")
    print("-" * 30)
    
    # Look for schema.org markup
    schema_elements = soup.find_all(attrs={"property": True})
    if schema_elements:
        print(f"✓ FOUND: {len(schema_elements)} elements with 'property' attributes")
        property_types = {}
        for elem in schema_elements:
            prop = elem.get('property', '')
            if prop in property_types:
                property_types[prop] += 1
            else:
                property_types[prop] = 1
        
        print("   Property types found:")
        for prop, count in sorted(property_types.items()):
            print(f"     {prop}: {count} occurrences")
    
    # Look for JSON-LD structured data
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    if json_ld_scripts:
        print(f"\n✓ FOUND: {len(json_ld_scripts)} JSON-LD scripts")
        for i, script in enumerate(json_ld_scripts):
            content = script.get_text()[:200]
            print(f"   JSON-LD {i+1}: {content}...")
    
    # 11. Generate DOM path for author section
    print(f"\n🗺️ DOM PATH ANALYSIS")
    print("-" * 20)
    
    # Try to find the exact DOM path to author section
    core_authors = soup.select_one('section.core-authors')
    if core_authors:
        print("✓ Found section.core-authors - tracing DOM path:")
        path_elements = []
        current = core_authors
        
        while current and current.name != 'html':
            tag_name = current.name
            # Find position among siblings of same type
            siblings = [s for s in current.parent.children if s.name == tag_name] if current.parent else []
            position = siblings.index(current) + 1 if len(siblings) > 1 else 1
            
            classes = current.get('class', [])
            class_str = f".{'.'.join(classes)}" if classes else ""
            element_str = f"{tag_name}{class_str}[{position}]"
            path_elements.append(element_str)
            
            current = current.parent
        
        path_elements.reverse()
        dom_path = " > ".join(path_elements)
        print(f"   DOM Path: {dom_path}")
        
        # Also show CSS selector path
        css_selectors = []
        current = core_authors
        while current and current.name != 'html':
            selector = current.name
            if current.get('id'):
                selector += f"#{current['id']}"
            elif current.get('class'):
                selector += f".{'.'.join(current['class'])}"
            css_selectors.append(selector)
            current = current.parent
        
        css_selectors.reverse()
        css_path = " > ".join(css_selectors)
        print(f"   CSS Path: {css_path}")
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_html_structure()