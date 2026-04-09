# TOML 模型继承与抽象模型设计指南

本文档介绍了在 `er-gen-core` 中，如何使用 TOML 文件来表示模型（Model）的继承关系、抽象模型（无表的模型）以及模型描述信息。

## 1. 核心概念

在 TOML 配置中，模型系统主要由两部分组成：
- **`[templates]`**：用于定义**抽象模型（Abstract Models）**。它们不对应数据库中的真实表，而是作为字段集合的模板（Mixins/基类），供其他实体继承。
- **`[entities]`**：用于定义**具体实体模型（Concrete Models）**。它们映射到数据库中的真实表，必须包含 `table_name` 属性，并且可以继承一个或多个模板。

无论是模板还是实体，只要是“模型”，都可以通过 `comment` 属性添加描述信息。

## 2. 抽象模型 (Templates)

对于没有对应数据库表的抽象模型，需要定义在 `[templates]` 层级下。它们主要用于复用通用的字段（如：创建时间、更新时间、通用状态等）。

### 支持的属性
- `export_path`: (可选) 导出或引用的 Python 模块路径，用于代码生成。
- `package`: (可选) 包路径。
- `comment`: (可选) **模型的描述信息**。对于抽象模型同样适用。
- `columns`: (必填) 该抽象模型包含的字段列表。

### 示例
```toml
[templates.TimestampMixin]
export_path = "common.mixins"
comment = "包含创建和更新时间的通用抽象模型"
columns = [
    { name = "created_at", type = "datetime", comment = "记录创建时间" },
    { name = "updated_at", type = "datetime", comment = "记录更新时间" }
]

[templates.SoftDeleteMixin]
export_path = "common.mixins"
comment = "软删除抽象模型"
columns = [
    { name = "is_deleted", type = "boolean", default = false, comment = "是否已被软删除" }
]
```

## 3. 具体实体与模型继承 (Entities & Extends)

具体的实体定义在 `[entities]` 层级下。通过配置 `extends` 属性，实体可以继承多个抽象模型（模板）的字段。

### 支持的属性
- `table_name`: (必填) 数据库中的真实表名。
- `extends`: (可选) **模型继承**。一个包含要继承的模板名称的数组（例如 `["TemplateA", "TemplateB"]`）。
- `comment`: (可选) **模型的描述信息**。
- `columns`: (必填) 实体自身的特有字段列表。

### 继承行为
- **多继承支持**：实体可以同时继承多个模板，按数组顺序依次合并。
- **字段覆盖**：如果实体自身的字段与继承的模板字段同名，实体自身的字段定义将覆盖模板的定义。
- **解析模式**：根据解析器的配置（`reference` 或 `flatten`），继承的字段可以被展平到实体内部，或作为 Python 基类进行继承引用。

### 示例
```toml
[entities.User]
table_name = "sys_user"
# 继承多个抽象模型
extends = ["TimestampMixin", "SoftDeleteMixin"]
comment = "系统用户模型，存储用户基本信息"
columns = [
    { name = "id", type = "int", is_pk = true, comment = "用户主键" },
    { name = "username", type = "string", max_length = 50, unique = true, comment = "登录用户名" },
    { name = "password", type = "string", max_length = 128, comment = "加密后的密码" }
]

[entities.Post]
table_name = "blog_post"
extends = ["TimestampMixin"]
comment = "博客文章模型"
columns = [
    { name = "id", type = "int", is_pk = true },
    { name = "title", type = "string", max_length = 200, comment = "文章标题" },
    { name = "content", type = "text", comment = "文章内容" }
]
```

## 4. 总结

1. **模型继承**：通过 `[entities.<Name>.extends]` 数组实现，可以同时继承多个模板。
2. **抽象模型**：没有数据表的模型定义在 `[templates]` 中，作为复用字段的基类（Mixin）。
3. **模型描述**：无论是 `[templates]` 还是 `[entities]`，只要是模型，都可以通过顶层的 `comment = "..."` 属性来声明模型描述，生成代码时将作为类的文档注释或 Meta 配置中的 verbose_name 保留。
