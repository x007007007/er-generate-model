# x007007007-er-gen-tool-ai

AI Extension for ER Diagram Generator Tool - AI 驱动的 ER 建模插件，为 `er-gen-tool` 添加智能建模功能。

> **Note**: This package is part of the ER monorepo workspace. For workspace development setup, see the [root README](../../README.md) and [DEVELOPMENT.md](../../DEVELOPMENT.md).

## 概述

`er-gen-tool-ai` 是 `er-gen-tool` 的可选插件，提供基于 AI 的 ER 建模功能。安装此插件后，`er-gen-tool` 命令会自动获得 `ai-assist` 子命令，让你可以使用自然语言生成和优化 ER 图。

**核心特性：**

- 🤖 **自然语言生成**: 从需求描述自动生成 TOML 格式的 ER 配置
- 🔄 **智能优化**: 根据修改请求优化现有的 ER 配置
- 💬 **交互式对话**: 通过对话模式逐步完善 ER 模型
- ✅ **自动验证**: 生成的配置自动验证，确保语法正确
- 🔌 **插件架构**: 通过 entry points 自动集成到 `er-gen-tool`

## 安装

### Workspace Installation (Development)

If you're working in the monorepo workspace:

```bash
# From workspace root
uv sync
```

This installs all packages in editable mode, including `er-gen-tool-ai` and its internal dependency `er-gen-core`.

### Standalone Installation

For standalone use outside the workspace:

### 使用 uv（推荐）

```bash
# 安装 AI 插件
uv pip install x007007007-er-gen-tool-ai

# 或者与 er-gen-tool 一起安装
uv pip install x007007007-er-gen-tool[ai]
```

### 使用 pip

```bash
# 安装 AI 插件
uv pip install x007007007-er-gen-tool-ai

# 或者与 er-gen-tool 一起安装
uv pip install x007007007-er-gen-tool[ai]
```

### Internal Dependencies

This package depends on:
- `x007007007-er-gen-core>=0.3.0` - Core ER diagram functionality (required)

This package is used by:
- `x007007007-er-gen-tool` - Automatically loads as a plugin when installed

In the workspace, internal dependencies are automatically resolved from local packages.

## 配置

### API 密钥

AI 功能需要 DeepSeek API 密钥。你可以通过以下方式配置：

**方式 1: 环境变量**

```bash
export DEEPSEEK_API_KEY=your-api-key-here
```

**方式 2: .env 文件**

在项目根目录创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1  # 可选
```

**方式 3: 命令行参数**

```bash
er-gen-tool ai-assist generate "需求描述" --api-key your-api-key-here
```

## 使用方法

安装插件后，`er-gen-tool` 会自动获得 `ai-assist` 子命令：

```bash
$ er-gen-tool --help
Usage: er-gen-tool [OPTIONS] COMMAND [ARGS]...

Commands:
  ai-assist      AI-powered ER modeling
  convert        Convert ER diagrams
  makemigration  Generate migrations
  migrate        Manage migrations
```

### 1. 生成 ER 模型 (generate)

从自然语言需求生成 TOML 格式的 ER 配置：

```bash
# 基本用法
er-gen-tool ai-assist generate "设计一个博客系统，包含用户、文章、评论和标签"

# 保存到文件
er-gen-tool ai-assist generate "设计一个电商系统" -o ecommerce.toml

# 启用流式输出（实时显示生成过程）
er-gen-tool ai-assist generate "设计一个任务管理系统" --stream

# 从标准输入读取需求
echo "设计一个图书管理系统" | er-gen-tool ai-assist generate
```

**示例输出：**

```toml
[entities.USER]
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "username", type = "string", unique = true},
    {name = "email", type = "string"},
    {name = "created_at", type = "datetime"},
]

[entities.POST]
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "title", type = "string"},
    {name = "content", type = "text"},
    {name = "author_id", type = "int", is_fk = true},
    {name = "created_at", type = "datetime"},
]

[[relationships]]
left = "USER"
right = "POST"
type = "one-to-many"
left_label = "writes"
```

### 2. 优化现有配置 (refine)

根据修改请求优化现有的 TOML 配置：

```bash
# 基本用法
er-gen-tool ai-assist refine existing.toml "添加评论功能"

# 保存到新文件
er-gen-tool ai-assist refine blog.toml "添加点赞和收藏功能" -o blog_v2.toml

# 启用流式输出
er-gen-tool ai-assist refine existing.toml "添加用户权限系统" --stream

# 从标准输入读取修改请求
echo "添加文章分类功能" | er-gen-tool ai-assist refine blog.toml
```

### 3. 交互式对话 (chat)

通过交互式对话逐步完善 ER 模型：

```bash
# 启动交互模式
er-gen-tool ai-assist chat existing.toml

# 保存最终结果到文件
er-gen-tool ai-assist chat blog.toml -o blog_final.toml
```

**交互示例：**

```
Interactive TOML refinement mode. Type your modification requests.
Type 'quit' or 'exit' to finish and save.
============================================================

Modification request: 添加评论功能
Refining TOML configuration...

