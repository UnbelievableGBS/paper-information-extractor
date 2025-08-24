import requests
import openai
import json

# 设置 API 密钥
openai.api_key = "你的OPENAI_API_KEY"

# 1. 假设用户输入了标题
paper_title = "Nuclear Spins and Magnetic Moments"

# 2. 调用 Semantic Scholar API
ss_url = f"https://www.nature.com/articles/s41586-025-09386-0"
params = {
    "query": paper_title,
    "fields": "title,authors,abstract,publicationDate",
    "limit": 1  # 只获取最相关的一个结果
}

try:
    response = requests.get(ss_url, params=params)
    
    # 检查请求是否成功
    response.raise_for_status()
    
    # 尝试解析 JSON
    data = response.json()
    print(data)
    # 检查是否有结果
    if not data.get('data') or len(data['data']) == 0:
        print("没有找到相关论文")
        exit()
        
    paper_data = data['data'][0]  # 取最相关的结果
    # print(paper_data)
    
    # 3. 准备给LLM的Prompt
    prompt = f"""
    请根据以下论文信息，用中文总结其摘要。
    论文标题：{paper_data.get('title', '未知')}
    作者：{', '.join([author.get('name', '未知') for author in paper_data.get('authors', [])])}
    摘要：{paper_data.get('abstract', '无摘要')}
    """

    # # 4. 调用 OpenAI API
    # completion = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": prompt}]
    # )

    # 5. 输出结果
    # print(completion.choices[0].message.content)

except requests.exceptions.RequestException as e:
    print(f"网络请求错误: {e}")
    print(f"响应状态码: {response.status_code if 'response' in locals() else '未知'}")
    print(f"响应内容: {response.text if 'response' in locals() else '无响应'}")
except json.JSONDecodeError as e:
    print(f"JSON 解析错误: {e}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"发生未知错误: {e}")