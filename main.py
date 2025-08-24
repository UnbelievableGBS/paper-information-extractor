from operator import contains
from openai import OpenAI
import json
import nature_extractor as ne
import science_extractor as se
import aps_extractor as ae
import pandas as pd
import os
import re

api_key = os.getenv("DEEPSEEK_API_KEY", "sk-9d3e8463fbf34fb4ab915bef2baa9ba3")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

system_prompt = """
你是一个科研论文信息整理助手，你现在需要完成下面两个任务；
任务1: 根据以下论文 JSON 信息，生成一段中文新闻风格的介绍；
要求1：
1. 开头写明：发表日期、主要研究单位、期刊名称、论文标题（保持英文原题，括号内加中文翻译）。  
2. 中间插入论文摘要（直接引用，但需将“我们”统一改为“研究者们”）。  
3. 结尾描述：第一作者和通讯作者及其所属大学（单位只列到大学或者科研院所，不需要学院、系和实验室; 如果作者单位为多个，则均列出），国家信息，以及作者贡献（来自 JSON 的 "contributions" 字段）。  

任务2:根据以下论文 JSON 信息，提取论文中的关键信息；
要求2:
1. 输出论文第一作者/共同第一作者/通讯作者的单位，其中通讯作者的单位后面标记“*”
2. 输出其他作者的单位
3. 输出所有作者的单位所属国家
4. 输出论文的url链接及论文名
5. 如果为英文，请将单位/国家翻译成中文
6. 当未表示标识通讯作者时，则第一作者为通讯作者
注意：作者单位单位只列到大学或者科研院所，不需要学院、系或实验室。

输出的格式为：新闻风格介绍：xxx；论文信息提取：第一作者/共同作者单位/通讯作者单位：xxx，其他作者单位：xxx，所有作者单位所属国家：xxx，论文url链接：xxx，论文名：xxx

示例输入Json格式论文信息：
{
    "title": "Predicting topological entanglement entropy in a Rydberg analogue simulator",
    "url": "https://www.nature.com/articles/s41567-025-02944-3",
    "authors": [
        {
            "name": "Linda Mauron",
            "role": "First Author",
            "affiliations": [
                "Institute of Physics, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland",
                "Center for Quantum Science and Engineering, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland"
            ],
            "is_corresponding": false
        },
        {
            "name": "Zakari Denis",
            "role": "Other Author",
            "affiliations": [
                "Institute of Physics, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland",
                "Center for Quantum Science and Engineering, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland"
            ],
            "is_corresponding": false
        },
        {
            "name": "Jannes Nys",
            "role": "Other Author",
            "affiliations": [
                "Institute of Physics, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland",
                "Center for Quantum Science and Engineering, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland"
            ],
            "is_corresponding": false
        },
        {
            "name": "Giuseppe Carleo",
            "role": "Corresponding Author",
            "affiliations": [
                "Institute of Physics, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland",
                "Center for Quantum Science and Engineering, \u00c9cole Polytechnique F\u00e9d\u00e9rale de Lausanne (EPFL), Lausanne, Switzerland"
            ],
            "is_corresponding": true
        }
    ],
    "countries": [
        "Switzerland"
    ],
    "publication_date": {
        "iso_date": "2025-07-28",
        "formatted_date": "28 July 2025"
    },
    "abstract": "Predicting the dynamical properties of topological matter is a challenging task, not only in theoretical and experimental settings, but also computationally. Numerical studies are often constrained to studying simplified models and lattices. Here we propose a time-dependent correlated ansatz for the dynamical preparation of a quantum-spin-liquid state on a Rydberg atom simulator. Together with a time-dependent variational Monte Carlo technique, we can faithfully represent the state of the system throughout the entire dynamical preparation protocol. We are able to match not only the physically correct form of the Rydberg atom Hamiltonian but also the relevant lattice topology at system sizes that exceed current experimental capabilities. This approach gives access to global quantities such as the topological entanglement entropy, providing insight into the topological properties of the system. Our results confirm the topological properties of the state during the dynamical preparation protocol, and deepen our understanding of topological entanglement dynamics. We show that, while the simulated state exhibits local properties resembling those of a resonating-valence-bond state, in agreement with experimental observations, it lacks the latter\u2019s characteristic topological entanglement entropy signature irrespective of the degree of adiabaticity of the protocol.",
    "contributions": "L.M. wrote the code and performed the simulations. L.M. analysed the data with the help of Z.D. All authors contributed to the design of the methods and discussed the results. L.M. prepared the manuscript with input from all authors."
}
示例输出：
新闻风格介绍：7月28日，瑞士洛桑联邦理工学院（EPFL）的研究团队在《Nature Physics》期刊上发表了题为"Predicting topological entanglement entropy in a Rydberg analogue simulator"（里德堡模拟器中拓扑纠缠熵的预测）的论文。该研究开发了一种创新的时间相关变分蒙特卡洛方法，用于在里德堡原子模拟器上动态制备量子自旋液体态。

研究团队提出的时间相关关联拟设能够精确表征整个动态制备过程中系统的量子态演化，成功匹配了里德堡原子哈密顿量的物理形式和晶格拓扑结构。该方法使研究者能够获取拓扑纠缠熵等全局量，从而深入理解系统的拓扑特性。研究发现，虽然模拟态展现出与共振价键态相似的局域性质，但无论制备过程的绝热程度如何，都缺乏后者特有的拓扑纠缠熵特征。这一发现深化了人们对拓扑纠缠动力学的认识。

该研究的第一作者Linda Mauron来自瑞士洛桑联邦理工学院物理研究所和量子科学与工程中心，通讯作者为Giuseppe Carleo教授。研究团队指出，L.M.负责编写代码和进行模拟计算，并在Z.D.的协助下完成数据分析，所有作者共同参与了方法设计和结果讨论，L.M.在全体成员的指导下完成了论文撰写工作。这项研究完全在瑞士完成。

论文信息提取：第一作者/共同作者单位：洛桑联邦理工学院，通讯作者单位：洛桑联邦理工学院*，其他作者单位；洛桑联邦理工学院，所有作者单位所属国家：瑞士，论文url链接：https://www.nature.com/articles/s41567-025-02944-3，论文名：Predicting topological entanglement entropy in a Rydberg analogue simulator
"""

