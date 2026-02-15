# x007007007-er-gen-mcp

ER Diagram Converter MCP Server - 独立的 MCP 服务器，为 AI 助手提供 ER 图转换能力。

> **Note**: This package is part of the ER monorepo workspace. For workspace development setup, see the [root README](../../README.md) and [DEVELOPMENT.md](../../DEVELOPMENT.md).

## 概述

`er-gen-mcp` 是一个独立的 MCP (Model Context Protocol) 服务器，通过标准化的协议为 AI 助手（如 Claude、Kiro 等）提供 ER 图解析、转换和验证功能。

**核心特性：**

- 🔄 **格式转换**: 支持 Mermaid、PlantUML、TOML、数据库连接等多种输入格式
- 🎯 **代码生成**: 生成 Django 或 SQLAlchemy ORM 代码
- 📊 **模型解析**: 解析 ER 图并返回结构化的模型数据
- ✅ **模型验证**: 验证 ER 模型的正确性
- 🔌 **标准协议**: 基于 MCP 协议，与任何支持 MCP 的 AI 助手无缝集成

## 安装

### Workspace Installation (Development)

If you're working in the monorepo workspace:

```bash
# From workspace root
uv sync
```

This installs all packages in editable mode, including `er-gen-mcp` and its internal dependency `er-gen-core`.

### Standalone Installation

For standalone use outside the workspace:

### 使用 uv（推荐）

```bash
# 安装 MCP 服务器
uv pip install x007007007-er-gen-mcp
```

### 使用 pip

```bash
# 安装 MCP 服务器
uv pip install x007007007-er-gen-mcp
```

### Internal Dependencies

This package depends on:
- `x007007007-er-gen-core>=0.3.0` - Core ER diagram functionality (required)

In the workspace, this dependency is automatically resolved from the local package.

## 配置

### 在 Kiro 中使用

在 Kiro 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "er-diagram-converter": {
      "command": "er-gen-mcp"
    }
  }
}
```

### 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加（`~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "er-diagram-converter": {
      "command": "er-gen-mcp"
    }
  }
}
```

### 调试模式

启用详细日志输出：

```bash
# 设置环境变量
export MCP_DEBUG=1
export MCP_LOG_LEVEL=DEBUG

# 启动服务器
er-gen-mcp
```

## MCP 工具

服务器提供以下 4 个工具：

### 1. convert_er_diagram

转换 ER 图到不同格式（代码或图表）。

**输入参数：**

- `content` (必需): ER 图内容或文件路径
- `input_type` (可选): 输入格式，可选值：`mermaid`、`plantuml`、`toml`、`db`（默认：`mermaid`）
- `output_format` (可选): 输出格式，可选值：`django`、`sqlalchemy`、`mermaid`、`plantuml`（默认：`django`）
- `app_label` (可选): Django app 标签（仅用于 Django 输出）
- `table_prefix` (可选): 表名前缀

**示例：**

```json
{
  "content": "erDiagram\n  USER ||--o{ POST : writes\n  USER {\n    int id PK\n    string username\n  }",
  "input_type": "mermaid",
  "output_format": "django",
  "app_label": "blog"
}
```

### 2. parse_er_diagram

解析 ER 图并返回结构化的模型数据（JSON 格式）。

**输入参数：**

- `content` (必需): ER 图内容或文件路径
- `input_type` (可选): 输入格式，可选值：`mermaid`、`plantuml`、`toml`、`db`（默认：`mermaid`）

**返回：** JSON 格式的 ER 模型，包含实体和关系信息。

**示例：**

```json
{
  "content": "erDiagram\n  USER ||--o{ POST : writes",
  "input_type": "mermaid"
}
```

### 3. render_er_model

将 ER 模型（JSON 格式）渲染为代码（Django 或 SQLAlchemy）。

**输入参数：**

- `model_json` (必需): ER 模型的 JSON 字符串
- `output_format` (必需): 输出格式，可选值：`django`、`sqlalchemy`
- `app_label` (可选): Django app 标签（仅用于 Django 输出，默认：`app`）
- `table_prefix` (可选): 表名前缀

**示例：**

```json
{
  "model_json": "{\"entities\": {...}, \"relationships\": [...]}",
  "output_format": "django",
  "app_label": "myapp"
}
```

### 4. validate_er_model

验证 ER 模型的正确性，返回验证结果和错误信息。

**输入参数：**

- `model_json` (必需): ER 模型的 JSON 字符串

**返回：** JSON 格式的验证结果：

```json
{
  "valid": true,
  "errors": []
}
```

**示例：**

```json
{
  "model_json": "{\"entities\": {...}, \"relationships\": [...]}"
}
```

## 使用示例

### 在 AI 助手中使用

当 MCP 服务器配置完成后，AI 助手可以直接调用这些工具：

**示例 1: 转换 Mermaid 到 Django**

```
用户: 请将这个 Mermaid ER 图转换为 Django 模型：

