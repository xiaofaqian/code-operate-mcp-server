"""
读取文本文件工具
用于读取指定完整路径的文件，以UTF-8编码返回带行号的纯文本内容
"""

import os
from typing import Optional, Annotated
from mcp.server.fastmcp import FastMCP


def read_text_file(
    file_path: Annotated[str, "文件的完整路径"],
    start_line: Annotated[int, "开始读取的行号（从1开始），默认为1"] = 1,
    end_line: Annotated[Optional[int], "结束读取的行号，None表示读取到文件末尾"] = None,
    max_lines: Annotated[int, "最大读取行数限制，防止文件过大"] = 1000
) -> str:
    """
    读取指定路径的文本文件，返回带行号的内容
    
    Args:
        file_path: 文件的完整路径
        start_line: 开始读取的行号（从1开始）
        end_line: 结束读取的行号，None表示读取到文件末尾
        max_lines: 最大读取行数限制
    
    Returns:
        带行号的文件内容字符串
    
    Raises:
        各种文件操作相关的异常
    """
    try:
        # 验证文件路径
        if not file_path:
            return "错误：文件路径不能为空"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误：文件不存在 - {file_path}"
        
        # 检查是否为文件（而不是目录）
        if not os.path.isfile(file_path):
            return f"错误：指定路径不是文件 - {file_path}"
        
        # 验证行号参数
        if start_line < 1:
            return "错误：开始行号必须大于等于1"
        
        if end_line is not None and end_line < start_line:
            return "错误：结束行号不能小于开始行号"
        
        if max_lines < 1:
            return "错误：最大行数限制必须大于0"
        
        # 读取文件
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            return f"错误：文件编码不是UTF-8，无法读取 - {file_path}"
        except PermissionError:
            return f"错误：没有权限读取文件 - {file_path}"
        
        # 计算实际的结束行号
        total_lines = len(lines)
        actual_end_line = min(end_line or total_lines, start_line + max_lines - 1, total_lines)
        
        # 检查开始行号是否超出文件范围
        if start_line > total_lines:
            return f"错误：开始行号 {start_line} 超出文件总行数 {total_lines}"
        
        # 提取指定范围的行
        selected_lines = lines[start_line - 1:actual_end_line]
        
        # 格式化输出，添加行号
        result_lines = []
        for i, line in enumerate(selected_lines, start=start_line):
            # 移除行末的换行符，然后添加行号
            clean_line = line.rstrip('\n\r')
            result_lines.append(f"{i}: {clean_line}")
        
        # 添加文件信息头部
        info_header = f"文件路径: {file_path}\n"
        info_header += f"总行数: {total_lines}\n"
        info_header += f"显示范围: {start_line}-{actual_end_line}\n"
        info_header += "-" * 50 + "\n"
        
        # 如果读取的行数达到了限制，添加提示
        if actual_end_line - start_line + 1 >= max_lines:
            result_lines.append(f"\n注意：已达到最大行数限制 ({max_lines} 行)")
        
        return info_header + "\n".join(result_lines)
        
    except Exception as e:
        return f"读取文件时发生未知错误: {str(e)}"
