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

logger = logging.getLogger(__name__)


class SyntaxChecker:
    """
    静态语法检测器类
    提供多种编程语言的语法错误检测功能
    """
    
    _lua_parser: Optional[Parser] = None
    
    @classmethod
    def _get_lua_parser(cls) -> Optional[Parser]:
        """
        获取 Lua 解析器实例（单例模式）
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
    
    @staticmethod
    def check_syntax(
        code: Annotated[str, "要检测的代码字符串"], 
        language: Annotated[str, "编程语言类型，目前支持 'lua'"]
    ) -> Dict[str, Any]:
        """
        检测代码语法错误
        
        Args:
            code: 要检测的代码字符串
            language: 编程语言类型，目前支持 'lua'
            
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
            else:
                return {
                    "has_errors": True,
                    "is_valid": False,
                    "errors": [{
                        "line": 0,
                        "column": 0,
                        "message": f"Unsupported language: {language}. Currently only 'lua' is supported.",
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
    def get_supported_languages() -> List[str]:
        """
        获取支持的编程语言列表
        
        Returns:
            支持的语言列表
        """
        supported = []
        
        if TREE_SITTER_AVAILABLE and LUA_LANGUAGE_AVAILABLE:
            supported.append("lua")
            
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
            依赖库状态字典
        """
        return {
            "tree_sitter": TREE_SITTER_AVAILABLE,
            "tree_sitter_lua": LUA_LANGUAGE_AVAILABLE
        }