erDiagram
  USER ||--o{ POST : writes
  USER {
    int id PK
    string username
    string email
  }
  POST {
    int id PK
    string title
    text content
    int author_id FK
  }

AI: 我会使用 convert_er_diagram 工具来转换...
[调用 MCP 工具]
```

**示例 2: 解析并验证 ER 图**

```
用户: 请解析这个 TOML 配置并验证是否正确

AI: 我会先解析配置，然后验证模型...
[调用 parse_er_diagram 和 validate_er_model 工具]
```

### 命令行测试

虽然 MCP 服务器主要用于 AI 助手集成，但你也可以通过标准输入测试：

```bash
# 启动服务器
er-gen-mcp

# 发送 JSON-RPC 请求（在另一个终端）
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | er-gen-mcp
```

## 支持的格式

### 输入格式

- **Mermaid**: Mermaid ER 图语法
  ```
  erDiagram
    USER ||--o{ POST : writes
  ```

- **PlantUML**: PlantUML ER 图语法
  ```
  @startuml
  entity USER {
    * id : int
  }
  @enduml
  ```

- **TOML**: TOML 配置格式
  ```toml
  [entities.USER]
  columns = [
    {name = "id", type = "int", is_pk = true}
  ]
  ```

- **Database**: 数据库连接字符串
  ```
  postgresql://user:pass@localhost/dbname
  ```

### 输出格式

- **Django**: Django ORM 模型代码
- **SQLAlchemy**: SQLAlchemy ORM 模型代码
- **Mermaid**: Mermaid ER 图
- **PlantUML**: PlantUML ER 图

## 工作流示例

### 完整的 ER 建模流程（通过 AI 助手）

1. **解析现有数据库**：
   ```
   用户: 请连接到我的数据库并解析 ER 模型
   AI: [调用 parse_er_diagram，input_type="db"]
   ```

2. **转换为 Mermaid 图**：
   ```
   用户: 将解析的模型转换为 Mermaid 图
   AI: [调用 render_er_model 或 convert_er_diagram]
   ```

3. **验证模型**：
   ```
   用户: 验证这个模型是否正确
   AI: [调用 validate_er_model]
   ```

4. **生成 Django 代码**：
   ```
   用户: 生成 Django 模型代码
   AI: [调用 convert_er_diagram，output_format="django"]
   ```

## 依赖关系

```
er-gen-core (核心库)
    ↑
    │
er-gen-mcp (MCP 服务器)
```

- `er-gen-mcp` 依赖 `er-gen-core` 获取核心解析和转换功能
- `er-gen-mcp` 独立于 `er-gen-tool`，可以单独安装和使用
- 适合集成到 AI 助手中，无需安装完整的命令行工具

## 协议规范

`er-gen-mcp` 实现了 MCP (Model Context Protocol) 规范：

- **协议版本**: 2024-11-05
- **传输方式**: stdio（标准输入/输出）
- **消息格式**: JSON-RPC 2.0

### 支持的 MCP 方法

- `initialize`: 初始化服务器
- `tools/list`: 列出所有可用工具
- `tools/call`: 调用指定工具
- `ping`: 健康检查

## 故障排除

### 服务器无法启动

检查 Python 版本和依赖：

```bash
^uv run python --version  # 需要 >= 3.8
uv pip list | grep x007007007-er-gen
```

### 工具调用失败

启用调试模式查看详细日志：

```bash
export MCP_DEBUG=1
er-gen-mcp
```

### 解析错误

确保输入格式正确：

- Mermaid: 使用 `erDiagram` 关键字
- PlantUML: 使用 `@startuml` 和 `@enduml`
- TOML: 遵循 TOML 语法规范

## 开发

### 安装开发依赖

```bash
cd packages/er-gen-mcp
uv pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 添加新工具

1. 在 `server.py` 中实现工具方法
2. 在 `_handle_tools_list` 中注册工具
3. 在 `_handle_tool_call` 中添加调用逻辑

## 许可证

MIT License

## 相关项目

- [er-gen-core](https://github.com/x007007007/er-gen-core) - 核心库
- [er-gen-tool](https://github.com/x007007007/er-gen-tool) - 命令行工具
- [er-gen-tool-ai](https://github.com/x007007007/er-gen-tool-ai) - AI 扩展插件
