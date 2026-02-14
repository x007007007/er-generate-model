# Database Migration Evolution Example

本目录展示了一个博客系统从简单到复杂，再到重构的完整演进过程，包含 8 个版本。

## 演进概述

这个示例展示了真实项目中数据库模型的演进过程，包括：
- 添加新表和字段
- 修改现有结构
- 重命名表和字段
- 删除不再需要的功能

## 版本列表

| 版本 | 目录 | 主要变更 | 操作类型 |
|------|------|---------|---------|
| v1 | [01-initial](01-initial/) | 创建 User 表 | CreateTable |
| v2 | [02-add-email](02-add-email/) | 添加 email 字段 | AddColumn, AddIndex |
| v3 | [03-add-posts](03-add-posts/) | 创建 Post 表 | CreateTable, AddForeignKey |
| v4 | [04-add-comments](04-add-comments/) | 创建 Comment 表 | CreateTable, AddForeignKey |
| v5 | [05-enhance-features](05-enhance-features/) | 添加业务字段 | AddColumn |
| v6 | [06-anonymous-comments](06-anonymous-comments/) | 评论匿名化 | RemoveForeignKey, AddColumn |
| v7 | [07-rename-to-article](07-rename-to-article/) | 重命名 Post 为 Article | RenameTable, AlterColumn |
| v8 | [08-remove-comments](08-remove-comments/) | 删除评论功能 | DropTable |

## 详细演进过程

### Version 1: 初始版本
最简单的起点，只有用户表。

**实体**: User  
**字段**: id, username, created_at

### Version 2: 添加邮箱
为用户添加邮箱功能。

**变更**: User 表添加 email 字段（唯一）

### Version 3: 添加文章功能
引入博客的核心功能 - 文章。

**新实体**: Post  
**关系**: User 写 Post（一对多）

### Version 4: 添加评论功能
允许用户对文章发表评论。

**新实体**: Comment  
**关系**: 
- User 写 Comment（一对多）
- Post 有 Comment（一对多）

### Version 5: 增强功能
添加更多业务字段以支持实际需求。

**变更**:
- Post 添加 published_at, view_count
- Comment 添加 is_approved

### Version 6: 评论匿名化
允许匿名用户发表评论。

**变更**:
- Comment 的 author_id 变为可选
- 删除 User 到 Comment 的强制关系

### Version 7: 重命名为 Article
为了更好的语义，将 Post 重命名为 Article。

**变更**:
- Post 表重命名为 Article
- 所有相关的外键引用更新

### Version 8: 删除评论功能
简化系统，移除评论功能。

**变更**:
- 删除 Comment 表
- 只保留 User 和 Article

## 使用方法

### 查看单个版本

每个版本目录包含：
- `blog.mmd` - 该版本的 Mermaid ER 图
- `README.md` - 版本说明和变更详情

### 生成代码

从任意版本生成 Django 或 SQLAlchemy 代码：

```bash
# 生成 Django 模型
uv run er-convert convert 01-initial/blog.mmd -t mermaid -f django -d output/

# 生成 SQLAlchemy 模型
uv run er-convert convert 03-add-posts/blog.mmd -t mermaid -f sqlalchemy -d output/

# 生成 TOML 格式
uv run er-convert convert 05-enhance-features/blog.mmd -t mermaid -o output.toml
```

### 对比版本差异

```bash
# 对比两个版本的 ER 图
diff 01-initial/blog.mmd 02-add-email/blog.mmd

# 使用 Mermaid 可视化对比
# 在支持 Mermaid 的编辑器中打开两个文件并排查看
```

## 学习要点

### 1. 渐进式设计
从最简单的模型开始，逐步添加功能，而不是一开始就设计复杂的系统。

### 2. 关系管理
理解如何添加、修改和删除实体间的关系。

### 3. 重构技巧
学习如何安全地重命名表和字段，以及如何删除不再需要的功能。

### 4. 向后兼容
每个版本都应该考虑如何从前一个版本迁移，保持数据完整性。

## 迁移操作覆盖

这个演进示例覆盖了以下数据库迁移操作：

- ✅ **CreateTable** - 创建新表（v1, v3, v4）
- ✅ **DropTable** - 删除表（v8）
- ✅ **RenameTable** - 重命名表（v7）
- ✅ **AddColumn** - 添加列（v2, v5, v6）
- ✅ **RemoveColumn** - 删除列（v6）
- ✅ **AlterColumn** - 修改列属性（v5）
- ✅ **AddForeignKey** - 添加外键（v3, v4）
- ✅ **RemoveForeignKey** - 删除外键（v6）
- ✅ **AddIndex** - 添加索引（v2）

## 实际应用

这个演进模式反映了真实项目中的常见场景：

1. **MVP 阶段** (v1-v3) - 快速构建核心功能
2. **功能扩展** (v4-v5) - 根据用户需求添加新功能
3. **优化调整** (v6) - 根据实际使用情况调整设计
4. **重构** (v7) - 改进命名和结构
5. **简化** (v8) - 移除不常用的功能

## 相关资源

- [Django Migrations 文档](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [SQLAlchemy Alembic 文档](https://alembic.sqlalchemy.org/)
- [数据库迁移最佳实践](https://www.prisma.io/dataguide/types/relational/migration-strategies)

## 下一步

- 尝试添加自己的 v9 版本
- 将这些 ER 图转换为实际的数据库迁移
- 在真实项目中应用这种渐进式设计方法
