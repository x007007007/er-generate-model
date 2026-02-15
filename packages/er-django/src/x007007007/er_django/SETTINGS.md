# ER Django Settings Configuration

ER Django 插件支持通过 Django settings 进行配置。所有设置都是可选的，如果未配置则使用默认值。

## 📋 可用设置

### ER_MIGRATIONS_DIR

**类型**: `str`  
**默认值**: `BASE_DIR / 'er_migrations'`  
**描述**: ER 迁移文件存储目录

```python
# settings.py

# 相对路径（相对于 BASE_DIR）
ER_MIGRATIONS_DIR = 'er_migrations'

# 绝对路径
ER_MIGRATIONS_DIR = '/path/to/migrations'

# 使用 Path 对象
from pathlib import Path
ER_MIGRATIONS_DIR = BASE_DIR / 'database' / 'er_migrations'
```

### ER_EXPORT_DIR

**类型**: `str`  
**默认值**: `BASE_DIR / 'er_export'`  
**描述**: ER 图导出文件存储目录

```python
# settings.py

# 相对路径（相对于 BASE_DIR）
ER_EXPORT_DIR = 'er_export'

# 绝对路径
ER_EXPORT_DIR = '/path/to/diagrams'

# 使用 Path 对象
ER_EXPORT_DIR = BASE_DIR / 'docs' / 'er_diagrams'
```

### ER_DEFAULT_FORMAT

**类型**: `str`  
**默认值**: `'mermaid'`  
**可选值**: `'mermaid'`, `'plantuml'`, `'toml'`  
**描述**: 默认的 ER 图导出格式

```python
# settings.py
ER_DEFAULT_FORMAT = 'mermaid'  # 或 'plantuml' 或 'toml'
```

### ER_AUTO_CREATE_DIRS

**类型**: `bool`  
**默认值**: `True`  
**描述**: 是否自动创建输出目录

```python
# settings.py
ER_AUTO_CREATE_DIRS = True  # 自动创建目录
ER_AUTO_CREATE_DIRS = False  # 不自动创建，需要手动创建
```

### ER_INCLUDE_DJANGO_APPS

**类型**: `bool`  
**默认值**: `False`  
**描述**: 是否默认包含 Django 内置应用

```python
# settings.py
ER_INCLUDE_DJANGO_APPS = False  # 默认排除 Django 内置应用
ER_INCLUDE_DJANGO_APPS = True   # 默认包含 Django 内置应用
```

### ER_EXCLUDE_APPS

**类型**: `list[str]`  
**默认值**: `[]`  
**描述**: 默认排除的应用列表

```python
# settings.py
ER_EXCLUDE_APPS = [
    'admin',
    'auth',
    'contenttypes',
    'sessions',
    'messages',
    'staticfiles',
    'er_django',  # 排除插件本身
]
```

### ER_FILE_PREFIX

**类型**: `str`  
**默认值**: `''`  
**描述**: 导出文件名前缀

```python
# settings.py
ER_FILE_PREFIX = 'project'  # 生成文件如: project_blog.mmd
ER_FILE_PREFIX = 'v1'       # 生成文件如: v1_blog.mmd
```

### ER_FILE_SUFFIX

**类型**: `str`  
**默认值**: `''`  
**描述**: 导出文件名后缀

```python
# settings.py
ER_FILE_SUFFIX = 'latest'   # 生成文件如: blog_latest.mmd
ER_FILE_SUFFIX = '2024'     # 生成文件如: blog_2024.mmd
```

## 📝 文件命名规则

导出的文件名默认使用 Django app label 作为基础名称：

- **单个 app**: `{app_label}.{ext}`
  - 例如: `blog.mmd`, `users.puml`, `products.toml`
  
- **带前缀**: `{prefix}_{app_label}.{ext}`
  - 例如: `v1_blog.mmd`, `prod_users.puml`
  
- **带后缀**: `{app_label}_{suffix}.{ext}`
  - 例如: `blog_latest.mmd`, `users_2024.puml`
  
- **前缀和后缀**: `{prefix}_{app_label}_{suffix}.{ext}`
  - 例如: `v1_blog_latest.mmd`

- **自定义名称**: 使用 `--name` 参数
  - 例如: `python manage.py er_export blog --name custom` → `custom.mmd`

**注意**: 当导出多个 app 时，每个 app 会生成独立的文件，文件名使用各自的 app label。

## 📝 完整配置示例

```python
# settings.py
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ... 其他 Django 设置 ...

# ER Django 配置
ER_MIGRATIONS_DIR = BASE_DIR / 'database' / 'er_migrations'
ER_EXPORT_DIR = BASE_DIR / 'docs' / 'er_export'
ER_DEFAULT_FORMAT = 'mermaid'
ER_AUTO_CREATE_DIRS = True
ER_INCLUDE_DJANGO_APPS = False
ER_EXCLUDE_APPS = [
    'admin',
    'auth', 
    'contenttypes',
    'sessions',
    'messages',
    'staticfiles',
    'er_django',
]
ER_FILE_PREFIX = 'myproject'
ER_FILE_SUFFIX = 'v1'
```

