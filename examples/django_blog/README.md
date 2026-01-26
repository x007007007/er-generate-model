# Django Blog Example

这是一个用于测试 ER Django 插件的示例项目，包含三个 Django app：

- **users**: 用户管理（CustomUser, UserProfile, UserSettings）
- **blog**: 博客系统（Category, Post, Tag, Comment, PostTag）
- **products**: 产品管理（Category, Brand, Product, ProductImage, ProductVariant）

## 快速开始

### 1. 导出 ER 图

ER Django 支持三种导出格式：

```bash
# 导出所有 app 为 Mermaid 格式（每个 app 独立文件）
uv run python manage.py er_export --format mermaid

# 导出所有 app 为 PlantUML 格式
uv run python manage.py er_export --format plantuml

# 导出所有 app 为 TOML 格式
uv run python manage.py er_export --format toml
```

导出的文件将保存在 `er_export/` 目录下：
- `blog.mmd` / `blog.puml` / `blog.toml`
- `users.mmd` / `users.puml` / `users.toml`
- `products.mmd` / `products.puml` / `products.toml`

### 2. 导出特定 app

```bash
# 只导出 blog app
uv run python manage.py er_export blog --format mermaid

# 导出多个指定 app
uv run python manage.py er_export users products --format toml
```

### 3. 生成迁移文件

```bash
# 为所有 app 生成迁移
uv run python manage.py er_makemigrations

# 为特定 app 生成迁移
uv run python manage.py er_makemigrations blog --name add_new_fields

# 预览迁移（不创建文件）
uv run python manage.py er_makemigrations --dry-run
```

迁移文件将保存在 `er_migrations/` 目录下。

## 配置说明

在 `django_blog/settings.py` 中配置 ER Django：

```python
# ER Django 设置
ER_MIGRATIONS_DIR = 'er_migrations'  # 迁移文件目录
ER_EXPORT_DIR = 'er_export'          # 导出文件目录
ER_DEFAULT_FORMAT = 'mermaid'        # 默认格式: mermaid, plantuml, toml
ER_AUTO_CREATE_DIRS = True           # 自动创建目录
ER_INCLUDE_DJANGO_APPS = False       # 排除 Django 内置 app
ER_EXCLUDE_APPS = ['er_django']      # 额外排除的 app
ER_FILE_PREFIX = ''                  # 文件名前缀
ER_FILE_SUFFIX = ''                  # 文件名后缀
```

## 文件命名规则

- **默认**: 使用 app label 作为文件名
  - `blog.mmd`, `users.puml`, `products.toml`
  
- **带前缀**: `ER_FILE_PREFIX = 'v1'`
  - `v1_blog.mmd`, `v1_users.puml`
  
- **带后缀**: `ER_FILE_SUFFIX = 'latest'`
  - `blog_latest.mmd`, `users_latest.puml`

- **自定义名称**: 使用 `--name` 参数
  - `python manage.py er_export blog --name custom` → `custom.mmd`

## 测试脚本

运行测试脚本以验证所有功能：

```bash
# Linux/Mac
./test_export_formats.sh

# Windows
test_export_formats.bat
```

## 目录结构

```
django_blog/
├── manage.py
├── django_blog/          # 项目配置
│   └── settings.py
├── users/                # 用户 app
│   └── models.py
├── blog/                 # 博客 app
│   └── models.py
├── products/             # 产品 app
│   └── models.py
├── er_migrations/        # ER 迁移文件
│   ├── users/
│   ├── blog/
│   └── products/
└── er_export/            # ER 导出文件
    ├── users.mmd
    ├── users.puml
    ├── users.toml
    ├── blog.mmd
    ├── blog.puml
    ├── blog.toml
    ├── products.mmd
    ├── products.puml
    └── products.toml
```

## 更多信息

查看完整文档：
- [ER Django 设置文档](../../packages/er-django/src/x007007007/er_django/SETTINGS.md)
- [ER Django 安装指南](../../packages/er-django/INSTALL.md)
- [ER Django README](../../packages/er-django/README.md)
