# TOML to Output Examples

本目录包含从 TOML 格式转换为各种输出格式的示例。

## 概述

TOML 是一种简洁、易读的配置文件格式，非常适合定义数据模型。本目录展示如何将 TOML 格式的数据模型定义转换为不同平台的代码或图表。

## 支持的输出平台

- **[Django](django/)** - Django ORM 模型（Python）
- **[SQLAlchemy](sqlalchemy/)** - SQLAlchemy ORM 模型（Python）
- **[Mermaid](mermaid/)** - Mermaid ER 图（可视化）

## 示例场景

每个平台包含三个示例，按复杂度递增：

### 01-simple-model
最简单的单表模型，适合入门学习。包含基本字段类型和主键定义。

### 02-relationships
包含多个表和关系的模型，展示外键和一对多关系。

### 03-all-data-types
完整的数据类型展示，包含所有支持的字段类型（字符串、数值、布尔、日期时间、特殊类型等）。

## 使用方法

### 基本转换命令

```bash
# 转换为 Django 模型
uv run er-convert convert <input.toml> -f django -d <output_dir>/

# 转换为 SQLAlchemy 模型
uv run er-convert convert <input.toml> -f sqlalchemy -d <output_dir>/

# 转换为 Mermaid ER 图
uv run er-convert convert <input.toml> -f mermaid -o <output.mmd>
```

### 示例

```bash
# Django 简单模型
uv run er-convert convert django/01-simple-model/input.toml \
  -f django \
  -d django/01-simple-model/output/

# SQLAlchemy 关系模型
uv run er-convert convert sqlalchemy/02-relationships/input.toml \
  -f sqlalchemy \
  -d sqlalchemy/02-relationships/output/

# Mermaid 完整数据类型
uv run er-convert convert mermaid/03-all-data-types/input.toml \
  -f mermaid \
  -o mermaid/03-all-data-types/output.mmd
```

## TOML 格式说明

### 基本结构

```toml
# 定义实体
[entities.EntityName]
comment = "实体描述"
columns = [
    {name = "id", type = "int", is_pk = true, comment = "主键"},
    {name = "name", type = "string", unique = true, comment = "名称"},
]

# 定义关系
[[relationships]]
left_entity = "User"
right_entity = "Post"
relation_type = "one-to-many"
right_column = "author_id"
```

### 字段属性

- `name` - 字段名称（必需）
- `type` - 数据类型（必需）
- `is_pk` - 是否为主键
- `is_fk` - 是否为外键
- `unique` - 是否唯一
- `nullable` - 是否可为空
- `default` - 默认值
- `max_length` - 最大长度（字符串类型）
- `comment` - 字段注释

## 学习路径

1. 从 `django/01-simple-model` 开始，了解基本的 TOML 结构
2. 学习 `django/02-relationships`，理解如何定义关系
3. 查看 `django/03-all-data-types`，了解所有支持的数据类型
4. 对比不同平台（Django vs SQLAlchemy）的输出差异
5. 使用 Mermaid 输出可视化你的数据模型

## 注意事项

- Django 和 SQLAlchemy 输出为 Python 包结构（包含 `__init__.py` 和 `models.py`）
- Mermaid 输出为单个 `.mmd` 文件
- 所有输出文件都是实际执行转换工具生成的 golden files
- 输入文件使用 `input.toml` 命名，输出使用 `output/` 目录或 `output.mmd` 文件

## 相关示例

- 如果你想从其他格式转换为 TOML，查看 [../input-to-toml/](../input-to-toml/)
- 如果你想了解数据库迁移演进，查看 [../migration-evolution/](../migration-evolution/)
