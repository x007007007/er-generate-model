# SQLAlchemy ORM Examples

本目录包含从 TOML 转换为 SQLAlchemy ORM 模型的示例。

## SQLAlchemy ORM 特点

SQLAlchemy 是 Python 最流行的 ORM 框架之一，特点包括：

- 灵活的映射方式（声明式、经典式）
- 强大的查询构造器
- 支持多种数据库后端
- 事务管理
- 连接池管理

## 示例列表

### [01-simple-model](01-simple-model/)
最简单的单表模型示例，包含：
- 基本字段类型（Integer, String, DateTime）
- 主键定义
- 唯一约束

### [02-relationships](02-relationships/)
多表关系模型示例，包含：
- 外键关系（ForeignKey）
- 一对多关系（relationship）
- 关联查询

### [03-all-data-types](03-all-data-types/)
完整数据类型展示，包含：
- 所有支持的字段类型
- 字段选项（nullable, default, unique 等）
- 复杂字段类型（JSON, UUID 等）

## 转换命令

```bash
# 基本转换
uv run er-gen-tool convert convert input.toml -f sqlalchemy -d output/

# 指定表前缀
uv run er-gen-tool convert convert input.toml -f sqlalchemy -d output/ -p prefix_
```

## 输出结构

转换后会生成 Python 包结构：

```
output/
├── __init__.py      # 包初始化文件
└── models.py        # SQLAlchemy 模型定义
```

## 使用生成的模型

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from output.models import Base, User, Post

# 创建数据库引擎
engine = create_engine('sqlite:///example.db')

# 创建所有表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 使用模型
user = User(username='john', email='john@example.com')
session.add(user)
session.commit()
```

## SQLAlchemy 字段映射

| TOML 类型 | SQLAlchemy 类型 |
|-----------|-----------------|
| int | Integer |
| bigint | BigInteger |
| string | String |
| text | Text |
| boolean | Boolean |
| datetime | DateTime |
| date | Date |
| time | Time |
| uuid | UUID (with UUID type) |
| json | JSON |
| decimal | Numeric |
| float | Float |

## 声明式基类

生成的模型使用 SQLAlchemy 的声明式基类：

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    # ...
```

## 相关资源

- [SQLAlchemy 官方文档](https://www.sqlalchemy.org/)
- [SQLAlchemy ORM 教程](https://docs.sqlalchemy.org/en/stable/orm/tutorial.html)
- [SQLAlchemy 核心概念](https://docs.sqlalchemy.org/en/stable/core/)
