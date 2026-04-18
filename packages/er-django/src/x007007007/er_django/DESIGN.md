# ER Django 插件设计文档

## 📋 概述

ER Django 是一个 Django 插件，用于将 Django models 转换为 ER 图和 ER 迁移系统的内部数据结构。它将 Django app 作为命名空间，实现了现有 er-migration 的所有功能。

## 🎯 设计目标

1. **无缝集成**: 作为 Django app 集成，使用 Django management commands
2. **命名空间隔离**: Django app → ER migration namespace 的自然映射
3. **双向转换**: Django models ↔ ER 图
4. **完整功能**: 支持 er-migrate 的所有功能
5. **类型安全**: 完整的类型提示和验证

## 🏗️ 架构设计

### 模块结构

```
src/x007007007/er_django/
├── __init__.py              # 包初始化，导出主要类
├── apps.py                  # Django AppConfig
├── introspector.py          # Django Model 内省工具
├── parser.py                # Django Model → ERModel 转换器
├── management/              # Django management commands
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── er_export.py     # 导出 ER 图
│       ├── er_makemigrations.py  # 生成迁移
│       └── er_showmigrations.py  # 显示迁移状态
├── DESIGN.md                # 本文档
└── README.md                # 用户文档
```

### 数据流

```
┌─────────────────┐
│ Django Models   │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│ DjangoModelIntrospector │  ← 提取元数据
└────────┬────────────────┘
         │
         ↓
┌─────────────────────┐
│ DjangoModelParser   │  ← 转换为 ERModel
└────────┬────────────┘
         │
         ↓
┌─────────────────┐
│ ERModel         │  ← 统一的 ER 表示
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ↓                 ↓
┌─────────────────┐  ┌──────────────┐
│ ERConverter     │  │ JinjaRenderer│
└────────┬────────┘  └──────┬───────┘
         │                  │
         ↓                  ↓
┌─────────────────┐  ┌──────────────┐
│ Migration Ops   │  │ ER Diagram   │
└─────────────────┘  └──────────────┘
```

## 🔧 核心组件

### 1. DjangoModelIntrospector

**职责**: 从 Django models 提取元数据

**主要方法**:
- `get_field_type(field)`: 获取字段类型
- `get_field_max_length(field)`: 获取最大长度
- `is_primary_key(field)`: 检查是否为主键
- `is_nullable(field)`: 检查是否可空
- `is_unique(field)`: 检查是否唯一
- `get_related_model(field)`: 获取关联模型
- `get_foreign_keys(model)`: 获取所有外键
- `get_one_to_one_fields(model)`: 获取所有一对一字段
- `get_many_to_many_fields(model)`: 获取所有多对多字段

**设计考虑**:
- 静态方法设计，无状态
- 处理 Django 的各种字段类型
- 支持自定义字段（通过类型映射）

### 2. DjangoModelParser

**职责**: 将 Django models 转换为 ERModel

**主要方法**:
- `parse(models_list)`: 解析 models 列表
- `_convert_model_to_entity(model)`: 转换单个 model
- `_convert_field_to_column(field)`: 转换字段为列
- `_extract_relationships(model)`: 提取关系
- `_collect_all_abstract_ancestors(model)`: 递归收集所有抽象祖先模型
- `_convert_abstract_to_template(model)`: 将抽象模型转换为模板定义

**工作流程**:
1. 获取要解析的 models（从 app 或列表）
2. 第一遍：创建所有 Entity + 递归收集所有抽象基类作为 templates
3. 第二遍：创建所有 Relationship
4. 第三遍：将抽象基类转换为 templates 并添加到 ERModel

**设计考虑**:
- 支持三种输入方式：
  - 指定 app_label
  - 提供 models_list
  - 解析所有 models
- 三遍扫描确保关系正确建立，抽象模型完整收集
- 递归遍历继承链确保多层抽象基类不遗漏

### 3. Management Commands

#### er_export

**功能**: 导出 Django models 为 ER 图

**参数**:
- `apps`: Django app 名称列表（可选）
- `--format`: 输出格式（toml/mermaid/plantuml）
- `--output`: 输出文件路径
- `--output-dir`: 输出目录
- `--models`: 只导出指定的 models
- `--exclude-apps`: 排除指定的应用
- `--include-django-apps`: 包含 Django 内置应用

**实现**:
```python
# 1. 导出每个 app 的 concrete models
for app_label in target_apps:
    parser = DjangoModelParser(app_label=app_label)
    er_model = parser.parse()
    renderer = TOMLRenderer()
    diagram = renderer.render(er_model)
    # 写入 app 的 TOML 文件（含 templates 段）

# 2. 收集所有抽象模板，按 Python 包路径分组导出
_export_templates(all_templates, path_config)
```

**抽象模型导出流程**:
1. 遍历所有 app 的 concrete models
2. 对每个 model 递归收集其所有抽象祖先（`_collect_all_abstract_ancestors`）
3. 收集完成后按 `__module__` 分组
4. 每组生成独立的 TOML 文件，namespace 为包路径

