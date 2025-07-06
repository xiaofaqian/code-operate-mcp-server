#!/usr/bin/env python3
"""
XML 语法检测器演示脚本
展示 utils/syntax_checker.py 中的 XML 语法检测功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.syntax_checker import SyntaxChecker

def demo_xml_syntax_checker():
    """演示 XML 语法检测器的功能"""
    
    print("=== XML 语法检测器演示 ===\n")
    
    # 演示用例
    examples = [
        {
            "title": "✓ 正确的 XML 包含注释",
            "xml": """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <!-- 书店库存管理系统 -->
    <book id="1" category="fiction">
        <title>《三体》</title>
        <author>刘慈欣</author>
        <!-- 价格信息 -->
        <price currency="CNY">29.99</price>
    </book>
    <book id="2" category="science">
        <title>《时间简史》</title>
        <author>史蒂芬·霍金</author>
        <price currency="CNY">39.99</price>
    </book>
    <!-- 库存统计：2本书 -->
</bookstore>"""
        },
        {
            "title": "✗ 标签不匹配错误",
            "xml": """<root>
    <item>内容</wrong_tag>
</root>"""
        },
        {
            "title": "✗ 注释包含非法 '--' 序列",
            "xml": """<root>
    <!-- 这里有非法的 -- 序列 -->
    <item>内容</item>
</root>"""
        },
        {
            "title": "✗ 属性值未加引号",
            "xml": """<root>
    <item id=123 name=test>内容</item>
</root>"""
        }
    ]
    
    # 检查系统状态
    print("系统状态:")
    print(f"  支持的语言: {SyntaxChecker.get_supported_languages()}")
    dependency_status = SyntaxChecker.get_dependency_status()
    for dep, available in dependency_status.items():
        status = "✓" if available else "✗"
        print(f"  {dep}: {status}")
    
    print("\n" + "="*60 + "\n")
    
    # 运行演示
    for i, example in enumerate(examples, 1):
        print(f"演示 {i}: {example['title']}")
        print("-" * 40)
        print("XML 代码:")
        print(example['xml'])
        print("\n检测结果:")
        
        # 执行语法检测
        result = SyntaxChecker.check_syntax(example['xml'], 'xml')
        
        if result['has_errors']:
            print("❌ 发现语法错误:")
            for error in result['errors']:
                print(f"   • 第 {error['line']} 行，第 {error['column']} 列: {error['message']}")
                print(f"     错误类型: {error['type']}")
        else:
            print("✅ XML 语法正确，包括注释处理")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    demo_xml_syntax_checker()
