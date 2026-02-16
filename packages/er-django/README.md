# ER Django

Django models 与 ER 图双向转换工具。支持从 Django models 导出 ER 图（TOML/Mermaid/PlantUML），以及从 TOML 格式生成 Django/SQLAlchemy 代码。

## 功能特性

- **Django → TOML**: 从 Django models 导出为 TOML 格式的 ER 定义
- **TOML → Django/SQLAlchemy**: 从 TOML 生成 Django models 或 SQLAlchemy 代码
- **Django → Mermaid/PlantUML**: 导出 ER 图用于文档和可视化
- **db_column 支持**: 正确处理 Django 字段的 `db_column` 参数
- **三方包自动分离**: 自动检测并分离三方包（如 DRF、django-filter）的输出
- **批量处理**: 一次性处理多个应用
- **ER 迁移**: 基于 ER 图的数据库迁移系统（实验性）

## 安装

### 1. 安装包

```bash
pip install x007007007-er-django
```

或使用 uv：

```bash
uv pip install x007007007-er-django
```

### 2. 添加到 INSTALLED_APPS

在 Django 项目的 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'x007007007.er_django',
]
```

## 快速开始

### 基本工作流程

```bash
# 1. 从 Django models 导出 TOML
python manage.py er_export --output-dir src

# 2. 从 TOML 生成代码（Django 或 SQLAlchemy）
python manage.py er_convert --framework django
```

### 示例：博客应用

假设你有一个博客应用：

```python
# blog/models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blog_post'
```

**导出为 TOML：**

```bash
python manage.py er_export blog --format toml --output-dir src
```

生成的文件 `src/blog/models.toml`：

```toml
[entities.Post]
table_name = "blog_post"

[[entities.Post.columns]]
name = "id"
type = "AutoField"
primary_key = true

[[entities.Post.columns]]
name = "title"
type = "CharField"
max_length = 200

[[entities.Post.columns]]
name = "content"
type = "TextField"

[[entities.Post.columns]]
name = "author_id"
type = "ForeignKey"
related_model = "auth.User"
on_delete = "CASCADE"

[[entities.Post.columns]]
name = "created_at"
type = "DateTimeField"
auto_now_add = true
```

**从 TOML 生成 Django 代码：**

```bash
python manage.py er_convert blog --framework django
```

生成的文件 `src/blog/models/post.py`：

```python
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blog_post'
```

## 命令参考

### er_export - 导出 Django models

从 Django models 导出为 TOML、Mermaid 或 PlantUML 格式。

```bash
python manage.py er_export [apps] [options]
```

**参数：**
- `apps`: 要导出的应用名称（可选，不指定则导出所有本地应用）

**选项：**
- `--format {toml,mermaid,plantuml}`: 输出格式（默认：toml）
- `--output FILE`: 输出文件路径（仅单个应用时有效）
- `--output-dir DIR`: 输出目录（默认：src）
- `--models MODEL1,MODEL2`: 只导出指定的 models
- `--exclude-apps APP1,APP2`: 排除指定的应用
- `--include-django-apps`: 包含 Django 内置应用（auth、contenttypes 等）

**示例：**

```bash
# 导出所有本地应用为 TOML
python manage.py er_export --format toml --output-dir src

# 导出指定应用
python manage.py er_export blog account --format toml

# 导出为 Mermaid ER 图
python manage.py er_export blog --format mermaid --output docs/blog_er.mmd

# 只导出特定 models
python manage.py er_export blog --models Post,Comment

# 包含 Django 内置应用
python manage.py er_export --include-django-apps
```

### er_convert - 从 TOML 生成代码

从 TOML 格式的 ER 定义生成 Django 或 SQLAlchemy 代码。

```bash
python manage.py er_convert [apps] [options]
```

**参数：**
- `apps`: 要转换的应用名称（可选，不指定则自动发现所有有 TOML 的应用）

**选项：**
- `--framework {django,sqlalchemy}`: 目标框架（默认：django）
- `--output-dir DIR`: TOML 搜索和代码输出目录（默认：src）
- `--output-subdir SUBDIR`: 自定义输出子目录名称
- `--base-model-import PATH`: SQLAlchemy 的 BaseModel 导入路径

**示例：**

```bash
# 自动发现并转换所有应用
python manage.py er_convert --framework django

# 转换指定应用
python manage.py er_convert blog account --framework django

# 生成 SQLAlchemy 代码
python manage.py er_convert blog --framework sqlalchemy

# 自定义输出目录
python manage.py er_convert --framework django --output-subdir generated

# 指定 SQLAlchemy BaseModel
python manage.py er_convert --framework sqlalchemy \
    --base-model-import myproject.database.Base
