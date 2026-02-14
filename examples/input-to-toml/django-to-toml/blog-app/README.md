# Blog App - Django to TOML

这个示例展示如何将 Django 模型转换为 TOML 格式。

## 示例内容

一个简化的博客应用，包含：
- **Category** - 文章分类
- **Post** - 博客文章
- **Comment** - 文章评论

## 文件说明

- `models/models.py` - Django 模型定义
- `models/__init__.py` - Python 包初始化文件
- `output.toml` - 转换后的 TOML 文件

## Django 模型特点

- 使用 Django ORM 的标准字段类型
- 包含 ForeignKey 关系
- 包含字段选项（max_length, unique, null, blank 等）
- 包含 Meta 类配置

## 转换说明

当前示例中的 `output.toml` 是手动创建的，展示了预期的 TOML 输出格式。

未来可能支持的转换命令：
```bash
# 注意：此命令可能需要工具支持
uv run er-convert convert models/ -t django -o output.toml
```

## 学习要点

1. **Django 字段映射** - 了解 Django 字段如何映射到 TOML 类型
2. **关系转换** - ForeignKey 如何表示为 TOML 关系
3. **字段选项** - Django 的 null, blank, default 等选项如何转换
4. **Meta 信息** - db_table, ordering 等元数据的处理

## TOML 输出结构

```toml
[entities.Category]
comment = "文章分类"
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "name", type = "string", max_length = 100, unique = true},
    # ...
]

[[relationships]]
left_entity = "Category"
right_entity = "Post"
relation_type = "one-to-many"
right_column = "category_id"
```

## 使用场景

- 已有 Django 项目，想要导出模型定义
- 需要将 Django 模型迁移到其他平台
- 想要生成数据模型文档

## 下一步

转换为 TOML 后，可以：
- 转换为 SQLAlchemy：`uv run er-convert convert output.toml -f sqlalchemy -d models/`
- 生成 Mermaid 图：`uv run er-convert convert output.toml -f mermaid -o diagram.mmd`
- 作为文档保存和版本控制