#### er_makemigrations

**功能**: 从 Django models 生成 ER 迁移

**参数**:
- `app_label`: Django app 名称（必需）
- `--migrations-dir`: 迁移目录
- `--name`: 自定义迁移名称
- `--dry-run`: 预览模式

**实现**:
```python
# 1. 解析 Django models
parser = DjangoModelParser(app_label=app_label)
er_model = parser.parse()

# 2. 转换为迁移格式
converter = ERConverter()
current_state = converter.convert_model(er_model)

# 3. 计算差异
differ = MigrationDiffer()
operations = differ.diff(previous_state, current_state)

# 4. 生成迁移文件
generator = MigrationGenerator(file_manager)
migration = generator.generate_migration(...)
```

#### er_showmigrations

**功能**: 显示 ER 迁移状态

**参数**:
- `app_label`: Django app 名称（可选）
- `--migrations-dir`: 迁移目录

**实现**:
```python
file_manager = MigrationFileManager(migrations_dir)
migrations = file_manager.load_migrations(app_label)
# 显示迁移列表
```

## 🔄 命名空间映射

### Django App → ER Namespace

Django app 直接映射为 ER 迁移的命名空间：

```
Django Project
├── blog/                    ← Django app
│   ├── models.py
│   └── ...
├── users/                   ← Django app
│   ├── models.py
│   └── ...
└── .migrations/             ← ER 迁移目录
    ├── blog/                ← ER namespace
    │   ├── 0001_initial.yaml
    │   └── 0002_add_views.yaml
    └── users/               ← ER namespace
        └── 0001_initial.yaml
```

**优势**:
- 自然的映射关系
- 与 Django 的 app 概念一致
- 易于理解和管理

## 📊 类型映射

### Django Field → ER Type

| Django Field | ER Type | 说明 |
|-------------|---------|------|
| AutoField | int | 自增整数 |
| BigAutoField | bigint | 大整数自增 |
| SmallAutoField | smallint | 小整数自增 |
| IntegerField | int | 整数 |
| BigIntegerField | bigint | 大整数 |
| SmallIntegerField | smallint | 小整数 |
| CharField | string | 字符串 |
| TextField | text | 文本 |
| EmailField | string | 邮箱（字符串） |
| URLField | string | URL（字符串） |
| UUIDField | uuid | UUID |
| BooleanField | boolean | 布尔值 |
| DateField | date | 日期 |
| DateTimeField | datetime | 日期时间 |
| TimeField | time | 时间 |
| DecimalField | decimal | 十进制数 |
| FloatField | float | 浮点数 |
| JSONField | json | JSON |
| FileField | string | 文件路径 |
| ImageField | string | 图片路径 |

### Django Relationship → ER Relationship

| Django Relationship | ER Relationship | 说明 |
|--------------------|-----------------|------|
| ForeignKey | one-to-many | 多对一（反向为一对多） |
| OneToOneField | one-to-one | 一对一 |
| ManyToManyField | many-to-many | 多对多 |

## 🎨 使用场景

### 场景 1: 文档生成

从现有 Django 项目生成 ER 图文档：

```bash
# 为每个 app 生成 ER 图
^uv run python manage.py er_export users --output docs/users_er.mmd
^uv run python manage.py er_export blog --output docs/blog_er.mmd
^uv run python manage.py er_export products --output docs/products_er.mmd
```

### 场景 2: 迁移管理

使用 ER 迁移系统管理数据库变更：

```bash
# 1. 修改 Django models
# 2. 生成 ER 迁移
^uv run python manage.py er_makemigrations blog

# 3. 查看变更
^uv run python manage.py er_showmigrations blog

# 4. 应用迁移（未来功能）
# python manage.py er_migrate blog
```

### 场景 3: 跨框架迁移

将 Django models 导出为框架无关的 ER 图，用于：
- 迁移到其他框架（Flask, FastAPI）
- 生成其他 ORM 代码（SQLAlchemy）
- 数据库设计文档

```bash
# 导出 ER 图
^uv run python manage.py er_export blog --output blog_er.mmd

# 使用 er-cli 生成 SQLAlchemy 代码
er-cli -i blog_er.mmd -o sqlalchemy -f blog_models.py
```

### 场景 4: 多 App 项目

管理大型 Django 项目的多个 app：

```bash
# 为每个 app 生成独立的迁移命名空间
^uv run python manage.py er_makemigrations users
^uv run python manage.py er_makemigrations blog
^uv run python manage.py er_makemigrations products
^uv run python manage.py er_makemigrations orders

# 查看所有 app 的迁移状态
^uv run python manage.py er_showmigrations
```

## 🔍 技术细节

### 字段属性提取

