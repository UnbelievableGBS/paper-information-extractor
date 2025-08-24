# filename: aps_extractor.py
import re
import json
import time
import hashlib
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# 全局浏览器实例（复用提升性能）
_browser_instance = None
_context_instance = None

def get_browser():
    """获取复用的浏览器实例，增强反检测"""
    global _browser_instance, _context_instance
    if _browser_instance is None or _context_instance is None:
        p = sync_playwright().start()
        _browser_instance = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-default-apps',
                '--disable-web-security'
            ]
        )
        _context_instance = _browser_instance.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        # 移除webdriver痕迹
        _context_instance.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
    return _browser_instance, _context_instance

def get_cache_path(url):
    """生成缓存文件路径"""
    cache_dir = "/tmp/aps_cache"
    os.makedirs(cache_dir, exist_ok=True)
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(cache_dir, f"{url_hash}.html")

def get_html_with_playwright(url: str, use_cache: bool = True, wait_ms: int = 5000) -> str:
    """优化的Playwright HTML获取，支持缓存和浏览器复用"""
    # 检查缓存
    if use_cache:
        cache_path = get_cache_path(url)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()

    try:
        browser, context = get_browser()
        page = context.new_page()
        
        # 随机延迟避免被检测
        time.sleep(0.5 + (time.time() % 1))
        
        # 先访问首页建立session
        try:
            page.goto("https://journals.aps.org/", timeout=15000)
            time.sleep(1)
        except:
            pass
        
        # 访问目标页面
        page.goto(url, wait_until="networkidle", timeout=45000)
        
        # 等待关键元素出现
        key_selectors = [
            "div.authors-wrapper",
            "meta[name='citation_author']",
            "#abstract-section-content",
            "h1.title"
        ]
        
        for selector in key_selectors:
            try:
                page.wait_for_selector(selector, timeout=wait_ms)
                break
            except:
                continue
        
        # 处理弹窗
        try_dismiss_banners(page)
        
        # 额外等待动态内容
        time.sleep(1)
        
        html = page.content()
        page.close()
        
        # 保存到缓存
        if use_cache:
            cache_path = get_cache_path(url)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
        
    except Exception as e:
        print(f"Playwright error: {e}")
        # 如果失败，尝试从缓存读取
        if use_cache:
            cache_path = get_cache_path(url)
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
        raise


def try_dismiss_banners(page):
    """快速处理Cookie弹窗"""
    selectors = ["#onetrust-accept-btn-handler", "button[aria-label*='Accept']"]
    for sel in selectors:
        try:
            if page.locator(sel).count() > 0:
                page.locator(sel).first.click(timeout=500)
                return
        except:
            continue


# ---------------------------
# 解析函数（沿用你原来的逻辑）
# ---------------------------
def extract_aps_publication_date(soup: BeautifulSoup):
    pub_wrapper = soup.find('div', class_='pub-info-wrapper')
    if pub_wrapper:
        pub_strong = pub_wrapper.find('strong')
        if pub_strong and 'Published' in pub_strong.get_text():
            date_text = pub_strong.get_text(strip=True)
            date_match = re.search(r'Published\s+(.+)', date_text)
            if date_match:
                return date_match.group(1).strip()
    # 兜底：meta
    meta_pub = soup.select_one("meta[name='citation_publication_date']")
    if meta_pub and meta_pub.get("content"):
        return meta_pub["content"].strip()
    return None


def extract_aps_abstract(soup: BeautifulSoup):
    abstract_section = soup.find('div', id='abstract-section-content')
    if abstract_section:
        abstract_p = abstract_section.find('p')
        if abstract_p:
            return abstract_p.get_text(' ', strip=True)
    # 兜底：meta
    meta_abs = soup.select_one("meta[name='citation_abstract']")
    if meta_abs and meta_abs.get("content"):
        return meta_abs["content"].strip()
    return None


def extract_aps_title(soup: BeautifulSoup):
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
    # 兜底：meta
    meta_title = soup.select_one("meta[name='citation_title']")
    if meta_title and meta_title.get("content"):
        return meta_title["content"].strip()
    return "Unknown Title"


def extract_aps_journal_name(soup: BeautifulSoup):
    journal_selectors = [
        '.journal-title',
        '.journal-name',
        'meta[name="citation_journal_title"]',
        'meta[property="og:site_name"]',
        '.header-journal-title',
        'h1.journal-title'
    ]
    for selector in journal_selectors:
        if selector.startswith('meta'):
            journal_elem = soup.select_one(selector)
            if journal_elem and journal_elem.get('content'):
                return journal_elem['content'].strip()
        else:
            journal_elem = soup.select_one(selector)
            if journal_elem:
                return journal_elem.get_text(' ', strip=True)
    return "Physical Review (APS)"


def parse_authors_from_dom(soup: BeautifulSoup):
    """多层级作者信息提取策略"""
    authors = []

    # 策略1：完整DOM解析
    authors_wrapper = soup.find('div', class_='authors-wrapper')
    if authors_wrapper:
        authors = parse_authors_detailed(authors_wrapper)
        if authors:
            return authors

    # 策略2：文本模式解析（更宽泛的DOM结构）
    author_selectors = [
        '.authors p',
        '.author-list',
        '.contrib-group .contrib',
        'div[class*="author"] p'
    ]
    
    for selector in author_selectors:
        elements = soup.select(selector)
        if elements:
            authors = parse_authors_from_text(elements[0], soup)
            if authors:
                break

    # 策略3：meta标签兜底
    if not authors:
        authors = parse_authors_from_meta(soup)

    # 策略4：通用模式解析（最后兜底）
    if not authors:
        authors = parse_authors_fallback(soup)

    return authors

