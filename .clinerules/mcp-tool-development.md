## Brief overview
这些规则专门针对 MCP (Model Context Protocol) 服务器工具开发，确保工具方法的标准化描述、参数规范化和异常处理的最佳实践。

## 工具方法文档规范
- 所有工具方法必须使用三个双引号（"""）包裹方法描述
- 方法描述应该清晰说明工具的功能、用途和预期行为
- 描述格式应遵循标准的 Python docstring 规范

## 参数处理规范
- 当方法有参数时，必须使用 `Annotated` 类型注解将参数规范化
- 参数注解应包含类型信息和详细的描述说明
- 使用 `Annotated[类型, "参数描述"]` 的格式进行参数标注

## 异常处理要求
- 实现严格的异常处理机制
- 捕获并处理所有可能的异常情况
- 提供有意义的错误信息和适当的错误响应
- 确保异常不会导致整个 MCP 服务器崩溃

## 代码质量标准
- 遵循 Python PEP 8 编码规范
- 确保代码的可读性和可维护性
- 添加适当的类型提示以提高代码质量
