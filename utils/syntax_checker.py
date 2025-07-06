"""
语法检测器工具类
使用 Tree-sitter 库进行代码语法错误检测
"""

import logging
from typing import Dict, List, Any, Optional
from typing_extensions import Annotated

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    tree_sitter = None
    Language = None
    Parser = None

try:
    import tree_sitter_lua
    LUA_LANGUAGE_AVAILABLE = True
except ImportError:
    LUA_LANGUAGE_AVAILABLE = False
    tree_sitter_lua = None

try:
    import tree_sitter_xml
    XML_LANGUAGE_AVAILABLE = True
except ImportError:
    XML_LANGUAGE_AVAILABLE = False
    tree_sitter_xml = None

logger = logging.getLogger(__name__)


class SyntaxChecker:
    """
    静态语法检测器类
    提供多种编程语言的语法错误检测功能
    支持的语言：Lua, XML
    """
    
    _lua_parser: Optional[Parser] = None
    _xml_parser: Optional[Parser] = None
    
    @classmethod
    def _get_lua_parser(cls) -> Optional[Parser]:
        """
        获取 Lua 解析器实例（单例模式）
        
        Returns:
            Parser: Lua 解析器实例，如果初始化失败则返回 None
            
        Note:
            使用单例模式避免重复创建解析器实例，提高性能
            首次调用时会初始化解析器，后续调用直接返回缓存的实例
        """
        if not TREE_SITTER_AVAILABLE or not LUA_LANGUAGE_AVAILABLE:
            return None
            
        if cls._lua_parser is None:
            try:
                # 获取 Lua 语言定义
                lua_language = Language(tree_sitter_lua.language())
                
                # 创建解析器
                cls._lua_parser = Parser(lua_language)
                logger.info("Lua parser initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Lua parser: {e}")
                return None
                
        return cls._lua_parser
    
    @classmethod
    def _get_xml_parser(cls) -> Optional[Parser]:
        """
        获取 XML 解析器实例（单例模式）
        
        Returns:
            Parser: XML 解析器实例，如果初始化失败则返回 None
            
        Note:
            使用单例模式避免重复创建解析器实例，提高性能
            首次调用时会初始化解析器，后续调用直接返回缓存的实例
            XML 解析器能够正确处理 XML 注释、标签匹配等语法结构
        """
        if not TREE_SITTER_AVAILABLE or not XML_LANGUAGE_AVAILABLE:
            return None
            
        if cls._xml_parser is None:
            try:
                # 获取 XML 语言定义
                xml_language = Language(tree_sitter_xml.language_xml())
                
                # 创建解析器
                cls._xml_parser = Parser(xml_language)
                logger.info("XML parser initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize XML parser: {e}")
                return None
                
        return cls._xml_parser
    
    @staticmethod
    def check_syntax(
        code: Annotated[str, "要检测的代码字符串"], 
        language: Annotated[str, "编程语言类型，目前支持 'lua', 'xml'"]
    ) -> Dict[str, Any]:
        """
        检测代码语法错误
        
        Args:
            code: 要检测的代码字符串
            language: 编程语言类型，目前支持 'lua', 'xml'
            
        Returns:
            包含检测结果的字典，格式如下：
            {
                "has_errors": bool,           # 是否有语法错误
                "is_valid": bool,             # 代码是否有效
                "errors": [                   # 错误列表
                    {
                        "line": int,          # 错误行号（从1开始）
                        "column": int,        # 错误列号（从1开始）
                        "message": str,       # 错误描述
                        "type": str,          # 错误类型
                        "node_type": str      # 错误节点类型
                    }
                ],
                "language": str,              # 检测的语言
                "available": bool             # Tree-sitter 是否可用
            }
        """
        try:
            # 检查依赖是否可用
            if not TREE_SITTER_AVAILABLE:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": "Tree-sitter library is not available. Please install: pip install tree-sitter",
                        "type": "dependency_error",
                        "node_type": "missing_dependency"
                    }],
                    "language": language,
                    "available": False
                }
            
            # 根据语言类型调用相应的检测方法
            if language.lower() == "lua":
                return SyntaxChecker.check_lua_syntax(code)
            elif language.lower() == "xml":
                return SyntaxChecker.check_xml_syntax(code)
            else:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": f"Unsupported language: {language}. Currently supported: 'lua', 'xml'.",
                        "type": "unsupported_language",
                        "node_type": "language_error"
                    }],
                    "language": language,
                    "available": True
                }
                
        except Exception as e:
            logger.error(f"Error in syntax checking: {e}")
            return {
                "has_errors": True,
                "is_valid": False,
                "errors": [{
                    "line": 0,
                    "column": 0,
                    "message": f"Internal error during syntax checking: {str(e)}",
                    "type": "internal_error",
                    "node_type": "exception"
                }],
                "language": language,
                "available": TREE_SITTER_AVAILABLE
            }
    
    @staticmethod
    def check_lua_syntax(code: Annotated[str, "要检测的 Lua 代码字符串"]) -> Dict[str, Any]:
        """
        检测 Lua 代码语法错误
        
        Args:
            code: 要检测的 Lua 代码字符串
            
        Returns:
            包含检测结果的字典
        """
        try:
            # 检查 Lua 解析器是否可用
            if not LUA_LANGUAGE_AVAILABLE:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": "Tree-sitter Lua language is not available. Please install: pip install tree-sitter-lua",
                        "type": "dependency_error",
                        "node_type": "missing_lua_parser"
                    }],
                    "language": "lua",
                    "available": False
                }
            
            # 获取 Lua 解析器
            parser = SyntaxChecker._get_lua_parser()
            if parser is None:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": "Failed to initialize Lua parser",
                        "type": "parser_error",
                        "node_type": "initialization_error"
                    }],
                    "language": "lua",
                    "available": False
                }
            
            # 解析代码
            code_bytes = code.encode('utf-8')
            tree = parser.parse(code_bytes)
            
            # 检查语法错误
            errors = []
            has_errors = False
            
            # 遍历语法树查找错误节点
            def find_errors(node, code_lines):
                nonlocal has_errors
                
                # 检查是否是错误节点
                if node.type == "ERROR":
                    has_errors = True
                    start_point = node.start_point
                    end_point = node.end_point
                    
                    # 获取错误的文本内容
                    error_text = ""
                    if start_point[0] < len(code_lines):
                        line = code_lines[start_point[0]]
                        if start_point[1] < len(line):
                            error_text = line[start_point[1]:end_point[1]] if end_point[0] == start_point[0] else line[start_point[1]:]
                    
                    errors.append({
                        "line": start_point[0] + 1,  # Tree-sitter 行号从0开始，转换为从1开始
                        "column": start_point[1] + 1,  # Tree-sitter 列号从0开始，转换为从1开始
                        "message": f"Syntax error at line {start_point[0] + 1}, column {start_point[1] + 1}" + (f": '{error_text}'" if error_text.strip() else ""),
                        "type": "syntax_error",
                        "node_type": "ERROR"
                    })
                
                # 检查是否有缺失的节点
                if node.is_missing:
                    has_errors = True
                    start_point = node.start_point
                    errors.append({
                        "line": start_point[0] + 1,
                        "column": start_point[1] + 1,
                        "message": f"Missing {node.type} at line {start_point[0] + 1}, column {start_point[1] + 1}",
                        "type": "missing_node",
                        "node_type": node.type
                    })
                
                # 检查特定的语法问题
                if node.type in ["binary_expression", "unary_expression"]:
                    # 检查二元表达式是否完整
                    if node.type == "binary_expression" and len(node.children) < 3:
                        has_errors = True
                        start_point = node.start_point
                        errors.append({
                            "line": start_point[0] + 1,
                            "column": start_point[1] + 1,
                            "message": f"Incomplete binary expression at line {start_point[0] + 1}, column {start_point[1] + 1}",
                            "type": "incomplete_expression",
                            "node_type": "binary_expression"
                        })
                
                # 递归检查子节点
                for child in node.children:
                    find_errors(child, code_lines)
            
            # 将代码分割为行，用于错误报告
            code_lines = code.split('\n')
            
            # 开始查找错误
            find_errors(tree.root_node, code_lines)
            
            # 额外检查：如果没有发现明显的语法错误，但根节点包含错误子节点
            if not has_errors and tree.root_node.has_error:
                has_errors = True
                errors.append({
                    "line": 1,
                    "column": 1,
                    "message": "Code contains syntax errors that could not be precisely located",
                    "type": "general_syntax_error",
                    "node_type": "unknown"
                })
            
            return {
                "has_errors": has_errors,
                "is_valid": not has_errors,
                "errors": errors,
                "language": "lua",
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Error in Lua syntax checking: {e}")
            return {
                "has_errors": True,
                "is_valid": False,
                "errors": [{
                    "line": 0,
                    "column": 0,
                    "message": f"Internal error during Lua syntax checking: {str(e)}",
                    "type": "internal_error",
                    "node_type": "exception"
                }],
                "language": "lua",
                "available": True
            }
    
    @staticmethod
    def check_xml_syntax(code: Annotated[str, "要检测的 XML 代码字符串"]) -> Dict[str, Any]:
        """
        检测 XML 代码语法错误，正确处理 XML 注释
        
        该方法会检测以下 XML 语法问题：
        - 标签匹配错误（开始标签与结束标签不匹配）
        - 属性语法错误（缺少引号、无效字符等）
        - XML 声明错误
        - 文档结构错误
        - 字符编码问题
        - 命名空间相关错误
        - 注释相关错误（未闭合注释、注释内容非法等）
        
        支持的 XML 注释格式：
        - 单行注释：<!-- 这是注释 -->
        - 多行注释：<!-- 这是
                        多行注释 -->
        - 元素间注释：<root><!-- 注释 --><item/></root>
        
        Args:
            code: 要检测的 XML 代码字符串
            
        Returns:
            Dict[str, Any]: 包含检测结果的字典，格式与其他语言检测器一致
            
        Example:
            >>> checker = SyntaxChecker()
            >>> result = checker.check_xml_syntax('<root><item>content</root>')
            >>> print(result['has_errors'])  # True (标签不匹配)
            
            >>> result = checker.check_xml_syntax('<root><!-- 注释 --><item/></root>')
            >>> print(result['has_errors'])  # False (正确的 XML 包含注释)
        """
        try:
            # 检查 XML 解析器是否可用
            if not XML_LANGUAGE_AVAILABLE:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": "Tree-sitter XML language is not available. Please install: pip install tree-sitter-xml",
                        "type": "dependency_error",
                        "node_type": "missing_xml_parser"
                    }],
                    "language": "xml",
                    "available": False
                }
            
            # 获取 XML 解析器
            parser = SyntaxChecker._get_xml_parser()
            if parser is None:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": "Failed to initialize XML parser",
                        "type": "parser_error",
                        "node_type": "initialization_error"
                    }],
                    "language": "xml",
                    "available": False
                }
            
            # 解析代码
            code_bytes = code.encode('utf-8')
            tree = parser.parse(code_bytes)
            
            # 检查语法错误
            errors = []
            has_errors = False
            
            # 遍历语法树查找错误节点
            def find_xml_errors(node, code_lines):
                nonlocal has_errors
                
                # 检查是否是错误节点
                if node.type == "ERROR":
                    has_errors = True
                    start_point = node.start_point
                    end_point = node.end_point
                    
                    # 获取错误的文本内容
                    error_text = ""
                    if start_point[0] < len(code_lines):
                        line = code_lines[start_point[0]]
                        if start_point[1] < len(line):
                            error_text = line[start_point[1]:end_point[1]] if end_point[0] == start_point[0] else line[start_point[1]:]
                    
                    errors.append({
                        "line": start_point[0] + 1,  # Tree-sitter 行号从0开始，转换为从1开始
                        "column": start_point[1] + 1,  # Tree-sitter 列号从0开始，转换为从1开始
                        "message": f"XML syntax error at line {start_point[0] + 1}, column {start_point[1] + 1}" + (f": '{error_text}'" if error_text.strip() else ""),
                        "type": "syntax_error",
                        "node_type": "ERROR"
                    })
                
                # 检查是否有缺失的节点
                if node.is_missing:
                    has_errors = True
                    start_point = node.start_point
                    errors.append({
                        "line": start_point[0] + 1,
                        "column": start_point[1] + 1,
                        "message": f"Missing {node.type} at line {start_point[0] + 1}, column {start_point[1] + 1}",
                        "type": "missing_node",
                        "node_type": node.type
                    })
                
                # 检查 XML 特定的语法问题
                if node.type == "element":
                    # 检查元素标签是否匹配
                    start_tag = None
                    end_tag = None
                    
                    for child in node.children:
                        if child.type == "start_tag":
                            start_tag = child
                        elif child.type == "end_tag":
                            end_tag = child
                    
                    # 如果有开始标签但没有结束标签（对于非自闭合标签）
                    if start_tag and not end_tag:
                        # 检查是否是自闭合标签
                        start_tag_text = code_bytes[start_tag.start_byte:start_tag.end_byte].decode('utf-8', errors='ignore')
                        if not start_tag_text.endswith('/>'):
                            has_errors = True
                            start_point = start_tag.start_point
                            errors.append({
                                "line": start_point[0] + 1,
                                "column": start_point[1] + 1,
                                "message": f"Unclosed tag at line {start_point[0] + 1}, column {start_point[1] + 1}",
                                "type": "unclosed_tag",
                                "node_type": "element"
                            })
                
                # 检查注释相关的错误
                elif node.type == "comment":
                    # 获取注释内容
                    comment_text = code_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
                    
                    # 检查注释是否正确闭合
                    if not comment_text.startswith('<!--') or not comment_text.endswith('-->'):
                        has_errors = True
                        start_point = node.start_point
                        errors.append({
                            "line": start_point[0] + 1,
                            "column": start_point[1] + 1,
                            "message": f"Malformed comment at line {start_point[0] + 1}, column {start_point[1] + 1}",
                            "type": "malformed_comment",
                            "node_type": "comment"
                        })
                    
                    # 检查注释内容中是否包含非法的 '--' 序列
                    comment_content = comment_text[4:-3]  # 去掉 <!-- 和 -->
                    if '--' in comment_content:
                        has_errors = True
                        start_point = node.start_point
                        errors.append({
                            "line": start_point[0] + 1,
                            "column": start_point[1] + 1,
                            "message": f"Invalid '--' sequence in comment content at line {start_point[0] + 1}, column {start_point[1] + 1}",
                            "type": "invalid_comment_content",
                            "node_type": "comment"
                        })
                
                # 检查属性相关的错误
                elif node.type == "attribute":
                    # 检查属性值是否正确引用
                    attribute_text = code_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
                    
                    # 简单检查属性值是否有引号
                    if '=' in attribute_text:
                        parts = attribute_text.split('=', 1)
                        if len(parts) == 2:
                            value_part = parts[1].strip()
                            if not ((value_part.startswith('"') and value_part.endswith('"')) or 
                                   (value_part.startswith("'") and value_part.endswith("'"))):
                                has_errors = True
                                start_point = node.start_point
                                errors.append({
                                    "line": start_point[0] + 1,
                                    "column": start_point[1] + 1,
                                    "message": f"Unquoted attribute value at line {start_point[0] + 1}, column {start_point[1] + 1}",
                                    "type": "unquoted_attribute",
                                    "node_type": "attribute"
                                })
                
                # 递归检查子节点
                for child in node.children:
                    find_xml_errors(child, code_lines)
            
            # 将代码分割为行，用于错误报告
            code_lines = code.split('\n')
            
            # 开始查找错误
            find_xml_errors(tree.root_node, code_lines)
            
            # 额外检查：如果没有发现明显的语法错误，但根节点包含错误子节点
            if not has_errors and tree.root_node.has_error:
                has_errors = True
                errors.append({
                    "line": 1,
                    "column": 1,
                    "message": "XML contains syntax errors that could not be precisely located",
                    "type": "general_syntax_error",
                    "node_type": "unknown"
                })
            
            return {
                "has_errors": has_errors,
                "is_valid": not has_errors,
                "errors": errors,
                "language": "xml",
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Error in XML syntax checking: {e}")
            return {
                "has_errors": True,
                "is_valid": False,
                "errors": [{
                    "line": 0,
                    "column": 0,
                    "message": f"Internal error during XML syntax checking: {str(e)}",
                    "type": "internal_error",
                    "node_type": "exception"
                }],
                "language": "xml",
                "available": True
            }
    
    @staticmethod
    def get_supported_languages() -> List[str]:
        """
        获取支持的编程语言列表
        
        Returns:
            支持的语言列表，包括 'lua' 和 'xml'（如果相应的依赖库可用）
        """
        supported = []
        
        if TREE_SITTER_AVAILABLE and LUA_LANGUAGE_AVAILABLE:
            supported.append("lua")
        
        if TREE_SITTER_AVAILABLE and XML_LANGUAGE_AVAILABLE:
            supported.append("xml")
            
        return supported
    
    @staticmethod
    def is_available() -> bool:
        """
        检查 Tree-sitter 是否可用
        
        Returns:
            True 如果 Tree-sitter 可用，否则 False
        """
        return TREE_SITTER_AVAILABLE
    
    @staticmethod
    def get_dependency_status() -> Dict[str, bool]:
        """
        获取依赖库的状态
        
        Returns:
            依赖库状态字典，包含所有支持的语言解析器状态
            - tree_sitter: Tree-sitter 核心库是否可用
            - tree_sitter_lua: Lua 语言解析器是否可用
            - tree_sitter_xml: XML 语言解析器是否可用
        """
        return {
            "tree_sitter": TREE_SITTER_AVAILABLE,
            "tree_sitter_lua": LUA_LANGUAGE_AVAILABLE,
            "tree_sitter_xml": XML_LANGUAGE_AVAILABLE
        }
