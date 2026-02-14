# Simple Model Example - Django

这是最简单的 TOML 到 Django 转换示例，适合初学者入门。

## 示例内容

一个简单的 User 模型，包含基本字段：
- `id` - 整数主键
- `username` - 唯一用户名
- `email` - 邮箱地址
- `created_at` - 创建时间

## 文件说明

- `input.toml` - TOML 格式的模型定义
- `output/models.py` - 生成的 Django 模型代码
- `output/__init__.py` - Python 包初始化文件

## 转换命令

```bash
uv run er-convert convert input.toml -f django -d output/
```

## 学习要点

1. **TOML 基本结构** - 了解如何定义实体和字段
2. **字段类型映射** - TOML 类型如何映射到 Django 字段
3. **主键定义** - 使用 `is_pk = true` 定义主键
4. **唯一约束** - 使用 `unique = true` 添加唯一约束

## 下一步

学习完本示例后，可以继续学习：
- [02-relationships](../02-relationships/) - 了解如何定义表关系
- [03-all-data-types](../03-all-data-types/) - 了解所有支持的数据类型