--- Updated TOML ---
[entities.COMMENT]
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "content", type = "text"},
    ...
]
--- End of TOML ---

Modification request: 添加点赞功能
Refining TOML configuration...
...

Modification request: quit
Final TOML saved to: blog_final.toml
```

## 插件系统工作原理

`er-gen-tool-ai` 使用 Python entry points 机制自动注册到 `er-gen-tool`：

### 1. 插件注册

在 `pyproject.toml` 中声明 entry point：

```toml
[project.entry-points."er_gen_tool.plugins"]
ai-assist = "x007007007.er_tool_ai.cli_plugin:ai_assist_cmd"
```

### 2. 自动发现

`er-gen-tool` 在启动时自动发现并加载所有已安装的插件：

```python
from importlib.metadata import entry_points

# 自动发现插件
plugin_eps = entry_points(group='er_gen_tool.plugins')
for ep in plugin_eps:
    plugin_cmd = ep.load()
    main.add_command(plugin_cmd, name=ep.name)
```

### 3. 无缝集成

- ✅ 安装插件后，`ai-assist` 命令自动可用
- ✅ 卸载插件后，命令自动消失
- ✅ 无需修改 `er-gen-tool` 核心代码
- ✅ 支持多个插件同时安装

## 命令选项

### generate 命令

```bash
er-gen-tool ai-assist generate [REQUIREMENT] [OPTIONS]
```

**参数：**
- `REQUIREMENT`: 需求描述（可选，可从 stdin 读取）

**选项：**
- `--api-key TEXT`: DeepSeek API 密钥（或设置 DEEPSEEK_API_KEY 环境变量）
- `-o, --output PATH`: 输出文件路径
- `--stream/--no-stream`: 启用/禁用流式输出（默认：禁用）
- `--max-retries INTEGER`: 验证失败时的最大重试次数（默认：3）

### refine 命令

```bash
er-gen-tool ai-assist refine EXISTING_TOML_FILE [MODIFICATION_REQUEST] [OPTIONS]
```

**参数：**
- `EXISTING_TOML_FILE`: 现有的 TOML 配置文件（必需）
- `MODIFICATION_REQUEST`: 修改请求（可选，可从 stdin 读取）

**选项：**
- `--api-key TEXT`: DeepSeek API 密钥
- `-o, --output PATH`: 输出文件路径
- `--stream/--no-stream`: 启用/禁用流式输出
- `--max-retries INTEGER`: 最大重试次数

### chat 命令

```bash
er-gen-tool ai-assist chat EXISTING_TOML_FILE [OPTIONS]
```

**参数：**
- `EXISTING_TOML_FILE`: 现有的 TOML 配置文件（必需）

**选项：**
- `--api-key TEXT`: DeepSeek API 密钥
- `-o, --output PATH`: 输出文件路径
- `--max-retries INTEGER`: 最大重试次数

## 工作流示例

### 完整的 ER 建模流程

```bash
# 1. 生成初始模型
er-gen-tool ai-assist generate "设计一个博客系统" -o blog.toml

# 2. 查看生成的配置
cat blog.toml

# 3. 转换为 Django 代码
er-gen-tool convert blog.toml --format django -o models.py

# 4. 优化模型（添加新功能）
er-gen-tool ai-assist refine blog.toml "添加评论和点赞功能" -o blog_v2.toml

# 5. 重新生成代码
er-gen-tool convert blog_v2.toml --format django -o models.py

# 6. 交互式完善（如果需要）
er-gen-tool ai-assist chat blog_v2.toml -o blog_final.toml
```

## 依赖关系

```
er-gen-core (核心库)
    ↑
    │
er-gen-tool-ai (AI 插件)
    ↑
    │ (可选插件)
    │
er-gen-tool (命令行工具)
```

- `er-gen-tool-ai` 依赖 `er-gen-core` 获取核心功能
- `er-gen-tool` 可选依赖 `er-gen-tool-ai` 获取 AI 功能
- 三者可以独立安装和使用

## 开发

### 安装开发依赖

```bash
cd packages/er-gen-tool-ai
uv pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 创建自己的插件

参考 `er-gen-tool-ai` 的实现，你可以创建自己的插件：

1. **创建 Click 命令组**：

```python
import click

@click.group()
def my_plugin_cmd():
    """My custom plugin"""
    pass

@my_plugin_cmd.command()
def my_command():
    """My custom command"""
    click.echo("Hello from my plugin!")
```

2. **在 pyproject.toml 中注册**：

```toml
[project.entry-points."er_gen_tool.plugins"]
my-plugin = "my_package.cli_plugin:my_plugin_cmd"
```

3. **安装插件**：

```bash
uv pip install my-plugin-package
```

4. **使用插件**：

```bash
er-gen-tool my-plugin my-command
```

## 许可证

MIT License

## 相关项目

- [er-gen-core](https://github.com/x007007007/er-gen-core) - 核心库
- [er-gen-tool](https://github.com/x007007007/er-gen-tool) - 命令行工具
- [er-gen-mcp](https://github.com/x007007007/er-gen-mcp) - MCP 服务器
