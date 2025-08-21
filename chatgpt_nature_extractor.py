import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

def extract_publication_date(soup):
    """Extract publication date from Nature paper HTML"""
    pub_date_elem = soup.select_one('li.c-article-identifiers__item time[datetime]')
    if pub_date_elem:
        return {
            "iso_date": pub_date_elem.get("datetime"),
            "formatted_date": pub_date_elem.get_text(strip=True)
        }
    return None

def extract_abstract(soup):
    """Extract abstract from Nature paper HTML"""
    abstract_elem = soup.select_one('#Abs1-content p')
    if abstract_elem:
        # Remove citation links but keep the text flow
        for sup in abstract_elem.find_all('sup'):
            sup.decompose()
        return abstract_elem.get_text(' ', strip=True)
    return None

def extract_contributions(soup):
    """Extract contributions section from Nature paper HTML"""
    # Look for the contributions heading
    contributions_heading = soup.find('h3', {'id': 'contributions'})
    if contributions_heading:
        # Get the next paragraph element which contains the contributions text
        contributions_para = contributions_heading.find_next_sibling('p')
        if contributions_para:
            return contributions_para.get_text(strip=True)
    
    # Alternative: look for contributions by class name
    contributions_elem = soup.select_one('h3.c-article__sub-heading#contributions + p')
    if contributions_elem:
        return contributions_elem.get_text(strip=True)
    
    return None

def extract_institution_only(affiliation):
    """Extract only school/research institute from affiliation, removing departments and countries"""
    # First extract country
    country_patterns = [
        (r',\s*([A-Z]{2,3})$', lambda m: m.group(1)),  # ', USA', ', UK', etc.
        (r',\s*([A-Z][a-z]+)$', lambda m: m.group(1)),  # ', China', ', Japan', etc.
        (r',\s*(United States)$', lambda m: 'USA'),
        (r',\s*(United Kingdom)$', lambda m: 'UK')
    ]
    
    country = ""
    clean_aff = affiliation
    
    for pattern, country_extractor in country_patterns:
        match = re.search(pattern, affiliation)
        if match:
            country = country_extractor(match)
            clean_aff = re.sub(pattern, '', affiliation).strip()
            break
    
    # Split by comma and reverse to find main institution (usually at the end)
    parts = [part.strip() for part in clean_aff.split(',')]
    parts.reverse()  # Start from the end (main institution usually last)
    
    # Institution keywords to identify the main institution
    main_institution_keywords = ['University', 'Institute', 'College', 'Academy', 'Hospital']
    
    institution = ""
    
    # Look for main institution keywords first
    for part in parts:
        if any(keyword in part for keyword in main_institution_keywords):
            # Skip if it's just a department
            if not any(dept_word in part.lower() for dept_word in [
                'department of', 'faculty of', 'school of', 'division of'
            ]):
                institution = part
                break
    
    # If no main institution found, look for other research entities
    if not institution:
        other_keywords = ['Center', 'Centre', 'Laboratory', 'Foundation', 'BioHub']
        for part in parts:
            if any(keyword in part for keyword in other_keywords):
                if not any(dept_word in part.lower() for dept_word in [
                    'department of', 'faculty of', 'school of', 'division of'
                ]):
                    institution = part
                    break
    
    # If still no institution found, use the last part
    if not institution and parts:
        institution = parts[0]  # Remember we reversed the list
    
    return institution.strip(), country

def extract_title(soup):
    """Extract paper title"""
    title_elem = soup.select_one('h1.c-article-title')
    if title_elem:
        return title_elem.get_text(strip=True)
    return "Unknown Title"