```

### er_makemigrations - 生成 ER 迁移（实验性）

从 Django models 生成基于 ER 的迁移文件。

```bash
python manage.py er_makemigrations <app> [options]
```

**参数：**
- `app`: Django 应用名称（必需）

**选项：**
- `--migrations-dir DIR`: 迁移目录（默认：.migrations）
- `--name NAME`: 自定义迁移名称
- `--dry-run`: 预览模式，不创建文件

**示例：**

```bash
# 生成迁移
python manage.py er_makemigrations blog

# 自定义迁移名称
python manage.py er_makemigrations blog --name add_post_views

# 预览变更
python manage.py er_makemigrations blog --dry-run
```

### er_showmigrations - 显示迁移状态（实验性）

显示 ER 迁移的应用状态。

```bash
python manage.py er_showmigrations [app] [options]
```

**参数：**
- `app`: Django 应用名称（可选）

**选项：**
- `--migrations-dir DIR`: 迁移目录（默认：.migrations）

**示例：**

```bash
# 显示所有应用的迁移状态
python manage.py er_showmigrations

# 显示特定应用
python manage.py er_showmigrations blog
```

## 高级功能

### db_column 参数支持

ER Django 完全支持 Django 字段的 `db_column` 参数，能够正确区分业务字段名和数据库列名。

**示例：**

```python
class User(models.Model):
    # 业务字段名：username，数据库列名：user_name
    username = models.CharField(max_length=100, db_column='user_name')
    email = models.EmailField()  # 数据库列名与字段名相同
```

导出的 TOML：

```toml
[[entities.User.columns]]
name = "username"
db_column = "user_name"  # 仅在与 name 不同时输出
type = "CharField"
max_length = 100

[[entities.User.columns]]
name = "email"
# db_column 未输出，因为与 name 相同
type = "EmailField"
```

生成的代码会正确包含 `db_column` 参数：

```python
class User(models.Model):
    username = models.CharField(max_length=100, db_column='user_name')
    email = models.EmailField()
```

### 三方包自动检测和分离

ER Django 能够自动检测三方包（安装在 site-packages 或 .venv 中的包），并将它们的输出分离到 `third/` 目录。

#### 工作原理

1. **er_export** 检查应用的物理路径：
   - 如果在 `src/` 目录外（如 site-packages），标记为三方包
   - 三方包输出到 `src/third/{包路径}/models.toml`
   - 本地包输出到 `src/{包路径}/models.toml`

2. **er_convert** 自动发现所有 TOML 文件：
   - 在 `src/` 和 `src/third/` 中查找
   - 三方包代码输出到 `src/third/{包路径}/models/`
   - 本地包代码输出到 `src/{包路径}/models/`

#### 完整示例

**步骤 1：导出所有应用**

```bash
python manage.py er_export --output-dir src
```

输出：
```
Exporting all local apps: myapp, blog, django_filters, rest_framework
  django_filters: third-party package
  rest_framework: third-party package
Found 5 models in app 'myapp'
  → src/myapp/models.toml
Found 3 models in app 'blog'
  → src/blog/models.toml
Found 2 models in app 'django_filters'
  → src/third/django_filters/models.toml
Found 7 models in app 'rest_framework'
  → src/third/rest_framework/models.toml
```

**步骤 2：转换所有 TOML**

```bash
python manage.py er_convert --framework django
```

输出：
```
Auto-discovered 4 apps with models.toml:
  - myapp
  - blog
  - django_filters
  - rest_framework

Converting app 'myapp' to django...
  Output directory: src/myapp/models
  Generated 3 files

Converting app 'blog' to django...
  Output directory: src/blog/models
  Generated 2 files

Converting app 'django_filters' to django (third-party package)...
  Output directory: src/third/django_filters/models
  Generated 2 files

Converting app 'rest_framework' to django (third-party package)...
  Output directory: src/third/rest_framework/models
  Generated 5 files
```

**生成的目录结构：**

```
src/
├── myapp/                      # 本地应用
│   ├── models.toml
│   └── models/
│       ├── __init__.py
│       └── user.py
├── blog/                       # 本地应用
│   ├── models.toml
│   └── models/
│       ├── __init__.py
│       └── post.py
└── third/                      # 三方包目录
    ├── django_filters/
    │   ├── models.toml
    │   └── models/
    │       ├── __init__.py
    │       └── filter.py
    └── rest_framework/
        ├── models.toml
        └── models/
            ├── __init__.py
            ├── token.py
            └── ...
