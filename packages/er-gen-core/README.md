# x007007007-er-gen-core

ER Diagram Core Library - 核心功能库，提供 ER 图解析、渲染和转换功能。

> **Note**: This package is part of the ER monorepo workspace. For workspace development setup, see the [root README](../../README.md) and [DEVELOPMENT.md](../../DEVELOPMENT.md).

## 概述

`er-gen-core` 是 ER 图生成工具的核心库，包含所有共享功能，不包含 CLI 或 AI 依赖。这个包被 `er-gen-tool` 和 `er-gen-mcp` 使用，提供：

- **解析器 (Parsers)**: 支持 Mermaid、PlantUML、TOML 和数据库模式解析
- **渲染器 (Renderers)**: 生成 Django 和 SQLAlchemy 代码
- **转换器 (Converters)**: 在不同 ER 图格式之间转换
- **模型 (Models)**: 统一的 ER 图数据模型

## 安装

### Workspace Installation (Development)

If you're working in the monorepo workspace:

```bash
# From workspace root
uv sync
```

This installs all packages in editable mode with their dependencies.

### Standalone Installation

For standalone use outside the workspace:

```bash
pip install x007007007-er-gen-core
```

### Internal Dependencies

This is a core package with no internal dependencies. It is used by:
- `x007007007-er-gen-tool` - CLI tool
- `x007007007-er-gen-mcp` - MCP server
- `x007007007-er-gen-tool-ai` - AI extension

## 核心功能

### 1. 解析器 (Parsers)

支持多种输入格式：

- **Mermaid**: 解析 Mermaid ER 图语法
- **PlantUML**: 解析 PlantUML ER 图语法
- **TOML**: 解析 TOML 配置文件
- **Database**: 从现有数据库模式解析

### 2. 渲染器 (Renderers)

生成 Python ORM 代码：

- **DjangoRenderer**: 生成 Django Models
- **SQLAlchemyRenderer**: 生成 SQLAlchemy Models

### 3. 转换器 (Converters)

在不同格式之间转换：

- **MermaidConverter**: 转换为 Mermaid ER 图
- **PlantUMLConverter**: 转换为 PlantUML ER 图

### 4. 数据模型 (Models)

统一的 ER 图数据模型，包括：

- `ERModel`: ER 图模型
- `Entity`: 实体定义
- `Field`: 字段定义
- `Relationship`: 关系定义

## 基本使用

### 解析 TOML 并生成 Django 代码

```python
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers import DjangoRenderer

# 解析 TOML 文件
parser = TomlERParser()
with open('model.toml', 'r') as f:
    er_model = parser.parse(f.read())

# 渲染为 Django 代码
renderer = DjangoRenderer(app_label='myapp')
django_code = renderer.render(er_model)
print(django_code)
```

### 解析 Mermaid 并转换为 PlantUML

```python
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.converters import PlantUMLConverter

# 解析 Mermaid
parser = MermaidAntlrParser()
with open('diagram.mmd', 'r') as f:
    er_model = parser.parse(f.read())

# 转换为 PlantUML
converter = PlantUMLConverter()
plantuml_code = converter.convert(er_model)
print(plantuml_code)
```

### 从数据库解析并生成 SQLAlchemy 代码

```python
from x007007007.er.db_parser import DatabaseParser
from x007007007.er.renderers import SQLAlchemyRenderer

# 从数据库解析
parser = DatabaseParser('postgresql://user:pass@localhost/dbname')
er_model = parser.parse()

# 渲染为 SQLAlchemy 代码
renderer = SQLAlchemyRenderer()
sqlalchemy_code = renderer.render(er_model)
print(sqlalchemy_code)
```

## 依赖关系

这是一个核心库，被以下包使用：

- **er-gen-tool**: 命令行工具，提供 `convert`、`ai-assist`、`makemigration` 和 `migrate` 命令
- **er-gen-mcp**: MCP 服务器，提供 Model Context Protocol 接口

这两个包都依赖 `er-gen-core`，但互不依赖。

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 许可证

MIT License

## 相关项目

- [er-gen-tool](https://github.com/x007007007/er-gen-tool) - 命令行工具
- [er-gen-mcp](https://github.com/x007007007/er-gen-mcp) - MCP 服务器
