import re
from typing import Optional


def extract_aps_clean_content(markdown_content: str) -> str:
    """
    精确提取APS论文的标题到摘要内容，完全去除图片和分享按钮
    
    Args:
        markdown_content: 完整的markdown内容
        
    Returns:
        清洁的核心内容（标题、作者、机构、DOI、摘要）
    """
    lines = markdown_content.split('\n')
    
    # 找到论文标题位置
    title_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('# ') and not _is_navigation_line(line):
            title_start = i
            break
    
    if title_start is None:
        return "未找到论文标题"
    
    # 找到摘要位置
    abstract_line = None
    for i in range(title_start, len(lines)):
        if lines[i].strip() == '## Abstract':
            abstract_line = i
            break
    
    if abstract_line is None:
        return "未找到摘要"
    
    # 找到摘要内容（通常是摘要标题后的第一个长段落）
    abstract_content = None
    for i in range(abstract_line + 1, len(lines)):
        line = lines[i].strip()
        if line and len(line) > 100:  # 摘要通常是很长的段落
            abstract_content = i
            break
    
    if abstract_content is None:
        return "未找到摘要内容"
    
    # 收集标题到摘要的所有内容
    result_lines = []
    
    for i in range(title_start, abstract_content + 1):
        line = lines[i]
        
        # 跳过不需要的内容
        if _should_skip_line(line):
            continue
            
        result_lines.append(line)
    
    return '\n'.join(result_lines).strip()


def _is_navigation_line(line: str) -> bool:
    """判断是否为网页导航行"""
    navigation_keywords = [
        'Skip to Main Content', 'Physical Review', 'All Journals',
        'Highlights', 'Recent', 'Collections'
    ]
    return any(keyword in line for keyword in navigation_keywords)


def _should_skip_line(line: str) -> bool:
    """判断是否应该跳过这一行"""
    line_stripped = line.strip()
    
    # 跳过纯符号行
    if line_stripped in ['open icon close icon', 'Shareopen icon close icon']:
        return True
    
    # 跳过分享按钮（包括列表项格式）
    share_buttons = ['X', 'Facebook', 'Mendeley', 'LinkedIn', 'Reddit', 'Sina Weibo']
    if line_stripped in share_buttons:
        return True
    
    # 跳过包含分享按钮的列表项 - 更精确的匹配
    if line_stripped.startswith('  *'):
        # 提取列表项的内容（去掉 "  * " 前缀）
        list_content = line_stripped[4:].strip()  # 去掉 "  * " 
        if list_content in share_buttons:
            return True
    
    # 跳过PDF分享相关行
    if '[PDF]' in line and ('Share' in line or any(btn in line for btn in share_buttons)):
        return True
    
    # 跳过altmetric链接
    if 'altmetric.com' in line or line_stripped == '[ ]':
        return True
    
    # 跳过Export Citation等操作
    if line_stripped in ['Export Citation', 'Show metricsopen icon close icon']:
        return True
    
    return False


if __name__ == "__main__":
    # 测试功能
    with open("result.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    extracted = extract_aps_clean_content(content)
    
    # 保存提取结果
    with open("clean_extracted.md", "w", encoding="utf-8") as f:
        f.write(extracted)
    
    print("清洁内容提取完成，已保存到 clean_extracted.md")