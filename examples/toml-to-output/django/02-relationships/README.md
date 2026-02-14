# Relationships Example - Django

这个示例展示如何在 TOML 中定义表关系，并转换为 Django 的 ForeignKey。

## 示例内容

两个相关的模型：
- **User** - 用户表
- **Post** - 文章表（通过 author_id 关联到 User）

关系：User 可以写多篇 Post（一对多关系）

## 文件说明

- `input.toml` - 包含关系定义的 TOML 文件
- `output/models.py` - 生成的 Django 模型，包含 ForeignKey
- `output/__init__.py` - Python 包初始化文件

## 转换命令

```bash
uv run er-convert convert input.toml -f django -d output/
```

## 学习要点

1. **外键定义** - 使用 `is_fk = true` 标记外键字段
2. **关系声明** - 在 `[[relationships]]` 部分定义关系
3. **关系类型** - `one-to-many` 表示一对多关系
4. **related_name** - Django 中的反向查询名称

## TOML 关系语法

```toml
[[relationships]]
left_entity = "User"
right_entity = "Post"
relation_type = "one-to-many"
right_column = "author_id"
```

## 生成的 Django 代码

```python
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
```

## 下一步

- [03-all-data-types](../03-all-data-types/) - 了解所有支持的数据类型
- [../../sqlalchemy/02-relationships/](../../sqlalchemy/02-relationships/) - 对比 SQLAlchemy 的关系定义
