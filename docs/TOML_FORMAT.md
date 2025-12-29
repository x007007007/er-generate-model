# TOML ER图格式文档

## 概述

TOML格式ER图支持**继承和模板**功能，可以显著减少重复字段定义，让ER图更简洁易维护。

## 为什么选择TOML？

- ✅ **类型明确**：字符串、整数、布尔值类型清晰
- ✅ **语法简单**：不易出现缩进错误
- ✅ **结构化数据友好**：适合ER图这种结构化数据
- ✅ **格式校验**：使用Pydantic进行数据验证

## 基本语法

### 实体定义

```toml
[entities.USER]
comment = "User entity"
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "username", type = "string", unique = true},
    {name = "email", type = "string"},
]
```

### 关系定义

```toml
[[relationships]]
left = "USER"
right = "POST"
type = "one-to-many"
left_label = "writes"
```

## 模板和继承

### 定义模板

可以定义多个可复用的模板：

```toml
[templates.create_update_time]
columns = [
    {name = "created_at", type = "datetime", comment = "Creation timestamp"},
    {name = "updated_at", type = "datetime", comment = "Update timestamp"},
]

[templates.enable]
columns = [
    {name = "is_enabled", type = "boolean", comment = "Whether the record is enabled"},
]

[templates.name]
columns = [
    {name = "name", type = "string", comment = "Name field"},
]
```

### 继承单个模板

```toml
[entities.USER]
extends = "create_update_time"  # 继承单个模板
columns = [
    {name = "username", type = "string"},
    {name = "email", type = "string"},
]
```

### 继承多个模板（推荐）

`extends` 可以是数组，支持继承多个模板：

```toml
[entities.USER]
extends = ["create_update_time", "enable", "name"]  # 继承多个模板
columns = [
    {name = "username", type = "string"},
    {name = "email", type = "string"},
]
```

**合并规则**：
- 按 `extends` 数组的顺序依次合并模板字段
- 如果多个模板有同名字段，**后面的模板会覆盖前面的**
- 实体自己的字段会覆盖所有继承的字段

### 字段覆盖

继承的字段可以被覆盖：

```toml
[templates.base]
columns = [
    {name = "name", type = "string", comment = "Base name"},
]

[entities.USER]
extends = "base"
columns = [
    {name = "name", type = "string", comment = "Overridden name"},  # 覆盖模板中的name字段
]
```

### 常见模板组合

```toml
# 常用模板定义
[templates.create_update_time]
columns = [
    {name = "created_at", type = "datetime"},
    {name = "updated_at", type = "datetime"},
]

[templates.enable]
columns = [
    {name = "is_enabled", type = "boolean"},
]

[templates.name]
columns = [
    {name = "name", type = "string"},
]

# 使用组合
[entities.PRODUCT]
extends = ["create_update_time", "enable", "name"]
columns = [
    {name = "price", type = "decimal"},
]
```

## 完整示例

```toml
# 定义可复用的字段模板
[templates.create_update_time]
columns = [
    {name = "created_at", type = "datetime"},
    {name = "updated_at", type = "datetime"},
]

[templates.enable]
columns = [
    {name = "is_enabled", type = "boolean"},
]

[templates.name]
columns = [
    {name = "name", type = "string"},
]

# 实体定义 - 使用多模板继承
[entities.USER]
extends = ["create_update_time", "enable"]
comment = "User entity"
columns = [
    {name = "username", type = "string", unique = true},
    {name = "email", type = "string"},
]

[entities.POST]
extends = ["create_update_time", "enable"]
comment = "Blog post"
columns = [
    {name = "title", type = "string"},
    {name = "content", type = "text"},
]

[entities.TAG]
extends = ["create_update_time", "name"]
comment = "Tag entity"
columns = []

# 关系定义
[[relationships]]
left = "USER"
right = "POST"
type = "one-to-many"
left_label = "writes"
```

## 字段属性

字段支持以下属性：

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `name` | string | 字段名（必需） | - |
| `type` | string | 字段类型（必需） | - |
| `is_pk` | boolean | 是否主键 | `false` |
| `is_fk` | boolean | 是否外键 | `false` |
| `nullable` | boolean | 是否可空 | `true` |
| `unique` | boolean | 是否唯一 | `false` |
| `indexed` | boolean | 是否索引 | `false` |
| `comment` | string | 字段注释 | `null` |
| `default` | string | 默认值 | `null` |
| `max_length` | integer | 最大长度 | `null` |
| `precision` | integer | 精度（decimal） | `null` |
| `scale` | integer | 小数位数（decimal） | `null` |

## 关系类型

支持以下关系类型：

| 类型值 | 说明 |
|--------|------|
| `one-to-one` 或 `1:1` | 一对一 |
| `one-to-many` 或 `1:N` | 一对多 |
| `many-to-one` 或 `N:1` | 多对一 |
| `many-to-many` 或 `N:M` | 多对多 |

## 关系属性

关系支持以下属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `left` | string | 左实体名（必需） |
| `right` | string | 右实体名（必需） |
| `type` | string | 关系类型（必需） |
| `left_label` | string | 左标签 |
| `right_label` | string | 右标签 |
| `left_column` | string | 左实体外键列名 |
| `right_column` | string | 右实体外键列名 |
| `left_cardinality` | string | 左基数（如 "1", "0..1", "*"） |
| `right_cardinality` | string | 右基数 |

## 使用方式

### CLI使用

```bash
# 解析TOML格式并生成Django模型
er-convert input.toml -t toml -f django

# 解析TOML格式并转换为Mermaid
er-convert input.toml -t toml -f mermaid

# 解析TOML格式并转换为PlantUML
er-convert input.toml -t toml -f plantuml
```

### 代码中使用

```python
from x007007007.er.parser.toml_parser import TomlERParser

parser = TomlERParser()
with open('diagram.toml', 'r') as f:
    model = parser.parse(f.read())
```

## 优势

1. **减少重复**：通过模板和继承，避免重复定义相同的字段
2. **易于维护**：修改模板，所有继承的实体自动更新
3. **类型安全**：TOML类型明确，减少错误
4. **格式校验**：解析时自动验证数据格式
5. **可读性强**：结构清晰，易于理解

## 注意事项

1. 模板必须在实体之前定义（或至少在被引用之前）
2. 字段覆盖时，后面的定义会覆盖前面的定义
3. 关系引用的实体必须存在
4. 模板名称不能与实体名称冲突

