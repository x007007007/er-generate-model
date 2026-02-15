# ER Django Integration

Django 插件，用于将 Django models 转换为 ER 图和 ER 迁移系统。

> **Note**: This package is part of the ER monorepo workspace. For workspace development setup, see the [root README](../../README.md) and [DEVELOPMENT.md](../../DEVELOPMENT.md).

## 🎯 功能特性

- ✅ **Django Model → ER 图**: 从 Django models 生成 Mermaid/PlantUML ER 图
- ✅ **Django Model → ER Migration**: 从 Django models 生成 ER 迁移文件
- ✅ **App 命名空间**: Django app 作为迁移命名空间
- ✅ **Management Commands**: 集成到 Django 命令系统
- ✅ **完整的关系支持**: ForeignKey, OneToOneField, ManyToManyField

## 📦 安装

### Workspace Installation (Development)

If you're working in the monorepo workspace:

```bash
# From workspace root
uv sync
```

This installs all packages in editable mode, including `er-django`.

### Standalone Installation

For standalone use outside the workspace:

### 1. 安装包

```bash
pip install x007007007-er-django
```

### 2. 添加到 Django INSTALLED_APPS

在你的 Django 项目的 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ... 其他 apps
    'x007007007.er_django',
]
```

### Internal Dependencies

This package has no internal dependencies within the workspace. It's a standalone Django integration package.

## 🚀 快速开始

### 示例：博客应用

假设你有一个 Django app `blog`，包含以下 models：

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'blog_post'
        verbose_name = '博客文章'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blog_comment'
```

### 1. 导出 ER 图

```bash
# 导出为 Mermaid 格式
python manage.py er_export blog --format mermaid --output blog_er.mmd

# 导出为 PlantUML 格式
python manage.py er_export blog --format plantuml --output blog_er.puml

# 输出到控制台
python manage.py er_export blog
```

### 2. 生成 ER 迁移

```bash
# 生成初始迁移
python manage.py er_makemigrations blog

# 指定迁移目录
python manage.py er_makemigrations blog --migrations-dir ./migrations

# 自定义迁移名称
python manage.py er_makemigrations blog --name add_post_views

# 预览（不创建文件）
python manage.py er_makemigrations blog --dry-run
```

输出：
```
Parsing Django models from app 'blog'...
Found 2 models
Detected 5 operations:
  - CreateTable
  - CreateTable
  - AddForeignKey
  - AddForeignKey
  - AddIndex

Migrations for 'blog':
  0001_initial.yaml

Migration saved to: .migrations/blog/0001_initial.yaml
```

### 3. 查看迁移状态

```bash
# 查看特定 app 的迁移
python manage.py er_showmigrations blog

# 查看所有 app 的迁移
python manage.py er_showmigrations
```

输出：
```
blog:
  [X] 0001_initial
  [X] 0002_add_post_views
```

## 📖 命令参考

### er_export

导出 Django models 为 ER 图。

```bash
python manage.py er_export <app_label> [OPTIONS]

参数:
  app_label              Django app 名称 [必需]

选项:
  --format {mermaid,plantuml}  输出格式 [默认: mermaid]
  --output PATH                输出文件路径 [默认: stdout]
```

**示例：**

```bash
# 导出为 Mermaid
python manage.py er_export blog --format mermaid --output docs/blog_er.mmd

# 导出为 PlantUML
python manage.py er_export blog --format plantuml --output docs/blog_er.puml
```

### er_makemigrations

从 Django models 生成 ER 迁移。

```bash
python manage.py er_makemigrations <app_label> [OPTIONS]

参数:
  app_label              Django app 名称 [必需]

选项:
  --migrations-dir PATH  迁移目录 [默认: .migrations]
  --name TEXT            自定义迁移名称
  --dry-run              预览模式（不创建文件）
```

**示例：**

```bash
# 基本用法
python manage.py er_makemigrations blog

# 自定义迁移名称
python manage.py er_makemigrations blog --name add_comment_likes

# 预览变更
python manage.py er_makemigrations blog --dry-run
```

### er_showmigrations

显示 ER 迁移状态。

```bash
python manage.py er_showmigrations [app_label] [OPTIONS]

参数:
  app_label              Django app 名称 [可选]

选项:
  --migrations-dir PATH  迁移目录 [默认: .migrations]
```

**示例：**

```bash
# 显示特定 app
python manage.py er_showmigrations blog

# 显示所有 app
python manage.py er_showmigrations
```

## 🔧 工作原理

### 架构设计

```
Django Models
     ↓
DjangoModelParser (parser.py)
     ↓
ERModel (x007007007.er.models)
     ↓
ERConverter (x007007007.er_migrate.converter)
     ↓
Migration Operations
     ↓
YAML Migration Files
```

### 核心组件

1. **DjangoModelIntrospector** (`introspector.py`)
   - 从 Django models 提取元数据
   - 字段类型、约束、关系等

