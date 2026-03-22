# Design Document: SQLAlchemy Field Attributes Fix

## Overview

本设计文档描述了修复 Django 到 SQLAlchemy 模型转换过程中字段属性丢失问题的技术方案。问题的根本原因在于 Jinja2 模板在渲染 SQLAlchemy Column 定义时，未能将 `unique`、`indexed` 和 `nullable` 属性完整地添加到参数列表中。

当前系统分为两个阶段：
1. **解析阶段**：Django 模型解析器（DjangoModelParser）正确提取字段属性到 Column 对象
2. **渲染阶段**：SQLAlchemy 渲染器使用 Jinja2 模板生成代码，但模板逻辑不完整

修复方案将专注于更新 Jinja2 模板，确保所有字段属性都被正确渲染。

## Architecture

### 系统组件

```
Django Model
     ↓
DjangoModelParser (解析器)
     ↓
ERModel (中间表示)
  - Entity
  - Column (包含 unique, indexed, nullable 等属性)
  - Relationship
     ↓
SQLAlchemyRenderer (渲染器)
     ↓
Jinja2 Templates (需要修复)
  - sqlalchemy_single_model.j2
  - sqlalchemy_model.j2
     ↓
SQLAlchemy Code (生成的代码)
```

### 问题定位

通过代码分析，发现问题出现在两个 Jinja2 模板文件中：

1. **sqlalchemy_single_model.j2**：用于单文件渲染
2. **sqlalchemy_model.j2**：用于多文件渲染

两个模板都存在相同的问题：在构建 `param_list` 时，只包含了 `primary_key`、`nullable`、`default` 和 `comment`，但遗漏了 `unique` 和 `index`。

### 模板逻辑分析

当前模板有两个代码路径处理字段：

**路径 1：外键字段（is_fk=True）**
```jinja2
{{ col.name }} = Column(Integer, ForeignKey('...'), nullable=..., comment=...)
```
- 直接内联参数，未使用 param_list
- 缺少 unique 和 index

**路径 2：普通字段（is_fk=False）**
```jinja2
{%- set param_list = [] %}
{%- if col.is_pk %}
{%- set _ = param_list.append('primary_key=True') %}
{%- endif %}
{%- if not col.nullable %}
{%- set _ = param_list.append('nullable=' + col.nullable|string) %}
{%- endif %}
{%- if col.default is not none %}
{%- set _ = param_list.append('default=' + ...) %}
{%- endif %}
{%- if col.comment %}
{%- set _ = param_list.append('comment=' + ...) %}
{%- endif %}
```
- 使用 param_list 构建参数
- 缺少 unique 和 index

## Components and Interfaces

### Column 数据模型

```python
@dataclass
class Column:
    name: str
    type: str
    db_column: str
    is_pk: bool = False
    is_fk: bool = False
    nullable: bool = True
    comment: Optional[str] = None
    default: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    unique: bool = False      # 需要渲染
    indexed: bool = False     # 需要渲染为 index=True
```

### 模板修复方案

需要在两个位置添加 unique 和 index 参数：

1. **外键字段路径**：将内联参数改为使用 param_list
2. **普通字段路径**：在 param_list 构建逻辑中添加 unique 和 index

### 参数顺序规范

为了保持代码的一致性和可读性，定义以下参数顺序：

1. `primary_key` - 主键标识
2. `nullable` - 可空性约束
3. `unique` - 唯一性约束
4. `index` - 索引标识
5. `default` - 默认值
6. `comment` - 注释

## Data Models

### 模板变量

```jinja2
col: Column 对象
  - col.name: 字段名
  - col.type: 字段类型
  - col.is_pk: 是否主键
  - col.is_fk: 是否外键
  - col.nullable: 是否可空
  - col.unique: 是否唯一
  - col.indexed: 是否有索引
  - col.default: 默认值
  - col.comment: 注释
  - col.max_length: 最大长度

param_list: 参数列表
  - 用于构建 Column() 的参数
  - 格式：['primary_key=True', 'nullable=False', ...]
```

### 渲染逻辑

```python
# 伪代码
def build_param_list(col):
    params = []
    
    if col.is_pk:
        params.append('primary_key=True')
    
    if not col.nullable:
        params.append(f'nullable={col.nullable}')
    
    if col.unique:  # 新增
        params.append('unique=True')
    
    if col.indexed:  # 新增
        params.append('index=True')
    
    if col.default is not None:
        params.append(f'default={serialize(col.default)}')
    
    if col.comment:
        params.append(f'comment={serialize(col.comment)}')
    
    return params
```

