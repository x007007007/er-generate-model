# Django ORM Examples

本目录包含从 TOML 转换为 Django ORM 模型的示例。

## Django ORM 特点

Django ORM 是 Django 框架的对象关系映射系统，特点包括：

- 使用 Python 类定义数据模型
- 自动生成数据库迁移
- 内置管理后台支持
- 丰富的查询 API
- 支持多种数据库后端

## 示例列表

### [01-simple-model](01-simple-model/)
最简单的单表模型示例，包含：
- 基本字段类型（int, string, datetime）
- 主键定义
- 唯一约束

### [02-relationships](02-relationships/)
多表关系模型示例，包含：
- 外键关系（ForeignKey）
- 一对多关系
- 关联查询

### [03-all-data-types](03-all-data-types/)
完整数据类型展示，包含：
- 所有支持的字段类型
- 字段选项（nullable, default, unique 等）
- 复杂字段类型（JSON, UUID 等）

## 转换命令

```bash
# 基本转换
uv run er-gen-tool convert convert input.toml -f django -d output/

# 指定 app label
uv run er-gen-tool convert convert input.toml -f django -d output/ -a myapp

# 指定表前缀
uv run er-gen-tool convert convert input.toml -f django -d output/ -p prefix_
```

## 输出结构

转换后会生成 Python 包结构：

```
output/
├── __init__.py      # 包初始化文件
└── models.py        # Django 模型定义
```

## 使用生成的模型

1. 将生成的包复制到你的 Django 项目中
2. 在 `settings.py` 中添加 app
3. 运行 `python manage.py makemigrations`
4. 运行 `python manage.py migrate`

## Django 字段映射

| TOML 类型 | Django 字段 |
|-----------|-------------|
| int | IntegerField |
| bigint | BigIntegerField |
| string | CharField |
| text | TextField |
| boolean | BooleanField |
| datetime | DateTimeField |
| date | DateField |
| time | TimeField |
| uuid | UUIDField |
| json | JSONField |
| decimal | DecimalField |
| float | FloatField |

## 相关资源

- [Django 官方文档](https://docs.djangoproject.com/)
- [Django Models 文档](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [完整 Django 项目示例](../../full-projects/django-blog/)
