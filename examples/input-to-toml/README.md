# Input to TOML Examples

本目录包含从其他格式转换为 TOML 格式的示例。

## 概述

TOML 是一种简洁、易读的配置文件格式，可以作为数据模型定义的中间格式。本目录展示如何将不同来源的数据模型转换为 TOML 格式。

## 支持的输入格式

- **[Mermaid ER 图](mermaid-to-toml/)** - 从 Mermaid ER 图转换为 TOML
- **[Django 模型](django-to-toml/)** - 从 Django ORM 模型转换为 TOML

## 为什么转换为 TOML？

将数据模型转换为 TOML 格式有以下优势：

1. **平台无关** - TOML 是中立的配置格式，不依赖特定框架
2. **易于编辑** - 纯文本格式，可以用任何编辑器修改
3. **版本控制友好** - 适合 Git 等版本控制系统
4. **可再转换** - 可以从 TOML 转换为其他平台的代码
5. **文档化** - 可以作为数据模型的文档

## 使用场景

### 从 Mermaid 转 TOML

适用于：
- 已有 Mermaid ER 图，想要生成代码
- 使用可视化工具设计数据模型
- 需要将图表转换为可执行代码

示例：
```bash
uv run er-gen-tool convert convert input.mmd -t mermaid -o output.toml
```

### 从 Django 转 TOML

适用于：
- 已有 Django 项目，想要导出模型定义
- 需要将 Django 模型迁移到其他平台
- 想要生成数据模型文档

示例：
```bash
# 注意：当前工具可能不直接支持 Django 到 TOML 的转换
# 此示例展示了预期的 TOML 输出格式
```

## 示例列表

### Mermaid to TOML

- **[01-simple-blog](mermaid-to-toml/01-simple-blog/)** - 简单的博客系统模型
- **[02-file-upload-system](mermaid-to-toml/02-file-upload-system/)** - 复杂的文件上传系统

### Django to TOML

- **[blog-app](django-to-toml/blog-app/)** - Django 博客应用模型

## TOML 输出格式

转换后的 TOML 文件包含：

### 实体定义

```toml
[entities.EntityName]
comment = "实体描述"
columns = [
    {name = "id", type = "int", is_pk = true, comment = "主键"},
    {name = "name", type = "string", unique = true},
]
```

### 关系定义

```toml
[[relationships]]
left_entity = "User"
right_entity = "Post"
relation_type = "one-to-many"
right_column = "author_id"
```

## 工作流程

典型的工作流程：

1. **设计阶段** - 使用 Mermaid 或其他工具设计数据模型
2. **转换为 TOML** - 将设计转换为 TOML 格式
3. **编辑和完善** - 在 TOML 中添加更多细节
4. **生成代码** - 从 TOML 生成目标平台的代码

```
Mermaid ER → TOML → Django/SQLAlchemy/etc.
Django Models → TOML → Mermaid/SQLAlchemy/etc.
```

## 注意事项

- 转换过程中可能会丢失一些平台特定的特性
- 建议在转换后检查和完善 TOML 文件
- TOML 文件应该包含一个 namespace（通常从文件名推断）

## 相关示例

- 如果你想从 TOML 转换为其他格式，查看 [../toml-to-output/](../toml-to-output/)
- 如果你想了解完整的项目示例，查看 [../full-projects/](../full-projects/)