def parse_nature_authors(url: str):
    """Parse Nature paper and extract structured author information"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract basic paper info
    title = extract_title(soup)
    
    # Build affiliation map and author-affiliation mapping
    aff_list = soup.select("ol.c-article-author-affiliation__list > li")
    aff_map = {}
    author_aff_map = {}  # Map author names to their affiliations
    countries = set()
    
    for li in aff_list:
        aff_id = li.get("id")
        address = li.select_one(".c-article-author-affiliation__address")
        authors_list = li.select_one(".c-article-author-affiliation__authors-list")
        
        if address and authors_list:
            # Get the complete address text
            complete_address = address.get_text(strip=True)
            
            # Extract country for the countries set
            _, country = extract_institution_only(complete_address)
            if country:
                countries.add(country)
            
            # Store the complete address in the affiliation map
            aff_map[aff_id] = complete_address
            
            # Extract authors from this affiliation
            authors_text = authors_list.get_text(strip=True)
            # Split by comma and &, then clean up
            authors_in_aff = []
            for author_part in re.split(r',\s*|\s*&\s*', authors_text):
                author_name = author_part.strip()
                if author_name:
                    authors_in_aff.append(author_name)
                    # Map this author to this affiliation
                    if author_name not in author_aff_map:
                        author_aff_map[author_name] = []
                    author_aff_map[author_name].append(complete_address)

    # Extract corresponding authors
    corresponding_authors = set()
    corr_auths = soup.select("#corresponding-author-list a")
    for a in corr_auths:
        corresponding_authors.add(a.get_text(strip=True))
    
    # Extract all authors with their affiliations
    authors_data = []
    authors_list = soup.select("ol.c-article-authors-search > li")
    
    for idx, li in enumerate(authors_list):
        name = li.select_one(".js-search-name").get_text(strip=True)
        
        # Get affiliations for this author from our mapping
        author_affiliations = author_aff_map.get(name, [])
        
        # Determine author role
        role = "Other Author"
        if idx == 0:  # First author
            role = "First Author"
        if name in corresponding_authors:
            if idx == 0:
                role = "First/Corresponding Author"
            else:
                role = "Corresponding Author"
        
        authors_data.append({
            "name": name,
            "role": role,
            "affiliations": author_affiliations,
            "is_corresponding": name in corresponding_authors
        })

    return {
        "title": title,
        "url": url,
        "authors": authors_data,
        "countries": list(countries),
        "publication_date": extract_publication_date(soup),
        "abstract": extract_abstract(soup),
        "contributions": extract_contributions(soup)
    }

def create_nature_table(paper_data):
    """Create table matching the exact schema of nature information output.xlsx"""
    # Collect all unique affiliations first
    all_affiliations = set()
    first_corr_affiliations = set()
    other_affiliations = set()
    corresponding_affiliations = set()
    
    for author in paper_data["authors"]:
        for aff in author["affiliations"]:
            all_affiliations.add(aff)
            
            # Track corresponding author affiliations 
            if author["is_corresponding"]:
                corresponding_affiliations.add(aff)
            
            # Categorize by author role
            if author["role"] in ["First Author", "First/Corresponding Author", "Corresponding Author"]:
                first_corr_affiliations.add(aff)
            else:
                other_affiliations.add(aff)
    
    # Mark corresponding author affiliations with asterisk
    first_corr_list = []
    for aff in first_corr_affiliations:
        if aff in corresponding_affiliations:
            first_corr_list.append(aff + " *")
        else:
            first_corr_list.append(aff)
    
    # Create single row with Chinese column names matching the existing schema
    row = {
        "通信作者和第一/共一作者单位": "、".join(sorted(first_corr_list)) if first_corr_list else "",
        "其他作者单位": "、".join(sorted(other_affiliations)) if other_affiliations else "",
        "单位所属国家": "、".join(sorted(paper_data["countries"])) if paper_data["countries"] else "",
        "摘要": paper_data["abstract"] if paper_data["abstract"] else "",
        "贡献": paper_data["contributions"] if paper_data["contributions"] else "",
        "url": paper_data["url"]
    }
    
    return pd.DataFrame([row])


# if __name__ == "__main__":
#     url = "https://www.nature.com/articles/s41567-025-02944-3"
    
#     try:
#         # Extract paper data
#         paper_data = parse_nature_authors(url)
#         ## 格式化输出
#         print(json.dumps(paper_data, indent=4))

#         # # Create table with correct schema
#         # table = create_nature_table(paper_data)
#         # ## 保存到file
#         # with open("nature_information_output_new.json", "w") as f:
#         #     json.dump(paper_data, f)
            
#         # ## 保存到excel
#         # # Save to Excel file matching existing format
#         # output_file = "nature_information_output_new.xlsx"
#         # table.to_excel(output_file, index=False)
#         # print(f"✅ Data successfully saved to {output_file}")
        
        
#         # # Display table for verification
#         # print("\n=== Generated Table ===")
#         # print(table.to_string(index=False))
        
#     except Exception as e:
#         print(f"❌ Error processing paper: {e}")
#         import traceback
#         traceback.print_exc()
