"""
按行号替换代码工具
用于根据行号和代码内容替换文件中的指定行
"""

import os
from typing import Annotated, List, Dict, Any
from utils.syntax_checker import SyntaxChecker


def replace_code_by_line(
    file_path: Annotated[str, "目标文件的完整路径"],
    replacements: Annotated[List[Dict[str, Any]], "替换列表，每个元素必须包含两个必填字段：line（行号，从1开始计数的整数）和 code（新代码内容的字符串）"]
) -> str:
    """
    根据行号替换文件中指定行的代码
    
    此工具允许精确地替换文件中特定行的代码内容。
    支持批量替换多行，每次替换都会指定确切的行号和新的代码内容。
    如果指定的行号超过文件当前行数，工具会自动扩展文件以容纳新代码。
    
    重要说明：
    - replacements 参数中的每个替换项都必须包含两个必填字段：
      1. line: 整数类型，表示要替换的行号（从1开始计数）
      2. code: 字符串类型，表示新的代码内容
    - 不允许重复的行号
    - 当行号超过文件当前行数时，会自动在文件末尾添加空行以扩展文件
    
    Args:
        file_path: 目标文件的完整路径
        replacements: 替换列表，每个元素包含 line 和 code 字段
    
    Returns:
        操作结果的详细信息，包括扩展信息（如果有的话）
    
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
        
        # 检查文件权限
        if not os.access(file_path, os.R_OK):
            return f"错误：没有读取权限 - {file_path}"
        
        if not os.access(file_path, os.W_OK):
            return f"错误：没有写入权限 - {file_path}"
        
        # 验证 replacements 参数
        if not isinstance(replacements, list):
            return "错误：replacements 必须是一个列表"
        
        if not replacements:
            return "错误：替换列表不能为空"
        
        # 验证每个替换项的格式
        validated_replacements = []
        line_numbers = set()
        
        for i, item in enumerate(replacements):
            if not isinstance(item, dict):
                return f"错误：第{i+1}个替换项必须是字典格式"
            
            # 检查必填字段
            if "line" not in item:
                return f"错误：第{i+1}个替换项缺少必填字段 'line'"
            
            if "code" not in item:
                return f"错误：第{i+1}个替换项缺少必填字段 'code'"
            
            # 验证 line 字段
            try:
                line_num = int(item["line"])
            except (ValueError, TypeError):
                return f"错误：第{i+1}个替换项的 'line' 字段必须是整数"
            
            if line_num < 1:
                return f"错误：第{i+1}个替换项的行号必须大于0，当前值：{line_num}"
            
            if line_num in line_numbers:
                return f"错误：行号 {line_num} 重复出现"
            
            line_numbers.add(line_num)
            
            # 验证 code 字段
            if not isinstance(item["code"], str):
                return f"错误：第{i+1}个替换项的 'code' 字段必须是字符串"
            
            code_content = item["code"]
            validated_replacements.append({"line": line_num, "code": code_content})
        
        # 读取原文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                original_lines = file.readlines()
        except UnicodeDecodeError:
            return f"错误：文件编码不是UTF-8，无法读取 - {file_path}"
        except PermissionError:
            return f"错误：没有权限读取文件 - {file_path}"
        
        total_lines = len(original_lines)
        
        # 计算最大行号，用于判断是否需要扩展文件
        max_line_number = max(item["line"] for item in validated_replacements)
        
        # 按行号从大到小排序，避免替换时行号偏移问题
        validated_replacements.sort(key=lambda x: x["line"], reverse=True)
        
        # 创建新的文件内容
        new_lines = original_lines.copy()
        
        # 如果最大行号超过文件当前行数，则扩展文件
        lines_to_add = 0
        if max_line_number > total_lines:
            lines_to_add = max_line_number - total_lines
            # 添加空行到文件末尾
            for _ in range(lines_to_add):
                new_lines.append('\n')
        
        for item in validated_replacements:
            line_num = item["line"]
            new_code = item["code"]
            
            # 替换内容（保持原有的换行符）
            if not new_code.endswith('\n'):
                new_code += '\n'
            
            new_lines[line_num - 1] = new_code
        
        # 写入新内容
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except Exception as e:
            return f"错误：写入文件失败 - {str(e)}"
        
        # 构建基本结果信息
        result_info = []
        result_info.append(f"✅ 替换操作成功完成")
        result_info.append(f"文件路径: {file_path}")
        result_info.append(f"原文件行数: {total_lines}")
        if lines_to_add > 0:
            result_info.append(f"扩展行数: {lines_to_add}")
            result_info.append(f"扩展后行数: {total_lines + lines_to_add}")
        result_info.append(f"成功替换行数: {len(validated_replacements)}")
        
        # 检查是否为 Lua 文件
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.lua':
            result_info.append("")
            result_info.append("🔍 Lua 语法检查结果:")
            
            try:
                # 读取替换后的文件内容进行语法检查
                with open(file_path, 'r', encoding='utf-8') as file:
                    updated_content = file.read()
                
                # 调用语法检查器
                syntax_result = SyntaxChecker.check_syntax(updated_content, "lua")
                
                if syntax_result["is_valid"]:
                    result_info.append("✅ 语法检查通过，代码有效")
                else:
                    result_info.append("❌ 发现语法错误:")
                    for error in syntax_result["errors"]:
                        if error["line"] > 0:
                            result_info.append(f"- 第{error['line']}行，第{error['column']}列: {error['message']}")
                        else:
                            result_info.append(f"- {error['message']}")
                            
            except Exception as e:
                result_info.append(f"⚠️ 语法检查失败: {str(e)}")
        
        return "\n".join(result_info)
        
    except Exception as e:
        return f"执行替换操作时发生未知错误: {str(e)}"
