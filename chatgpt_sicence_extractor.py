import requests
from bs4 import BeautifulSoup
import json
import time
import random

def parse_science_authors(url: str):
    # FIXED: Complete browser headers that actually work
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1"
    }
    # Add retry mechanism with random delay
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random delay to avoid being flagged as bot
            time.sleep(random.uniform(1, 3))
            
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            break
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 and attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed with 403, retrying...")
                time.sleep(random.uniform(2, 5))  # Longer delay on 403
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

    soup = BeautifulSoup(resp.text, "html.parser")
    authors_section = soup.find("section", id="tab-contributors")

    if not authors_section:
        raise ValueError("Authors section not found - page structure may have changed")

    authors_data = []

    # Extract all authors
    for author_div in authors_section.select(".core-authors [property='author']"):
        author_info = {}

        heading = author_div.find("div", class_="heading")
        if heading:
            # Name
            given = heading.find("span", {"property": "givenName"})
            family = heading.find("span", {"property": "familyName"})
            author_info["name"] = f"{given.get_text(' ', strip=True)} {family.get_text(' ', strip=True)}" if given and family else None

            # Markers (co-first author †, corresponding author *)
            marks = [sup.get_text(strip=True) for sup in heading.find_all("sup")]
            author_info["marks"] = marks  # ["†", "*"]

            # ORCID
            orcid = heading.find("a", class_="orcid-id")
            author_info["orcid"] = orcid["href"] if orcid else None

            # Email (corresponding authors only)
            email = heading.find("a", {"property": "email"})
            author_info["email"] = email.get_text(strip=True) if email else None

        # Details (affiliations + contribution roles)
        content = author_div.find("div", class_="content")
        if content:
            # Affiliations
            affiliations = [aff.get_text(" ", strip=True) for aff in content.select(".affiliations [property='name']")]
            author_info["affiliations"] = affiliations

            # Contribution roles
            roles = content.find("div", class_="core-credits")
            if roles:
                author_info["roles"] = roles.get_text(" ", strip=True).replace("Roles :", "").replace("Role :", "").strip()

        authors_data.append(author_info)

    # Funding information
    funding_section = authors_section.find("section", class_="core-funding")
    funding_info = []
    if funding_section:
        for div in funding_section.find_all("div", role="paragraph"):
            funding_info.append(div.get_text(" ", strip=True))

    # Notes information
    notes_section = authors_section.find("section", class_="core-authors-notes")
    notes_info = {}
    if notes_section:
        for note in notes_section.find_all("div", role="doc-footnote"):
            label = note.find("div", class_="label")
            content = note.find("div", id=True)
            if label and content:
                notes_info[label.get_text(strip=True)] = content.get_text(" ", strip=True)

    result = {
        "authors": authors_data,
        "funding": funding_info,
        "notes": notes_info
    }

    return result


if __name__ == "__main__":
    # You can replace this with any Science paper URL
    url = "https://www.science.org/doi/10.1126/scitranslmed.ads7438"
    try:
        data = parse_science_authors(url)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error extracting data: {e}")
        print("This might be due to anti-bot protection or page structure changes.")
