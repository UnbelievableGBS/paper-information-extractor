#!/usr/bin/env python3
"""
Fixed HTML Access - properly handle compressed content from Science.org
"""

import requests
from bs4 import BeautifulSoup
import time
import gzip
import io

def fixed_science_access():
    """Access Science.org with proper compression handling"""
    
    test_url = "https://www.science.org/doi/10.1126/scitranslmed.adn2601"
    print(f"🔍 FIXED HTML ACCESS ANALYSIS")
    print(f"📄 URL: {test_url}")
    print("=" * 80)
    
    # Method 1: Request without compression
    print("\n🔄 METHOD 1: Request without compression")
    print("-" * 45)
    
    session = requests.Session()
    
    # Headers that explicitly request no compression
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'identity',  # Request no compression
        'Referer': 'https://www.google.com/search?q=science+translational+medicine',
        'Origin': 'https://www.google.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        time.sleep(3)
        response = session.get(test_url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Response received")
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        # Check if content is binary or text
        try:
            text_content = response.text
            print(f"✅ Successfully decoded as text")
            print(f"Text length: {len(text_content)} characters")
            
            # Show first 1000 characters
            print(f"\nFirst 1000 characters:")
            print("-" * 30)
            print(text_content[:1000])
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(text_content, 'html.parser')
            
            # Basic analysis
            print(f"\n📊 SOUP ANALYSIS")
            print("-" * 20)
            print(f"Title: {soup.title.get_text() if soup.title else 'None'}")
            
            # Look for specific elements
            body = soup.find('body')
            if body:
                body_text = body.get_text().strip()
                print(f"Body text length: {len(body_text)} characters")
                if body_text:
                    print(f"Body text preview: {body_text[:500]}...")
            
            # Look for author-related content
            print(f"\n🔍 AUTHOR CONTENT SEARCH")
            print("-" * 25)
            
            # Search for key elements
            searches = [
                ('section.core-authors', 'Core authors section'),
                ('div[property="author"]', 'Author property divs'),
                ('a[href*="orcid"]', 'ORCID links'),
                ('a[property="email"]', 'Email property links'),
                ('a[href^="mailto:"]', 'Mailto links'),
            ]
            
            for selector, description in searches:
                elements = soup.select(selector)
                if elements:
                    print(f"✓ Found {len(elements)} {description}")
                    for i, elem in enumerate(elements[:3]):
                        print(f"  Element {i+1}: {elem.name}")
                        if elem.get_text().strip():
                            print(f"    Text: {elem.get_text().strip()[:100]}...")
                        if elem.get('href'):
                            print(f"    Href: {elem.get('href')}")
                else:
                    print(f"❌ No {description} found")
            
        except UnicodeDecodeError as e:
            print(f"❌ Could not decode as text: {e}")
            print("Content appears to be binary")
            
            # Show first 500 bytes as hex
            print(f"\nFirst 500 bytes (hex):")
            print(response.content[:500].hex())
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Try with gzip handling
    print(f"\n🔄 METHOD 2: Manual gzip decompression")
    print("-" * 40)
    
    session2 = requests.Session()
    session2.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',  # Allow gzip only
        'Connection': 'keep-alive',
    })
    
    try:
        time.sleep(3)
        response = session2.get(test_url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Response received")
        print(f"Status code: {response.status_code}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
        
        # Check if content is gzip compressed
        if response.headers.get('Content-Encoding') == 'gzip':
            print("Content is gzip compressed, decompressing...")
            try:
                decompressed = gzip.decompress(response.content)
                text_content = decompressed.decode('utf-8')
                print(f"✅ Successfully decompressed gzip content")
                print(f"Decompressed length: {len(text_content)} characters")
                print(f"Preview: {text_content[:500]}...")
            except Exception as e:
                print(f"❌ Gzip decompression failed: {e}")
        else:
            print("Content is not gzip compressed")
            text_content = response.text
            print(f"Text length: {len(text_content)} characters")
            print(f"Preview: {text_content[:500]}...")
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Try with different user agent and no encoding specification
    print(f"\n🔄 METHOD 3: Minimal headers approach")
    print("-" * 35)
    
    session3 = requests.Session()
    session3.headers.clear()  # Start with no headers
    session3.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; Research Bot)',
    })
    
    try:
        time.sleep(3)
        response = session3.get(test_url, timeout=30, stream=True)
        response.raise_for_status()
        
        print(f"✅ Response received")
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
        
        # Get raw content
        raw_content = response.content
        print(f"Raw content length: {len(raw_content)} bytes")
        
        # Try to decode as UTF-8
        try:
            text_content = raw_content.decode('utf-8')
            print(f"✅ Successfully decoded as UTF-8")
            print(f"Text length: {len(text_content)} characters")
            print(f"Preview: {text_content[:500]}...")
            
            # Quick parse
            soup = BeautifulSoup(text_content, 'html.parser')
            title = soup.title.get_text() if soup.title else 'No title'
            print(f"Page title: {title}")
            
        except UnicodeDecodeError:
            print(f"❌ Could not decode as UTF-8")
            # Try other encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    text_content = raw_content.decode(encoding)
                    print(f"✅ Successfully decoded as {encoding}")
                    print(f"Preview: {text_content[:500]}...")
                    break
                except:
                    continue
            else:
                print("❌ Could not decode with any standard encoding")
                print(f"First 100 bytes (hex): {raw_content[:100].hex()}")
        
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fixed_science_access()