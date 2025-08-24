import asyncio
from crawl4ai import *
import json
from aps_clean_extractor import extract_aps_clean_content
import hashlib

async def async_crawl_aps(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        result_json = result.json()
        
        # 使用URL的哈希值作为文件名前缀，避免文件名冲突
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # 将完整的result_json保存为json文件
        json_filename = f"result_{url_hash}.json"
        with open(json_filename, "w") as f:
            json.dump(result_json, f)
            
        # 将完整结果保存为markdown文件
        md_filename = f"result_{url_hash}.md"
        with open(md_filename, "w") as f:
            f.write(result.markdown)
            
        # 提取论文核心内容（标题到摘要）
        extracted_content = extract_aps_clean_content(result.markdown)

        # 将提取的核心内容转换为json
        extracted_content_json = {
            "content": extracted_content
        }
        
        # 保存提取的核心内容
        extracted_filename = f"extracted_content_{url_hash}.md"
        with open(extracted_filename, "w") as f:
            f.write(extracted_content)
            
        print("爬取完成！")
        print(f"- 完整内容已保存到: {md_filename}")
        print(f"- 提取的核心内容已保存到: {extracted_filename}")
        print(f"- JSON数据已保存到: {json_filename}")
    
    return extracted_content_json

def crawl_aps(url):
    """
    同步函数，用于爬取APS网站内容
    
    Args:
        url (str): APS网站的URL
        
    Returns:
        str: 提取的论文核心内容
    """
    return asyncio.run(async_crawl_aps(url))

# # 使用示例
# if __name__ == "__main__":
#     url = "https://journals.aps.org/prxquantum/abstract/10.1103/pyzr-jmvw"
#     content = crawl_aps(url)
#     print("提取的内容:", content)