```python
# 从 Django field 提取属性
field = model._meta.get_field('username')

# 类型
field_type = field.__class__.__name__  # 'CharField'

# 约束
is_pk = field.primary_key
is_unique = field.unique
is_nullable = field.null
has_index = field.db_index

# 参数
max_length = field.max_length  # CharField
max_digits = field.max_digits  # DecimalField
decimal_places = field.decimal_places  # DecimalField

# 默认值
if field.has_default():
    default = field.default

# 注释
comment = field.help_text
```

### 关系提取

```python
# ForeignKey
for field in model._meta.get_fields():
    if isinstance(field, ForeignKey):
        related_model = field.related_model
        on_delete = field.remote_field.on_delete
        
# OneToOneField
for field in model._meta.get_fields():
    if isinstance(field, OneToOneField):
        related_model = field.related_model
        
# ManyToManyField
for field in model._meta.get_fields():
    if isinstance(field, ManyToManyField):
        related_model = field.related_model
        through_model = field.remote_field.through
```

### 状态重建

从迁移历史重建数据库状态：

```python
def _rebuild_state(migrations):
    state = {"tables": {}, "foreign_keys": []}
    
    for migration in migrations:
        for operation in migration.operations:
            if operation.type == "CreateTable":
                state["tables"][operation.table_name] = {
                    "columns": operation.columns,
                    "indexes": []
                }
            elif operation.type == "AddColumn":
                state["tables"][operation.table_name]["columns"].append(
                    operation.column
                )
            # ... 其他操作
    
    return state
```

## 🚀 未来扩展

### 1. 迁移应用

实现 `er_migrate` 命令，应用 ER 迁移到数据库：

```bash
^uv run python manage.py er_migrate blog
^uv run python manage.py er_migrate blog --fake
^uv run python manage.py er_migrate blog 0001
```

### 2. 迁移回滚

支持迁移回滚：

```bash
^uv run python manage.py er_migrate blog zero
^uv run python manage.py er_migrate blog 0001
```

### 3. 迁移合并

合并多个迁移文件：

```bash
^uv run python manage.py er_squashmigrations blog 0001 0005
```

### 4. 自动检测

自动检测 Django models 变更：

```bash
^uv run python manage.py er_makemigrations --auto-detect
```

### 5. 迁移验证

验证迁移的正确性：

```bash
^uv run python manage.py er_checkmigrations blog
```

### 6. 数据迁移

支持数据迁移操作：

```yaml
operations:
  - type: RunPython
    code: |
      def migrate_data(apps, schema_editor):
          User = apps.get_model('blog', 'User')
          # ... 数据迁移逻辑
```

## 🔒 安全考虑

1. **SQL 注入**: 使用参数化查询
2. **权限检查**: 验证用户权限
3. **数据验证**: 使用 Pydantic 验证
4. **事务管理**: 确保原子性操作

## 📈 性能优化

1. **延迟加载**: 只在需要时加载 models
2. **缓存**: 缓存 ER 模型和迁移状态
3. **批量操作**: 批量处理多个 models
4. **索引优化**: 自动生成索引建议

## 🧪 测试策略

1. **单元测试**: 测试每个组件
2. **集成测试**: 测试完整工作流
3. **端到端测试**: 测试 management commands
4. **性能测试**: 测试大型项目的性能

## 📝 代码管理

### 目录组织

```
src/x007007007/er_django/
├── __init__.py              # 公共 API
├── apps.py                  # Django 集成
├── introspector.py          # 内省工具（独立）
├── parser.py                # 解析器（依赖 introspector）
└── management/              # Django commands
    └── commands/
        ├── er_export.py     # 导出命令
        ├── er_makemigrations.py  # 迁移生成
        └── er_showmigrations.py  # 状态显示
```

### 依赖关系

```
management commands
    ↓
parser.py
    ↓
introspector.py
    ↓
Django models
```

### 版本控制

- 遵循语义化版本
- 与 er-migrate 版本保持同步
- 向后兼容性保证

## 🤝 与现有系统集成

### 与 er-migrate 集成

```python
# 使用相同的数据结构
from x007007007.er_migrate.models import Migration, Operation
from x007007007.er_migrate.converter import ERConverter
from x007007007.er_migrate.differ import MigrationDiffer
from x007007007.er_migrate.generator import MigrationGenerator
```

### 与 er 集成

```python
# 使用相同的 ER 模型
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers import JinjaRenderer
```

## 📚 参考资料

- [Django Models 文档](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Migrations 文档](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [ER Migrate 设计文档](../er_migrate/README.md)
- [ER 模型文档](../er/README.md)

## 🎯 总结

ER Django 插件通过以下设计实现了目标：

1. ✅ **模块化设计**: 清晰的职责分离
2. ✅ **Django 集成**: 原生 management commands
3. ✅ **命名空间映射**: App → Namespace
4. ✅ **完整功能**: 支持所有 er-migrate 功能
5. ✅ **可扩展性**: 易于添加新功能
6. ✅ **类型安全**: 完整的类型提示
7. ✅ **测试覆盖**: 全面的测试用例

这个设计提供了一个强大、灵活、易用的 Django 集成方案。
