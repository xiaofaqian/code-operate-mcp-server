"""
创建文件工具
用于创建指定路径的文件，自动创建不存在的目录路径，支持 Lua 文件语法检查
"""

import os
from typing import Annotated
from utils.syntax_checker import SyntaxChecker


def create_file(
    file_path: Annotated[str, "要创建的文件的完整路径"],
    content: Annotated[str, "要写入文件的内容，可以为空字符串"] = ""
) -> str:
    """
    创建指定路径的文件并写入内容
    
    此工具会自动创建文件路径中不存在的目录，然后创建文件并写入指定内容。
    如果是 .lua 文件且内容不为空，会自动进行语法检查。
    
    Args:
        file_path: 要创建的文件的完整路径
        content: 要写入文件的内容，可以为空字符串
    
    Returns:
        操作结果的详细信息，包括文件创建状态和语法检查结果（如果适用）
    
    Raises:
        各种文件操作相关的异常
    """
    try:
        # 验证文件路径
        if not file_path:
            return "错误：文件路径不能为空"
        
        if not isinstance(file_path, str):
            return "错误：文件路径必须是字符串"
        
        # 验证内容参数
        if not isinstance(content, str):
            return "错误：文件内容必须是字符串"
        
        # 获取文件所在目录
        directory = os.path.dirname(file_path)
        
        # 如果目录不为空且不存在，则创建目录
        directories_created = []
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                directories_created.append(directory)
            except PermissionError:
                return f"错误：没有权限创建目录 - {directory}"
            except OSError as e:
                return f"错误：创建目录失败 - {str(e)}"
        
        # 检查目录权限（如果目录存在）
        if directory and os.path.exists(directory):
            if not os.access(directory, os.W_OK):
                return f"错误：没有权限在目录中创建文件 - {directory}"
        
        # 检查文件是否已存在
        file_already_exists = os.path.exists(file_path)
        if file_already_exists:
            # 检查是否为文件（而不是目录）
            if not os.path.isfile(file_path):
                return f"错误：指定路径已存在且不是文件 - {file_path}"
            
            # 检查文件权限
            if not os.access(file_path, os.W_OK):
                return f"错误：没有权限覆盖现有文件 - {file_path}"
        
        # 创建文件并写入内容
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except PermissionError:
            return f"错误：没有权限创建文件 - {file_path}"
        except OSError as e:
            return f"错误：创建文件失败 - {str(e)}"
        except UnicodeEncodeError:
            return f"错误：文件内容包含无法编码的字符 - {file_path}"
        
        # 获取文件信息
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            file_size = 0
        
        # 构建基本结果信息
        result_info = []
        result_info.append("✅ 文件创建成功")
        result_info.append(f"文件路径: {file_path}")
        result_info.append(f"文件大小: {file_size} 字节")
        
        if file_already_exists:
            result_info.append("📝 已覆盖现有文件")
        else:
            result_info.append("🆕 创建新文件")
        
        if directories_created:
            result_info.append(f"📁 创建目录: {', '.join(directories_created)}")
        
        # 检查是否为 Lua 文件并进行语法检查
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.lua' and content.strip():
            result_info.append("")
            result_info.append("🔍 Lua 语法检查结果:")
            
            try:
                syntax_result = SyntaxChecker.check_syntax(content, "lua")
                
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
        elif file_extension == '.lua' and not content.strip():
            result_info.append("")
            result_info.append("ℹ️ 空的 Lua 文件，跳过语法检查")
        
        return "\n".join(result_info)
        
    except Exception as e:
        return f"创建文件时发生未知错误: {str(e)}"