def parse_authors_detailed(authors_wrapper):
    """原有详细解析逻辑"""
    authors = []
    authors_line = authors_wrapper.find('p')
    details_section = authors_wrapper.find('details')
    affil_dict, role_dict = {}, {}

    if details_section:
        # 机构映射
        affil_list = details_section.find('ul', class_='no-bullet')
        if affil_list:
            for item in affil_list.find_all('li'):
                sup = item.find('sup')
                if sup:
                    num = sup.text.strip()
                    sup.decompose()
                    affil_dict[num] = item.get_text(strip=True)

        # 角色映射
        contrib_notes = details_section.find('ul', class_='contrib-notes')
        if contrib_notes:
            for note in contrib_notes.find_all('li'):
                sup = note.find('sup')
                if sup:
                    symbol = sup.text.strip()
                    sup.decompose()
                    role_dict[symbol] = note.get_text(strip=True)

    current_author = {'name': '', 'affiliations': [], 'roles': []}
    if authors_line:
        for element in authors_line.children:
            if isinstance(element, str) and element.strip() == '':
                continue

            name = getattr(element, "name", None)
            if name == 'a' and '/search/field/author/' in element.get('href', ''):
                if current_author['name']:
                    authors.append(current_author.copy())
                current_author = {
                    'name': element.text.strip(),
                    'affiliations': [],
                    'roles': []
                }
            elif name == 'sup':
                marks = [m.strip() for m in element.text.split(',')]
                for mark in marks:
                    if mark.isdigit() and affil_dict.get(mark):
                        current_author['affiliations'].append(affil_dict[mark])
                    elif role_dict.get(mark):
                        current_author['roles'].append(role_dict[mark])
            elif isinstance(element, str) and 'and' in element.lower() and current_author['name']:
                authors.append(current_author.copy())

        if current_author['name']:
            authors.append(current_author.copy())

    return authors

def parse_authors_from_text(element, soup):
    """从文本中提取作者信息"""
    authors = []
    text = element.get_text()
    
    # 简单作者名提取
    author_patterns = [
        r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'([A-Z]\.\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in author_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for name in matches[:10]:  # 限制最多10个作者避免误匹配
                authors.append({
                    'name': name.strip(),
                    'affiliations': [],
                    'roles': []
                })
            break
    
    return authors

def parse_authors_from_meta(soup):
    """从meta标签提取作者信息"""
    authors = []
    meta_authors = [m.get("content", "").strip() for m in soup.select("meta[name='citation_author']")]
    meta_affils = [m.get("content", "").strip() for m in soup.select("meta[name='citation_author_institution']")]
    
    if meta_authors:
        if meta_affils and len(meta_affils) == len(meta_authors):
            for a, org in zip(meta_authors, meta_affils):
                authors.append({"name": a, "affiliations": [org], "roles": []})
        else:
            for a in meta_authors:
                authors.append({"name": a, "affiliations": [], "roles": []})
    
    return authors

def parse_authors_fallback(soup):
    """通用兜底解析策略"""
    authors = []
    
    # 查找可能包含作者的所有链接
    author_links = soup.find_all('a', href=lambda x: x and 'author' in x.lower())
    for link in author_links[:10]:  # 限制数量
        name = link.get_text(strip=True)
        if name and len(name.split()) >= 2:  # 至少两个词
            authors.append({
                'name': name,
                'affiliations': [],
                'roles': []
            })
    
    return authors


def scrape_aps_authors(url: str, use_cache: bool = True):
    """优化的APS论文信息提取"""
    try:
        # 使用优化的HTML获取
        html = get_html_with_playwright(url, use_cache=use_cache)
        soup = BeautifulSoup(html, "lxml")

        # 并行提取所有信息
        pub_date = extract_aps_publication_date(soup)
        abstract = extract_aps_abstract(soup)
        title = extract_aps_title(soup)
        journal_name = extract_aps_journal_name(soup)
        authors = parse_authors_from_dom(soup)

        # 数据质量检查和补强
        if not authors:
            print("Warning: No authors found, trying alternative extraction...")
        
        if not title or title == "Unknown Title":
            print("Warning: Title extraction failed")

        result = {
            'authors': authors,
            'publication_date': pub_date,
            'abstract': abstract,
            'title': title,
            'journal_name': journal_name,
            'url': url,
            'extraction_quality': {
                'has_authors': len(authors) > 0,
                'has_abstract': abstract is not None,
                'has_title': title is not None and title != "Unknown Title",
                'author_count': len(authors)
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Error during extraction: {str(e)}"
        print(error_msg)
        return json.dumps({
            'authors': [],
            'publication_date': None,
            'abstract': None,
            'title': None,
            'journal_name': None,
            'url': url,
            'error': str(e),
            'extraction_quality': {
                'has_authors': False,
                'has_abstract': False,
                'has_title': False,
                'author_count': 0
            }
        }, ensure_ascii=False, indent=2)

def cleanup_browser():
    """清理浏览器实例"""
    global _browser_instance, _context_instance
    try:
        if _context_instance:
            _context_instance.close()
        if _browser_instance:
            _browser_instance.close()
    except:
        pass
    finally:
        _browser_instance = None
        _context_instance = None


if __name__ == "__main__":
    import sys
    import atexit
    
    # 注册清理函数
    atexit.register(cleanup_browser)
    
    if len(sys.argv) >= 2:
        paper_url = sys.argv[1]
        use_cache = "--no-cache" not in sys.argv
    else:
        # 测试URL
        paper_url = "https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.130.267401"
        use_cache = True

    print(f"Extracting from: {paper_url}")
    print(f"Cache enabled: {use_cache}")
    print("-" * 50)
    
    result = scrape_aps_authors(paper_url, use_cache=use_cache)
    print(result)
    
    # 手动清理
    cleanup_browser()