## 🎯 使用场景

### 场景 1: 开发环境配置

```python
# settings/development.py
ER_MIGRATIONS_DIR = 'dev_migrations'
ER_EXPORT_DIR = 'dev_export'
ER_FILE_SUFFIX = 'dev'
```

### 场景 2: 生产环境配置

```python
# settings/production.py
ER_MIGRATIONS_DIR = '/var/app/migrations'
ER_EXPORT_DIR = '/var/app/docs/export'
ER_FILE_PREFIX = 'prod'
ER_AUTO_CREATE_DIRS = False  # 生产环境手动管理目录
```

### 场景 3: 团队协作配置

```python
# settings/base.py
ER_MIGRATIONS_DIR = 'shared_migrations'
ER_EXPORT_DIR = 'shared_export'
ER_EXCLUDE_APPS = [
    'admin',
    'auth',
    'contenttypes', 
    'sessions',
    'messages',
    'staticfiles',
    'debug_toolbar',  # 开发工具
    'django_extensions',
]
ER_FILE_PREFIX = 'team'
```

## 🔧 命令行覆盖

所有设置都可以通过命令行参数覆盖：

```bash
# 覆盖迁移目录
^uv run python manage.py er_makemigrations --migrations-dir custom_migrations

# 覆盖导出目录
^uv run python manage.py er_export --output-dir custom_export

# 覆盖格式（支持 mermaid, plantuml, toml）
^uv run python manage.py er_export --format toml

# 覆盖排除应用
^uv run python manage.py er_export --exclude-apps "admin,auth"

# 导出所有 app（每个 app 生成独立文件）
^uv run python manage.py er_export --format mermaid

# 导出特定 app
^uv run python manage.py er_export blog users --format toml

# 使用自定义文件名
^uv run python manage.py er_export blog --name my_custom_name
```

## 📁 目录结构示例

使用默认设置时的项目结构：

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   └── ...
├── myapp/
│   ├── models.py
│   └── ...
├── er_migrations/          # ER 迁移文件
│   ├── myapp/
│   │   ├── 0001_initial.yaml
│   │   └── 0002_add_fields.yaml
│   └── anotherapp/
│       └── 0001_initial.yaml
└── er_export/              # ER 图文件（每个 app 独立文件）
    ├── myapp.mmd           # Mermaid 格式
    ├── myapp.puml          # PlantUML 格式
    ├── myapp.toml          # TOML 格式
    ├── anotherapp.mmd
    ├── anotherapp.puml
    └── anotherapp.toml
```

## 🚀 最佳实践

### 1. 版本控制

```python
# 将迁移文件纳入版本控制
ER_MIGRATIONS_DIR = 'er_migrations'

# .gitignore
# er_export/  # 导出文件可以不纳入版本控制
```

### 2. 环境分离

```python
# settings/base.py
ER_AUTO_CREATE_DIRS = True

# settings/production.py
ER_AUTO_CREATE_DIRS = False
ER_MIGRATIONS_DIR = '/app/migrations'
ER_EXPORT_DIR = '/app/export'
```

### 3. 文件命名

```python
# 使用项目名和版本
ER_FILE_PREFIX = 'myproject'
ER_FILE_SUFFIX = 'v2'

# 生成: myproject_blog_v2.mmd, myproject_users_v2.mmd
```

### 4. 多格式导出

```bash
# 同时导出多种格式
^uv run python manage.py er_export --format mermaid
^uv run python manage.py er_export --format plantuml
^uv run python manage.py er_export --format toml

# 结果: blog.mmd, blog.puml, blog.toml
```

## 🔍 调试设置

查看当前生效的设置：

```python
# Django shell
^uv run python manage.py shell

>>> from x007007007.er_django.settings import get_er_settings
>>> import pprint
>>> pprint.pprint(get_er_settings())
{
    'auto_create_dirs': True,
    'default_format': 'mermaid',
    'exclude_apps': ['er_django'],
    'export_dir': '/path/to/project/er_export',
    'file_prefix': '',
    'file_suffix': '',
    'include_django_apps': False,
    'migrations_dir': '/path/to/project/er_migrations'
}
```

## 📊 导出格式说明

### Mermaid (.mmd)
- 适合在 Markdown 文档中使用
- 支持 GitHub、GitLab 等平台直接渲染
- 语法简洁，易于阅读

### PlantUML (.puml)
- 功能强大，支持复杂图表
- 需要 PlantUML 工具渲染
- 适合生成高质量的文档图表

### TOML (.toml)
- 结构化配置格式
- 可以被 ER 工具重新导入
- 适合版本控制和代码生成

## 📚 相关文档

- [Django Settings 文档](https://docs.djangoproject.com/en/stable/topics/settings/)
- [ER Django README](README.md)
- [安装指南](INSTALL.md)