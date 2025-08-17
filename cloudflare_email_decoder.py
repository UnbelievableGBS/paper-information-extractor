#!/usr/bin/env python3
"""
CloudFlare Email Protection Decoder
Decodes CloudFlare protected email addresses from Science.org
"""

import requests
from bs4 import BeautifulSoup
import re
import time

def decode_cloudflare_email(protected_path):
    """
    Decode CloudFlare protected email from the protection path
    CloudFlare uses a simple XOR cipher to protect emails
    """
    try:
        # Extract the hex encoded part
        hex_part = protected_path.split('#')[-1]
        
        # Convert hex to bytes
        encoded_bytes = bytes.fromhex(hex_part)
        
        # The first byte is the key for XOR decoding
        key = encoded_bytes[0]
        
        # Decode the rest using XOR
        decoded_chars = []
        for byte in encoded_bytes[1:]:
            decoded_chars.append(chr(byte ^ key))
        
        return ''.join(decoded_chars)
    
    except Exception as e:
        print(f"Error decoding email: {e}")
        return None

def extract_emails_from_science_org():
    """Extract real email addresses from Science.org paper"""
    
    test_url = "https://www.science.org/doi/10.1126/scitranslmed.adn2601"
    print(f"🔍 CLOUDFLARE EMAIL EXTRACTION")
    print(f"📄 URL: {test_url}")
    print("=" * 80)
    
    # Use the working method from previous analysis
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'identity',  # No compression - this was the key!
        'Referer': 'https://www.google.com/search?q=science+translational+medicine',
        'Origin': 'https://www.google.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        time.sleep(3)
        response = session.get(test_url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Successfully accessed page")
        print(f"Content length: {len(response.text)} characters")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all CloudFlare protected email links
        print(f"\n📧 CLOUDFLARE EMAIL ANALYSIS")
        print("-" * 35)
        
        email_links = soup.find_all('a', href=re.compile(r'/cdn-cgi/l/email-protection'))
        print(f"Found {len(email_links)} CloudFlare protected email links")
        
        decoded_emails = []
        
        for i, link in enumerate(email_links):
            href = link.get('href', '')
            link_text = link.get_text().strip()
            property_attr = link.get('property', '')
            
            print(f"\nEmail Link {i+1}:")
            print(f"  Display text: {link_text}")
            print(f"  Property: {property_attr}")
            print(f"  Protected href: {href}")
            
            # Try to decode the email
            decoded_email = decode_cloudflare_email(href)
            
            if decoded_email:
                print(f"  ✅ Decoded email: {decoded_email}")
                decoded_emails.append({
                    'original_text': link_text,
                    'decoded_email': decoded_email,
                    'property': property_attr,
                    'link_element': link
                })
            else:
                print(f"  ❌ Could not decode email")
        
        # Now find author context for each email
        print(f"\n👥 AUTHOR-EMAIL MAPPING")
        print("-" * 25)
        
        author_divs = soup.select('div[property="author"]')
        print(f"Found {len(author_divs)} author containers")
        
        author_email_mapping = []
        
        for i, author_div in enumerate(author_divs):
            author_info = {
                'index': i + 1,
                'full_name': '',
                'orcid': '',
                'email': '',
                'is_corresponding': False
            }
            
            # Extract author name
            author_text = author_div.get_text()
            
            # Look for name pattern (before ORCID link)
            name_match = re.search(r'^([^h]+?)(?=\s*https://orcid\.org)', author_text)
            if name_match:
                author_name = name_match.group(1).strip()
                # Clean up common artifacts
                author_name = re.sub(r'[*†‡§¶#]+', '', author_name).strip()
                author_info['full_name'] = author_name
            
            # Extract ORCID
            orcid_link = author_div.find('a', href=re.compile(r'orcid\.org'))
            if orcid_link:
                orcid_match = re.search(r'(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', orcid_link.get('href', ''))
                if orcid_match:
                    author_info['orcid'] = orcid_match.group(1)
            
            # Check for email in this author's container
            email_link_in_author = author_div.find('a', href=re.compile(r'/cdn-cgi/l/email-protection'))
            if email_link_in_author:
                # Find the corresponding decoded email
                email_href = email_link_in_author.get('href', '')
                decoded_email = decode_cloudflare_email(email_href)
                if decoded_email:
                    author_info['email'] = decoded_email
                    author_info['is_corresponding'] = True
                    print(f"  ✅ Found email for {author_info['full_name']}: {decoded_email}")
            
            # Check for corresponding author markers
            if '*' in author_text or 'corresponding' in author_text.lower():
                author_info['is_corresponding'] = True
            
            author_email_mapping.append(author_info)
            
            print(f"\nAuthor {i+1}:")
            print(f"  Name: {author_info['full_name']}")
            print(f"  ORCID: {author_info['orcid']}")
            print(f"  Email: {author_info['email'] if author_info['email'] else 'None'}")
            print(f"  Corresponding: {'YES' if author_info['is_corresponding'] else 'No'}")
        
        # Summary
        print(f"\n📊 EXTRACTION SUMMARY")
        print("-" * 25)
        print(f"Total authors found: {len(author_email_mapping)}")
        
        authors_with_emails = [a for a in author_email_mapping if a['email']]
        corresponding_authors = [a for a in author_email_mapping if a['is_corresponding']]
        
        print(f"Authors with emails: {len(authors_with_emails)}")
        print(f"Corresponding authors: {len(corresponding_authors)}")
        
        print(f"\nCorresponding authors with emails:")
        for author in corresponding_authors:
            if author['email']:
                print(f"  • {author['full_name']} - {author['email']}")
        
        return author_email_mapping
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_cloudflare_decoder():
    """Test the CloudFlare email decoder with sample data"""
    print(f"\n🧪 TESTING CLOUDFLARE DECODER")
    print("-" * 30)
    
    # Test with the actual protected paths we found
    test_paths = [
        "/cdn-cgi/l/email-protection#2f5c5d4e4b5b444a6f495d4a4b475a5b4c4701405d48104c4c1248414a584d566f45474246014a4b5a094e425f144c4c124744464a426f495d4a4b475a5b4c4701405d48",
        "/cdn-cgi/l/email-protection#5526273431213e3015332730313d2021363d7b3a27326a363668323b3022372c153f3d383c7b303120733438256e3636683d3e3c303815332730313d2021363d7b3a2732",
        "/cdn-cgi/l/email-protection#e192938085958a84a1879384858994958289cf8e9386de8282dc868f84968398a18b898c88cf848594c7808c91da8282dc898a88848ca1879384858994958289cf8e9386"
    ]
    
    for i, path in enumerate(test_paths):
        print(f"\nTest {i+1}:")
        print(f"  Protected path: {path}")
        decoded = decode_cloudflare_email(path)
        print(f"  Decoded email: {decoded}")

if __name__ == "__main__":
    # First test the decoder
    test_cloudflare_decoder()
    
    # Then extract real emails
    extract_emails_from_science_org()