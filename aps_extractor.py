import requests
from bs4 import BeautifulSoup
import re
import time
import random
import json

def extract_aps_publication_date(soup):
    """Extract publication date from APS paper HTML"""
    pub_wrapper = soup.find('div', class_='pub-info-wrapper')
    if pub_wrapper:
        pub_strong = pub_wrapper.find('strong')
        if pub_strong and 'Published' in pub_strong.get_text():
            # Extract date from "Published DD Month, YYYY" format
            date_text = pub_strong.get_text(strip=True)
            date_match = re.search(r'Published\s+(.+)', date_text)
            if date_match:
                return date_match.group(1).strip()
    return None

def extract_aps_abstract(soup):
    """Extract abstract from APS paper HTML"""
    abstract_section = soup.find('div', id='abstract-section-content')
    if abstract_section:
        abstract_p = abstract_section.find('p')
        if abstract_p:
            # Keep the complete text with italic formatting preserved
            return abstract_p.get_text(' ', strip=True)
    return None

def extract_aps_title(soup):
    """Extract title from APS paper HTML"""
    # Try multiple selectors for APS title
    title_selectors = [
        'h1.title',
        'h1[data-behavior="title"]',
        'h1.article-title',
        '.title-wrapper h1',
        'title'
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            return title_elem.get_text(' ', strip=True)
    return "Unknown Title"

def scrape_aps_authors(url):
    # FIXED: Complete browser headers that actually work for APS
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
    }
    
    # Add retry mechanism with random delay
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random delay to avoid being flagged as bot
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            break
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 and attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed with 403, retrying...")
                time.sleep(random.uniform(3, 6))  # Longer delay for APS
                continue
            else:
                raise
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}, retrying...")
                time.sleep(random.uniform(2, 5))
                continue
            else:
                raise
    
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract publication date, abstract, and title
        pub_date = extract_aps_publication_date(soup)
        abstract = extract_aps_abstract(soup)
        title = extract_aps_title(soup)
        
        # Locate authors information area
        authors_wrapper = soup.find('div', class_='authors-wrapper')
        if not authors_wrapper:
            print("Authors information area not found")
            return []
        
        # Extract authors line
        authors_line = authors_wrapper.find('p')
        if not authors_line:
            print("Authors line not found")
            return []
        
        # Parse collapsible details section
        details_section = authors_wrapper.find('details')
        affil_dict = {}
        role_dict = {}
        
        if details_section:
            # Extract affiliation information
            affil_list = details_section.find('ul', class_='no-bullet')
            if affil_list:
                for item in affil_list.find_all('li'):
                    sup = item.find('sup')
                    if sup:
                        num = sup.text.strip()
                        sup.decompose()
                        affil_text = item.get_text(strip=True)
                        affil_dict[num] = affil_text
            
            # Extract contribution notes
            contrib_notes = details_section.find('ul', class_='contrib-notes')
            if contrib_notes:
                for note in contrib_notes.find_all('li'):
                    sup = note.find('sup')
                    if sup:
                        symbol = sup.text.strip()
                        sup.decompose()
                        note_text = note.get_text(strip=True)
                        role_dict[symbol] = note_text
        
        # Process authors line
        authors = []
        current_author = {'name': '', 'orcid': '', 'affiliations': [], 'roles': []}
        
        # Traverse all child nodes (complex structure)
        for element in authors_line.children:
            # Skip empty text and comments
            if isinstance(element, str) and element.strip() == '':
                continue
                
            if element.name == 'a':
                # Handle author name links
                if '/search/field/author/' in element.get('href', ''):
                    # Save previous author
                    if current_author['name']:
                        authors.append(current_author.copy())
                    
                    # Start new author
                    current_author = {
                        'name': element.text.strip(),
                        # 'orcid': '',
                        'affiliations': [],
                        'roles': []
                    }
                # Handle ORCID links
                # elif 'orcid' in element.get('href', ''):
                    # current_author['orcid'] = element.get('href', '')
                    
            elif element.name == 'sup':
                # Handle superscripts (affiliation and role markers)
                marks = [m.strip() for m in element.text.split(',')]
                for mark in marks:
                    if mark.isdigit():
                        # Affiliation marker
                        if affil_dict.get(mark):
                            current_author['affiliations'].append(affil_dict[mark])
                    else:
                        # Role marker
                        if role_dict.get(mark):
                            current_author['roles'].append(role_dict[mark])
            
            # Handle text nodes (including separators)
            elif isinstance(element, str):
                if 'and' in element.lower():
                    if current_author['name']:
                        authors.append(current_author.copy())
        
        # Add the last author
        if current_author['name']:
            authors.append(current_author.copy())
        
        # 格式化json输出
        result = {
            'authors': authors,
            'publication_date': pub_date,
            'abstract': abstract,
            'title': title,
            'url': url
        }
        result = json.dumps(result, indent=4)
        # Return results with publication date and abstract
        return result

    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return {'authors': [], 'publication_date': None, 'abstract': None}

# # Usage example
# if __name__ == "__main__":
#     # Replace with actual APS paper URL
#     # Replace with actual APS paper URL (working example)
#     paper_url = "https://journals.aps.org/prl/abstract/10.1103/76xj-j9qr"
    
#     try:
#         result = scrape_aps_authors(paper_url)
#         print(result)
#         # authors_info = result.get('authors', [])
#         # pub_date = result.get('publication_date')
#         # abstract = result.get('abstract')
        
#         # # Format output results
#         # print(f"\n📅 Publication Date: {pub_date if pub_date else 'Not found'}")
#         # print(f"\n📄 Abstract: {abstract[:200] + '...' if abstract and len(abstract) > 200 else abstract or 'Not found'}")
        
#         # if authors_info:
#         #     print(f"\n✅ Successfully extracted {len(authors_info)} authors:")
#         #     for i, author in enumerate(authors_info, 1):
#         #         print(f"\nAuthor #{i}: {author['name']}")
#         #         print(f"  ORCID: {author['orcid'] if author['orcid'] else 'None'}")
#         #         print(f"  Affiliations: {', '.join(author['affiliations']) if author['affiliations'] else 'None'}")
#         #         print(f"  Roles: {', '.join(author['roles']) if author['roles'] else 'None'}")
#         # else:
#         #     print("❌ No author information found")
#         #     print("This might be due to:")
#         #     print("  - Anti-bot protection")
#         #     print("  - Page structure changes")
#         #     print("  - Invalid URL")
            
#     except Exception as e:
#         print(f"❌ Failed to extract authors: {e}")
#         print("Please check the URL and try again.")