2. **DjangoModelParser** (`parser.py`)
   - 将 Django models 转换为 ERModel
   - 处理 ForeignKey, OneToOneField, ManyToManyField

3. **Management Commands** (`management/commands/`)
   - `er_export`: 导出 ER 图
   - `er_makemigrations`: 生成迁移
   - `er_showmigrations`: 显示迁移状态

### 命名空间映射

Django app 直接映射为 ER 迁移的命名空间：

```
Django App: blog
    ↓
ER Namespace: blog
    ↓
Migration Files: .migrations/blog/0001_initial.yaml
```

### 字段类型映射

| Django Field | ER Type |
|-------------|---------|
| AutoField | int |
| BigAutoField | bigint |
| CharField | string |
| TextField | text |
| EmailField | string |
| UUIDField | uuid |
| BooleanField | boolean |
| DateField | date |
| DateTimeField | datetime |
| DecimalField | decimal |
| FloatField | float |
| JSONField | json |

### 关系类型映射

| Django Relationship | ER Relationship |
|--------------------|-----------------|
| ForeignKey | one-to-many |
| OneToOneField | one-to-one |
| ManyToManyField | many-to-many |

## 📁 目录结构

```
src/x007007007/er_django/
├── __init__.py              # 包初始化
├── apps.py                  # Django AppConfig
├── parser.py                # Django Model → ERModel 转换器
├── introspector.py          # Django Model 内省工具
├── management/              # Django management commands
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── er_export.py     # 导出 ER 图命令
│       ├── er_makemigrations.py  # 生成迁移命令
│       └── er_showmigrations.py  # 显示迁移状态命令
└── README.md                # 本文档
```

## 🎯 使用场景

### 场景 1: 从现有 Django 项目生成 ER 图

```bash
# 为每个 app 生成 ER 图
python manage.py er_export users --output docs/users_er.mmd
python manage.py er_export blog --output docs/blog_er.mmd
python manage.py er_export comments --output docs/comments_er.mmd
```

### 场景 2: 使用 ER 迁移管理数据库变更

```bash
# 1. 修改 Django models
# 2. 生成 ER 迁移
python manage.py er_makemigrations blog

# 3. 查看迁移状态
python manage.py er_showmigrations blog

# 4. 应用迁移（未来功能）
# python manage.py er_migrate blog
```

### 场景 3: 多 App 项目管理

```bash
# 为每个 app 生成独立的迁移命名空间
python manage.py er_makemigrations users
python manage.py er_makemigrations blog
python manage.py er_makemigrations comments

# 查看所有 app 的迁移状态
python manage.py er_showmigrations
```

## 🔍 高级用法

### 自定义迁移目录

```python
# settings.py
ER_MIGRATIONS_DIR = 'db/er_migrations'
```

```bash
python manage.py er_makemigrations blog --migrations-dir db/er_migrations
```

### 编程式使用

```python
from x007007007.er_django import DjangoModelParser
from x007007007.er.renderers import JinjaRenderer

# 解析 Django models
parser = DjangoModelParser(app_label='blog')
er_model = parser.parse()

# 渲染为 Mermaid
renderer = JinjaRenderer('mermaid_er.j2')
diagram = renderer.render(er_model)
print(diagram)
```

### 解析特定 Models

```python
from blog.models import Post, Comment
from x007007007.er_django import DjangoModelParser

# 只解析指定的 models
parser = DjangoModelParser()
er_model = parser.parse(models_list=[Post, Comment])
```

## 🐛 故障排除

### 问题：找不到 management commands

**原因：** 未添加到 INSTALLED_APPS

**解决：**
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'x007007007.er_django',
]
```

### 问题：解析失败

**原因：** App 不存在或 models 有错误

**解决：**
```bash
# 检查 app 是否存在
python manage.py showmigrations

# 检查 models 语法
python manage.py check
```

### 问题：关系未正确识别

**原因：** 使用了字符串引用的 model

**解决：** 确保所有相关的 models 都在同一个 app 中，或使用完整的 app_label.ModelName 引用。

## 🤝 与 Django 原生迁移的对比

| 特性 | Django Migrations | ER Migrations |
|-----|------------------|---------------|
| 基于 | Python 代码 | ER 图 (YAML) |
| 可读性 | 中等 | 高 |
| 版本控制 | 友好 | 非常友好 |
| 跨框架 | 仅 Django | 框架无关 |
| 学习曲线 | 陡峭 | 平缓 |
| 可视化 | 需要工具 | 原生支持 |

## 📚 相关文档

- [ER Migrate 文档](../er_migrate/README.md)
- [ER 模型文档](../er/README.md)
- [Django 官方文档](https://docs.djangoproject.com/)

## 🙏 致谢

本模块基于以下项目：
- `x007007007.er`: ER 图解析和渲染
- `x007007007.er_migrate`: ER 迁移系统
- Django: Web 框架

## 📄 许可证

MIT License
