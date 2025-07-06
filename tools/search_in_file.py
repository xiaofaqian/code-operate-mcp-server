"""
文件内容搜索工具
用于在指定文件中搜索字符串，支持正则匹配和精确匹配，返回匹配行号和内容
"""

import os
import re
from typing import Annotated


def search_in_file(
    file_path: Annotated[str, "要搜索的文件的完整路径"],
    search_text: Annotated[str, "要搜索的字符串或正则表达式"],
    match_type: Annotated[str, "匹配类型：'exact'（精确匹配）或 'regex'（正则匹配）"] = "exact",
    case_sensitive: Annotated[bool, "是否区分大小写，默认为False（不区分）"] = False
) -> str:
    """
    在指定文件中搜索字符串，支持精确匹配和正则表达式匹配
    
    Args:
        file_path: 要搜索的文件的完整路径
        search_text: 要搜索的字符串或正则表达式
        match_type: 匹配类型，'exact' 或 'regex'
        case_sensitive: 是否区分大小写
    
    Returns:
        包含搜索结果的详细信息字符串，包括匹配行号、内容和统计信息
    
    Raises:
        各种文件操作和正则表达式相关的异常
    """
    try:
        # 验证文件路径
        if not file_path:
            return "错误：文件路径不能为空"
        
        if not isinstance(file_path, str):
            return "错误：文件路径必须是字符串"
        
        # 验证搜索文本
        if not isinstance(search_text, str):
            return "错误：搜索文本必须是字符串"
        
        if not search_text:
            return "错误：搜索文本不能为空"
        
        # 验证匹配类型
        if match_type not in ["exact", "regex"]:
            return "错误：匹配类型必须是 'exact' 或 'regex'"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误：文件不存在 - {file_path}"
        
        # 检查是否为文件（而不是目录）
        if not os.path.isfile(file_path):
            return f"错误：指定路径不是文件 - {file_path}"
        
        # 检查文件权限
        if not os.access(file_path, os.R_OK):
            return f"错误：没有权限读取文件 - {file_path}"
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            try:
                # 尝试其他编码
                with open(file_path, 'r', encoding='gbk') as file:
                    lines = file.readlines()
            except UnicodeDecodeError:
                return f"错误：文件编码不支持，无法读取 - {file_path}"
        except PermissionError:
            return f"错误：没有权限读取文件 - {file_path}"
        except Exception as e:
            return f"错误：读取文件失败 - {str(e)}"
        
        # 获取文件总行数
        total_lines = len(lines)
        
        # 准备搜索模式
        if match_type == "regex":
            try:
                # 编译正则表达式
                flags = re.IGNORECASE if not case_sensitive else 0
                pattern = re.compile(search_text, flags)
            except re.error as e:
                return f"错误：正则表达式语法错误 - {str(e)}"
        else:
            # 精确匹配模式
            if not case_sensitive:
                search_text_lower = search_text.lower()
        
        # 搜索匹配行
        matches = []
        max_display = 100  # 最大显示结果数限制
        
        for line_num, line in enumerate(lines, 1):
            line_content = line.rstrip('\n\r')  # 移除行末换行符
            
            if match_type == "regex":
                # 正则匹配
                if pattern.search(line_content):
                    matches.append({
                        'line_num': line_num,
                        'content': line_content
                    })
            else:
                # 精确匹配
                if case_sensitive:
                    if search_text in line_content:
                        matches.append({
                            'line_num': line_num,
                            'content': line_content
                        })
                else:
                    if search_text_lower in line_content.lower():
                        matches.append({
                            'line_num': line_num,
                            'content': line_content
                        })
        
        # 计算显示的匹配项和隐藏的匹配项
        total_matches = len(matches)
        displayed_matches = matches[:max_display]
        hidden_count = max(0, total_matches - max_display)
        
        # 构建结果信息
        result_lines = []
        result_lines.append(f"文件路径: {file_path}")
        result_lines.append(f"总行数: {total_lines}")
        result_lines.append(f"搜索内容: \"{search_text}\"")
        result_lines.append(f"匹配类型: {'正则匹配' if match_type == 'regex' else '精确匹配'}")
        result_lines.append(f"区分大小写: {'是' if case_sensitive else '否'}")
        result_lines.append(f"匹配总数: {total_matches}")
        
        if hidden_count > 0:
            result_lines.append(f"显示结果: {len(displayed_matches)} 行（还有 {hidden_count} 行匹配项未显示）")
        
        result_lines.append("")
        
        if displayed_matches:
            result_lines.append("匹配结果:")
            for match in displayed_matches:
                result_lines.append(f"第{match['line_num']}行: {match['content']}")
            
            if hidden_count > 0:
                result_lines.append("")
                result_lines.append(f"注意：由于结果过多，仅显示前 {max_display} 行匹配结果")
        else:
            result_lines.append("未找到匹配内容")
        
        result_lines.append("")
        result_lines.append("搜索完成")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"搜索文件时发生未知错误: {str(e)}"
