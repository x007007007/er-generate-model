# ER Converter Examples

本目录包含 ER 转换工具的示例，按照转换场景进行组织，帮助开发者快速理解和使用工具。

## 目录结构

```
examples/
├── toml-to-output/          # TOML 转换为其他格式
│   ├── django/              # 转换为 Django ORM 模型
│   ├── sqlalchemy/          # 转换为 SQLAlchemy ORM 模型
│   └── mermaid/             # 转换为 Mermaid ER 图
├── input-to-toml/           # 其他格式转换为 TOML
│   ├── mermaid-to-toml/     # Mermaid ER 图转 TOML
│   └── django-to-toml/      # Django 模型转 TOML
├── migration-evolution/     # 数据库迁移演进示例
│   ├── 01-initial/          # 初始版本
│   ├── 02-add-email/        # 添加邮箱字段
│   └── ...                  # 8个演进版本
└── full-projects/           # 完整项目示例
    └── django-blog/         # Django 完整项目
```

## 快速导航

### 1. TOML 转换为其他格式

如果你有 TOML 格式的数据模型定义，想要转换为特定平台的代码：

- **[Django ORM](toml-to-output/django/)** - 转换为 Django models.py
- **[SQLAlchemy ORM](toml-to-output/sqlalchemy/)** - 转换为 SQLAlchemy models.py
- **[Mermaid ER 图](toml-to-output/mermaid/)** - 转换为 Mermaid ER 图

每个平台包含多个示例：
- `01-simple-model` - 简单的单表模型
- `02-relationships` - 包含关系的多表模型
- `03-all-data-types` - 展示所有支持的数据类型
- `04-templates-single-file` ⭐ - 单文件模板和继承（SQLAlchemy）
- `05-templates-cross-file` ⭐ - 跨文件模板引用（SQLAlchemy）
- `06-templates-explicit-export` ⭐ - 显式导出路径（SQLAlchemy）

### 2. 其他格式转换为 TOML

如果你想将现有的模型转换为 TOML 格式：

- **[Mermaid 转 TOML](input-to-toml/mermaid-to-toml/)** - 从 Mermaid ER 图生成 TOML
- **[Django 转 TOML](input-to-toml/django-to-toml/)** - 从 Django 模型生成 TOML

### 3. 数据库迁移演进

查看 **[migration-evolution](migration-evolution/)** 目录，了解博客系统从简单到复杂的完整演进过程（8个版本）。

### 4. 完整项目示例

查看 **[full-projects/django-blog](full-projects/django-blog/)** 了解如何在真实 Django 项目中使用转换工具。

## 使用示例

### TOML 转 Django

```bash
# 简单模型示例
uv run er-gen-tool convert convert examples/toml-to-output/django/01-simple-model/input.toml \
  -f django \
  -d examples/toml-to-output/django/01-simple-model/output/

# 关系模型示例
uv run er-gen-tool convert convert examples/toml-to-output/django/02-relationships/input.toml \
  -f django \
  -d examples/toml-to-output/django/02-relationships/output/
```

### TOML 转 SQLAlchemy

```bash
# 简单模型示例
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/01-simple-model/input.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/01-simple-model/output/

# 模板示例（Reference模式）
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/04-templates-single-file/input.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/04-templates-single-file/output/ \
  --inheritance-mode reference

# 跨文件模板引用
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/05-templates-cross-file/entities.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/05-templates-cross-file/output/ \
  --inheritance-mode reference \
  --toml-files examples/toml-to-output/sqlalchemy/05-templates-cross-file/base_templates.toml
```

### TOML 转 Mermaid

```bash
# 简单模型示例
uv run er-gen-tool convert convert examples/toml-to-output/mermaid/01-simple-model/input.toml \
  -f mermaid \
  -o examples/toml-to-output/mermaid/01-simple-model/output.mmd
```

### Mermaid 转 TOML

```bash
# 博客示例
uv run er-gen-tool convert convert examples/input-to-toml/mermaid-to-toml/01-simple-blog/input.mmd \
  -t mermaid \
  -o examples/input-to-toml/mermaid-to-toml/01-simple-blog/output.toml
```

## 学习路径

建议按照以下顺序学习示例：

1. **入门** - 从 `toml-to-output/django/01-simple-model` 开始
2. **关系** - 学习 `02-relationships` 示例
3. **完整功能** - 查看 `03-all-data-types` 了解所有数据类型
4. **模板和继承** ⭐ - 学习 `04-templates-single-file` 了解模板系统
5. **跨文件引用** ⭐ - 学习 `05-templates-cross-file` 了解跨文件模板
6. **反向转换** - 学习 `input-to-toml` 目录下的示例
7. **演进** - 查看 `migration-evolution` 了解数据库迁移
8. **实战** - 研究 `full-projects/django-blog` 完整项目

## 文件命名规范

- **输入文件**: `input.toml` 或 `input.mmd`
- **输出目录**: `output/` (Python 包) 或 `output.mmd` (单文件)
- **示例目录**: 使用数字前缀 (`01-`, `02-`, `03-`) 表示学习顺序

## 旧路径映射

如果你使用的是旧版本的示例路径，请参考以下映射：

| 旧路径 | 新路径 |
|--------|--------|
| `examples/blog_v1.mmd` ~ `blog_v8.mmd` | `examples/migration-evolution/01-initial/` ~ `08-remove-comments/` |
| `examples/all_data_types.mmd` | `examples/toml-to-output/*/03-all-data-types/input.toml` |
| `examples/file_upload_models.mmd` | `examples/input-to-toml/mermaid-to-toml/02-file-upload-system/input.mmd` |
| `examples/django_blog/` | `examples/full-projects/django-blog/` |

## 数据类型支持

所有示例中的 `03-all-data-types` 展示了以下数据类型：

### 字符串类型
- `string` / `varchar` - 可变长度字符串
- `char` - 固定长度字符串
- `text` - 大文本内容

### 数值类型
- `int` / `integer` - 标准整数
- `bigint` - 64位大整数
- `smallint` - 16位小整数
- `float` / `real` - 单精度浮点数
- `double` - 双精度浮点数
- `decimal` / `numeric` - 固定精度小数

### 布尔类型
- `boolean` / `bool` - 真/假值

### 日期时间类型
- `date` - 日期（年月日）
- `time` - 时间（时分秒）
- `datetime` - 日期时间
- `timestamp` - Unix时间戳

### 特殊类型
- `uuid` - 通用唯一标识符
- `json` / `jsonb` - JSON对象
- `file` - 文件字段

## Golden Files

所有示例中的输出文件都是通过实际执行转换工具生成的"golden files"，确保示例的正确性和可靠性。

## 更多信息

- 查看各子目录的 README.md 了解详细说明
- 查看项目根目录的文档了解工具的完整功能