## Correctness Properties

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: Unique 属性渲染

*对于任何* Column 对象，如果其 unique 属性为 True，则生成的 SQLAlchemy 代码必须包含 `unique=True` 参数；如果为 False，则不应包含 unique 参数

**Validates: Requirements 1.1, 1.2**

### Property 2: Index 属性渲染

*对于任何* Column 对象，如果其 indexed 属性为 True，则生成的 SQLAlchemy 代码必须包含 `index=True` 参数；如果为 False，则不应包含 index 参数

**Validates: Requirements 2.1, 2.2**

### Property 3: Nullable 属性渲染一致性

*对于任何* Column 对象，如果其 nullable 属性为 False，则生成的 SQLAlchemy 代码必须包含 `nullable=False` 参数，无论字段是否有 max_length；如果为 True，则不应包含 nullable 参数

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: 多属性组合渲染

*对于任何* 具有多个非默认属性（unique, indexed, nullable, default, comment）的 Column 对象，生成的 SQLAlchemy 代码必须包含所有这些属性的参数

**Validates: Requirements 1.3, 2.3**

### Property 5: 外键字段属性保留

*对于任何* 外键 Column 对象（is_fk=True），生成的 SQLAlchemy 代码必须包含该字段的所有非默认属性（unique, index, nullable）

**Validates: Requirements 6.3**

### Property 6: 参数顺序一致性

*对于任何* 生成的 Column 定义，参数必须按照固定顺序排列：primary_key, nullable, unique, index, default, comment

**Validates: Requirements 7.1**

### Property 7: 参数格式正确性

*对于任何* 包含多个参数的 Column 定义，生成的代码必须使用逗号和空格正确分隔参数

**Validates: Requirements 7.3**

### Property 8: 解析器属性提取完整性

*对于任何* Django 字段，解析器必须正确提取 unique（从 unique）、indexed（从 db_index）和 nullable（从 null）属性到 Column 对象

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 9: 端到端属性保留

*对于任何* Django 模型，从解析到渲染的完整流程必须保留所有字段的 unique、indexed 和 nullable 属性

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 10: 模板一致性

*对于任何* Column 对象，使用 sqlalchemy_single_model.j2 和 sqlalchemy_model.j2 模板生成的代码必须包含相同的字段属性

**Validates: Requirements 6.1, 6.2**

### Property 11: 带 max_length 字段的属性保留

*对于任何* 带有 max_length 的 Column 对象，生成的 SQLAlchemy 代码必须在类型参数之后正确包含所有字段属性

**Validates: Requirements 6.4**

## Error Handling

### 模板渲染错误

- **场景**：Column 对象缺少必需属性
- **处理**：Jinja2 会抛出 UndefinedError
- **预防**：确保 Column 数据类的所有字段都有默认值

### 属性值类型错误

- **场景**：unique、indexed、nullable 不是布尔值
- **处理**：Python 的类型系统会在运行时检测
- **预防**：使用 dataclass 和类型注解

### 参数序列化错误

- **场景**：default 或 comment 值无法序列化
- **处理**：使用 code_value 过滤器处理
- **预防**：在解析阶段验证值的可序列化性

## Testing Strategy

### 双重测试方法

本项目将采用单元测试和属性测试相结合的方法：

- **单元测试**：验证特定示例、边缘情况和错误条件
- **属性测试**：验证跨所有输入的通用属性

两者是互补的，共同提供全面的覆盖：
- 单元测试捕获具体的错误
- 属性测试验证一般正确性

### 单元测试策略

单元测试应专注于：
- 特定示例，展示正确行为
- 组件之间的集成点
- 边缘情况和错误条件

避免编写过多的单元测试 - 属性测试会处理大量输入的覆盖。

### 属性测试配置

- **测试库**：使用 Python 的 `hypothesis` 库
- **迭代次数**：每个属性测试最少 100 次迭代
- **标签格式**：`Feature: sqlalchemy-field-attributes-fix, Property {number}: {property_text}`
- **实现规则**：每个正确性属性必须由单个属性测试实现

### 测试覆盖范围

1. **解析阶段测试**
   - 验证 Django 字段属性被正确提取
   - 测试各种字段类型和属性组合

2. **渲染阶段测试**
   - 验证模板生成正确的 SQLAlchemy 代码
   - 测试参数顺序和格式

3. **端到端测试**
   - 验证完整的转换流程
   - 测试真实的 Django 模型

4. **回归测试**
   - 使用现有的测试文件 test_field_attributes.py
   - 确保修复不会破坏现有功能
