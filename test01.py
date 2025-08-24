import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

def extract_nature_paper(url):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)
    authors = [a.get_text(strip=True) for a in soup.select("a[data-test='author-name']")]
    abstract = soup.find("div", {"id": "Abs1-content"}).get_text(strip=True)

    return {"title": title, "authors": authors, "abstract": abstract}

api_key = os.getenv("DEEPSEEK_API_KEY", "sk-9d3e8463fbf34fb4ab915bef2baa9ba3")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def summarize_paper(info, prompt="总结这篇论文的研究目的和主要结论"):
    text = f"标题: {info['title']}\n作者: {', '.join(info['authors'])}\n摘要: {info['abstract']}\n"
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": text}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    url = "https://www.nature.com/articles/s41586-025-09428-7"  # 示例链接
    info = extract_nature_paper(url)
    print(info)
    summary = summarize_paper(info)
    print(summary)
