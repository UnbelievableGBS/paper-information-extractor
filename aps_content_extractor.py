import re
from typing import Optional


def extract_aps_paper_content(markdown_content: str) -> str:
    """
    从APS论文的markdown内容中提取标题到摘要的核心部分，去除图片链接
    
    Args:
        markdown_content: 完整的markdown内容
        
    Returns:
        提取的核心内容（标题到摘要结束）
    """
    lines = markdown_content.split('\n')
    
    # 找到论文标题的起始位置
    title_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('# ') and not _is_navigation_line(line):
            title_start = i
            break
    
    if title_start is None:
        return "未找到论文标题"
    
    # 找到摘要开始位置
    abstract_start = None
    for i in range(title_start, len(lines)):
        if lines[i].strip().startswith('## Abstract'):
            abstract_start = i
            break
    
    if abstract_start is None:
        return "未找到摘要部分"
    
    # 简单策略：收集从标题到摘要的内容，在摘要后遇到第一个图片时停止
    result_lines = []
    in_abstract_text = False
    
    for i in range(title_start, len(lines)):
        line = lines[i]
        line_stripped = line.strip()
        
        # 开始收集摘要文本
        if line_stripped.startswith('## Abstract'):
            result_lines.append(line)
            in_abstract_text = True
            continue
        
        # 在摘要中遇到图片链接，停止
        if in_abstract_text and (line_stripped.startswith('![') or 
                                (line_stripped.startswith('  *') and '![' in line_stripped)):
            break
            
        # 过滤不需要的内容
        if _should_filter_line(line):
            continue
            
        result_lines.append(line)
    
    # 清理并返回
    return _clean_empty_lines('\n'.join(result_lines))


def _is_navigation_line(line: str) -> bool:
    """判断是否为网页导航行"""
    navigation_keywords = [
        'Skip to Main Content', 'Physical Review', 'All Journals', 
        'Highlights', 'Recent', 'Collections', 'Authors', 'RSS'
    ]
    return any(keyword in line for keyword in navigation_keywords)


def _should_filter_line(line: str) -> bool:
    """判断是否应该过滤掉这一行"""
    line = line.strip()
    
    # 过滤图片链接（包括列表中的图片）
    if line.startswith('![') or (line.startswith('  *') and '![' in line):
        return True
    
    # 过滤分享按钮相关内容
    share_buttons = ['X', 'Facebook', 'Mendeley', 'LinkedIn', 'Reddit', 'Sina Weibo']
    if line in share_buttons:
        return True
    
    # 过滤包含分享按钮的列表项
    if line.startswith('  *') and any(button in line for button in share_buttons):
        return True
        
    # 过滤纯符号行和无意义内容
    meaningless_lines = [
        'open icon close icon', 
        'Shareopen icon close icon',
        'Show metricsopen icon close icon',
        'Export Citation'
    ]
    if line in meaningless_lines:
        return True
        
    # 过滤altmetric和空链接
    if 'altmetric.com' in line or line == '[ ]':
        return True
    
    # 过滤PDF分享行（包含多个分享选项的行）
    if line.startswith('[PDF]') and 'Shareopen icon close icon' in line:
        return True
    
    return False


def _find_content_end(lines: list, start_idx: int) -> Optional[int]:
    """当没有明确结束标记时，尝试推断内容结束位置"""
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        
        # 遇到Physics Subject Headings标记内容结束
        if 'Physics Subject Headings' in line or 'PhySH' in line:
            return i
            
        # 遇到Popular Summary标记内容结束
        if line.startswith('## Popular Summary'):
            return i
            
        # 遇到连续的图片链接
        if line.startswith('![') and i + 1 < len(lines) and lines[i + 1].strip().startswith('!['):
            return i
    
    # 如果找不到明确结束，返回合理的默认位置
    return min(start_idx + 50, len(lines))  # 限制最多50行


def _clean_empty_lines(content: str) -> str:
    """清理多余的空行"""
    lines = content.split('\n')
    result_lines = []
    prev_empty = False
    
    for line in lines:
        is_empty = not line.strip()
        
        if is_empty:
            if not prev_empty:  # 只保留一个连续的空行
                result_lines.append(line)
            prev_empty = True
        else:
            result_lines.append(line)
            prev_empty = False
    
    return '\n'.join(result_lines).strip()


if __name__ == "__main__":
    # 测试功能
    with open("result.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    extracted = extract_aps_paper_content(content)
    
    # 保存提取结果
    with open("extracted_content.md", "w", encoding="utf-8") as f:
        f.write(extracted)
    
    print("内容提取完成，已保存到 extracted_content.md")