import asyncio
from crawl4ai import *
import json
from aps_clean_extractor import extract_aps_clean_content


async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://journals.aps.org/prxquantum/abstract/10.1103/pyzr-jmvw",
        )
        result_json = result.json()
        
        # 将完整的result_json保存为json文件
        with open("result.json", "w") as f:
            json.dump(result_json, f)
            
        # 将完整结果保存为markdown文件
        with open("result.md", "w") as f:
            f.write(result.markdown)
            
        # 提取论文核心内容（标题到摘要）
        extracted_content = extract_aps_clean_content(result.markdown)
        
        # 保存提取的核心内容
        with open("extracted_content.md", "w") as f:
            f.write(extracted_content)
            
        print("爬取完成！")
        print(f"- 完整内容已保存到: result.md")
        print(f"- 提取的核心内容已保存到: extracted_content.md")
        print(f"- JSON数据已保存到: result.json")
    
    return extracted_content


# if __name__ == "__main__":
#     asyncio.run(main())