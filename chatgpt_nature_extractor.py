import requests
from bs4 import BeautifulSoup
import json

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

def parse_nature_authors(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    result = {
        "authors": [],
        "affiliations": [],
        "contributions": "",
        "corresponding_authors": [],
        "publication_date": extract_publication_date(soup),
        "abstract": extract_abstract(soup)
    }

    # 1. Affiliations & authors (机构+作者对应关系)
    aff_list = soup.select("ol.c-article-author-affiliation__list > li")
    aff_map = {}  # 机构ID -> 机构信息
    for li in aff_list:
        aff_id = li.get("id")
        address = li.select_one(".c-article-author-affiliation__address")
        authors = li.select_one(".c-article-author-affiliation__authors-list")
        aff_map[aff_id] = {
            "address": address.get_text(strip=True) if address else "",
            "authors": [a.strip() for a in authors.get_text().replace("\xa0", " ").split(",") if a.strip()] if authors else []
        }
        result["affiliations"].append(aff_map[aff_id])

    # 2. Authors info (带外部链接)
    authors_list = soup.select("ol.c-article-authors-search > li")
    for li in authors_list:
        name = li.select_one(".js-search-name").get_text(strip=True)
        # 所属机构id写在 li 的 id 里
        li_id = li.get("id", "")
        aff_ids = [part for part in li_id.split("-") if part.startswith("Aff")]
        # 外部链接
        links = {}
        for a in li.select("a.c-article-identifiers__item"):
            if "pubmed" in a["href"].lower():
                links["PubMed"] = a["href"]
            elif "scholar.google" in a["href"].lower():
                links["Google Scholar"] = a["href"]

        result["authors"].append({
            "name": name,
            "affiliations": [aff_map[aid]["address"] for aid in aff_ids if aid in aff_map],
            "links": links
        })

    # 3. Contributions
    contrib = soup.select_one("#contributions + p")
    if contrib:
        result["contributions"] = contrib.get_text(" ", strip=True)

    # 4. Corresponding authors
    corr_auths = soup.select("#corresponding-author-list a")
    for a in corr_auths:
        name = a.get_text(strip=True)
        email = a.get("href", "").replace("mailto:", "")
        result["corresponding_authors"].append({
            "name": name,
            "email": email
        })

    return result


if __name__ == "__main__":
    url = "https://www.nature.com/articles/s41586-025-09403-2#author-information"  # 示例论文链接
    data = parse_nature_authors(url)
    print(json.dumps(data, ensure_ascii=False, indent=2))