```

#### 优势

- **自动化**：无需手动区分本地包和三方包
- **清晰分离**：三方包代码与本地代码物理隔离
- **版本控制友好**：可以选择性地将 `third/` 添加到 `.gitignore`
- **避免冲突**：三方包在独立目录中，不会与本地代码冲突

### 批量处理

```bash
# 导出多个应用
python manage.py er_export blog account orders --format toml

# 转换多个应用
python manage.py er_convert blog account orders --framework django

# 排除某些应用
python manage.py er_export --exclude-apps test,migrations
```

### 自定义路径

```bash
# 自定义输出目录
python manage.py er_export --output-dir generated

# 自定义子目录名称
python manage.py er_convert --output-subdir db_models
```

## 支持的字段类型

### Django 字段映射

| Django Field | TOML Type | 说明 |
|-------------|-----------|------|
| AutoField | AutoField | 自增主键 |
| BigAutoField | BigAutoField | 大整数自增主键 |
| CharField | CharField | 字符串字段 |
| TextField | TextField | 文本字段 |
| EmailField | EmailField | 邮箱字段 |
| URLField | URLField | URL 字段 |
| UUIDField | UUIDField | UUID 字段 |
| BooleanField | BooleanField | 布尔字段 |
| IntegerField | IntegerField | 整数字段 |
| BigIntegerField | BigIntegerField | 大整数字段 |
| DecimalField | DecimalField | 十进制数字段 |
| FloatField | FloatField | 浮点数字段 |
| DateField | DateField | 日期字段 |
| DateTimeField | DateTimeField | 日期时间字段 |
| TimeField | TimeField | 时间字段 |
| JSONField | JSONField | JSON 字段 |
| ForeignKey | ForeignKey | 外键关系 |
| OneToOneField | OneToOneField | 一对一关系 |
| ManyToManyField | ManyToManyField | 多对多关系 |

### 关系字段

完全支持 Django 的关系字段：

- **ForeignKey**: 一对多关系
- **OneToOneField**: 一对一关系
- **ManyToManyField**: 多对多关系
- **on_delete**: CASCADE, SET_NULL, PROTECT 等
- **related_name**: 反向关系名称

## 使用场景

### 场景 1：文档生成

从现有 Django 项目生成 ER 图用于文档：

```bash
# 生成 Mermaid 格式的 ER 图
python manage.py er_export --format mermaid --output docs/database_er.mmd

# 生成 PlantUML 格式
python manage.py er_export --format plantuml --output docs/database_er.puml
```

### 场景 2：代码生成

从 TOML 定义生成 Django 或 SQLAlchemy 代码：

```bash
# 生成 Django models
python manage.py er_convert --framework django

# 生成 SQLAlchemy models
python manage.py er_convert --framework sqlalchemy
```

### 场景 3：跨框架迁移

从 Django 迁移到 SQLAlchemy：

```bash
# 1. 从 Django 导出 TOML
python manage.py er_export --format toml

# 2. 生成 SQLAlchemy 代码
python manage.py er_convert --framework sqlalchemy
```

### 场景 4：多应用项目管理

管理大型项目的多个应用：

```bash
# 导出所有应用
python manage.py er_export --output-dir src

# 批量转换
python manage.py er_convert --framework django

# 查看迁移状态
python manage.py er_showmigrations
```

## 常见问题

### Q: 找不到 management commands

**A:** 确保已将 `x007007007.er_django` 添加到 `INSTALLED_APPS`。

### Q: 三方包没有被检测到

**A:** 确保三方包安装在 `src/` 目录外（如 site-packages 或 .venv）。可以通过查看控制台输出确认哪些包被标记为 "third-party package"。

### Q: TOML 文件找不到

**A:** 确保先运行 `er_export` 生成 TOML 文件，然后再运行 `er_convert`。

### Q: 生成的代码与原 models 不一致

**A:** 检查 TOML 文件是否正确。某些复杂的字段配置可能需要手动调整 TOML。

### Q: 如何排除测试应用

**A:** 使用 `--exclude-apps` 选项：
```bash
python manage.py er_export --exclude-apps test,migrations
```

## 开发文档

如果你想参与开发或了解内部实现，请参阅：

- [开发指南](../../DEVELOPMENT.md) - 工作区开发设置
- [安装说明](INSTALL.md) - 详细安装步骤
- [项目结构](../../PROJECT_STRUCTURE.md) - 代码组织

## 相关项目

- [er-gen-core](../er-gen-core/) - ER 图核心库
- [er-gen-tool](../er-gen-tool/) - ER 命令行工具
- [er-gen-mcp](../er-gen-mcp/) - MCP 服务器集成

## 许可证

MIT License