def extract_paper_info(response_text):
    """Extract structured data from LLM response using regex patterns."""
    patterns = {
        "新闻风格介绍": r"新闻风格介绍：(.*?)论文信息提取：",
        "第一作者单位": r"第一作者/共同作者单位：(.*?)，通讯作者单位：",
        "通讯作者单位": r"通讯作者单位：(.*?)，其他作者单位：",
        "其他作者单位": r"其他作者单位：(.*?)，所有作者单位所属国家：",
        "单位所属国家": r"所有作者单位所属国家：(.*?)，论文url链接：",
        "url": r"论文url链接：(.*?)，论文名：",
        "论文名": r"论文名：(.*)$"
    }
    
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.DOTALL)
        extracted[key] = match.group(1).strip() if match else "N/A"
    
    return extracted

def process_paper(paper_data):
    """Process a single paper and return structured data."""
    try:
        # paper_data = cne.parse_nature_authors(url)
        print(f"Paper data: {json.dumps(paper_data, indent=2)}")
        
        content = json.dumps(paper_data, indent=4)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            stream=False
        )
        
        response_text = response.choices[0].message.content
        print(f"LLM Response: {response_text}")
        
        return extract_paper_info(response_text)
        
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def main(url):
    if "nature" in url:
        paper_data = ne.parse_nature_authors(url)
        extracted_data = process_paper(paper_data)
    elif "science" in url:
        paper_data = se.parse_science_authors(url)
        extracted_data = process_paper(paper_data)
    elif "aps" in url:
        paper_data = ae.scrape_aps_authors(url)
        extracted_data = process_paper(paper_data)
    else:
        print("Invalid URL")
        exit()

    return extracted_data

# main function
if __name__ == "__main__":
    url = "https://journals.aps.org/prresearch/abstract/10.1103/9pbp-jzr9"
    extracted_data = main(url)
    print(extracted_data)

    # save to excel

    df = pd.DataFrame([extracted_data])
    df.to_excel("extracted_data.xlsx", index=False)