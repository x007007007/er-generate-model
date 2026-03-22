# Django Inheritance Field Preservation Bugfix Design

## Overview

当 Django ORM models 通过 TOML 中间格式转换为 SQLAlchemy models 时，如果 TOML 中的 entity 包含 `extends` 字段（表示继承关系），但这些父类/mixin 类没有在 `templates` 部分定义（即没有 `export_path`），则转换后的 SQLAlchemy model 会丢失从这些父类继承的字段。

问题的根本原因在于 TOML parser 的 `_parse_entities` 方法中，当处理 `extends` 字段时，只有在 `templates` 字典中存在的模板才会展开其字段。对于不在 `templates` 中的父类（如 Django 内置类或第三方库的 mixin 类），代码会跳过字段展开，导致这些继承字段在最终的 SQLAlchemy model 中丢失。

修复策略提供两种继承处理模式，用户可以通过命令行参数选择：

1. **引用模式（Reference Mode）**: 将继承的 model 生成为独立的 mixin/base 类文件，子类通过 Python 继承机制引用这些类。字段通过继承获得，不在子类中重复定义。这是传统的面向对象方式。

2. **展开模式（Flatten Mode）**: 不生成独立的 mixin 类文件，将所有继承的字段直接展开到子类的字段定义中。这是扁平化处理，不使用 Python 继承，所有字段都显式定义在子类中。

两种模式各有优势：引用模式保持代码 DRY 原则和继承语义，展开模式使每个 model 文件自包含且易于理解。

## Glossary

- **Bug_Condition (C)**: 触发 bug 的条件 - 当 TOML entity 的 `extends` 字段引用了在 `templates` 中定义但没有 `export_path` 的父类时，这些父类的字段不会被展开
- **Property (P)**: 期望的行为 - 根据用户选择的继承模式，正确处理继承字段（引用模式：生成独立类文件并继承；展开模式：直接展开所有字段）
- **Preservation**: 现有的字段类型映射、关系生成、Django 风格命名等功能必须保持不变
- **引用模式（Reference Mode）**: 继承处理模式之一，生成独立的 mixin/base 类文件，子类通过 Python 继承引用
- **展开模式（Flatten Mode）**: 继承处理模式之一，将所有继承字段直接展开到子类中，不使用 Python 继承
- **TomlERParser**: `packages/er-gen-core/src/x007007007/er/parser/toml_parser.py` 中的类，负责解析 TOML 格式并构建 ERModel
- **_parse_entities**: TomlERParser 中的方法，处理实体定义和继承关系
- **templates**: TOML 文件中的 `[templates]` 部分，定义可复用的字段集合（mixin 类）
- **extends**: Entity 的属性，包含继承的父类/模板名称列表
- **export_path**: Template 的可选属性，指示该模板对应的 Python 模块路径（用于生成 import 语句）
- **inherited_column_names**: Jinja2 模板中的变量，用于跟踪哪些字段应该从渲染中排除（因为它们会通过 Python 继承获得）
- **inheritance_mode**: 命令行参数，控制继承处理方式（`reference` 或 `flatten`）

## Bug Details

### Fault Condition

当 TOML 文件包含以下结构时，bug 会发生：
1. Entity 的 `extends` 字段引用了一个或多个父类名称
2. 这些父类名称在 TOML 的 `templates` 部分有定义
3. 但这些 templates 没有 `export_path` 属性（意味着它们不是真实的 Python 类，只是字段集合）
4. 在这种情况下，`_parse_entities` 方法会跳过字段展开，导致生成的 SQLAlchemy model 缺少这些字段

此外，系统缺少灵活的继承处理机制，无法让用户选择如何处理继承关系（通过 Python 继承还是字段展开）。

**Formal Specification:**
```
FUNCTION isBugCondition(entity, templates, inheritance_mode)
  INPUT: entity of type Entity (from TOML), 
         templates of type Dict[str, Dict],
         inheritance_mode of type String ("reference" or "flatten")
  OUTPUT: boolean
  
  RETURN entity.extends IS NOT EMPTY
         AND EXISTS template_name IN entity.extends WHERE (
           template_name IN templates
           AND (
             (inheritance_mode = "flatten" AND templates[template_name].columns IS NOT EMPTY)
             OR
             (inheritance_mode = "reference" AND templates[template_name].export_path IS NULL)
           )
         )
         AND NOT correctlyHandledByMode(entity, templates, inheritance_mode)
END FUNCTION
```

### Examples

**Example 1: CreateModifyMixinModel 字段丢失**
- TOML 定义:
  ```toml
  [templates.CreateModifyMixinModel]
  [[templates.CreateModifyMixinModel.columns]]
  name = "created_at"
  type = "datetime"
  
  [[templates.CreateModifyMixinModel.columns]]
  name = "modified_at"
  type = "datetime"
  
  [entities.Translation]
  extends = ["CreateModifyMixinModel"]
  [[entities.Translation.columns]]
  name = "id"
  type = "bigint"
  ```
- 当前错误行为: 生成的 SQLAlchemy model 只有 `id` 字段，缺少 `created_at` 和 `modified_at`
- 期望正确行为: 生成的 SQLAlchemy model 应该包含 `id`, `created_at`, `modified_at` 三个字段

**Example 2: 多重继承字段丢失**
- TOML 定义:
  ```toml
  [templates.TimestampMixin]
  [[templates.TimestampMixin.columns]]
  name = "created_at"
  type = "datetime"
  
  [templates.SoftDeleteMixin]
  [[templates.SoftDeleteMixin.columns]]
  name = "deleted_at"
  type = "datetime"
  nullable = true
  
  [entities.User]
  extends = ["TimestampMixin", "SoftDeleteMixin"]
  [[entities.User.columns]]
  name = "username"
  type = "string"
  ```
- 当前错误行为: 生成的 SQLAlchemy model 只有 `username` 字段
- 期望正确行为: 生成的 SQLAlchemy model 应该包含 `username`, `created_at`, `deleted_at` 三个字段

**Example 3: 有 export_path 的模板（正常工作）**
- TOML 定义:
  ```toml
  [templates.BaseMixin]
  export_path = "myapp.mixins"
  [[templates.BaseMixin.columns]]
  name = "id"
  type = "bigint"
  
  [entities.Product]
  extends = ["BaseMixin"]
  [[entities.Product.columns]]
  name = "name"
  type = "string"
  ```
- 当前正确行为: 生成的 SQLAlchemy model 继承 BaseMixin 类，只定义 `name` 字段（`id` 通过 Python 继承获得）
- 期望保持不变: 这种情况应该继续正常工作

**Edge Case: 混合有无 export_path 的继承**
- TOML 定义:
  ```toml
  [templates.RealPythonClass]
  export_path = "myapp.base"
  [[templates.RealPythonClass.columns]]
  name = "id"
  type = "bigint"
  
  [templates.FieldCollectionMixin]
  # No export_path
  [[templates.FieldCollectionMixin.columns]]
  name = "created_at"
  type = "datetime"
  
  [entities.Article]
  extends = ["RealPythonClass", "FieldCollectionMixin"]
  [[entities.Article.columns]]
  name = "title"
  type = "string"
  ```
- 期望行为: 生成的 SQLAlchemy model 应该继承 RealPythonClass，定义 `created_at` 和 `title` 字段（`id` 通过 Python 继承获得）

## Inheritance Mode Design

系统提供两种继承处理模式，通过命令行参数 `--inheritance-mode` 控制：

### Mode 1: Reference Mode（引用模式）

**命令行参数**: `--inheritance-mode reference`（默认值）

**行为描述**:
- 为所有在 `templates` 中定义的模板生成独立的 Python 类文件
- 每个模板生成到指定的 `export_path` 或默认的 mixins 目录
- 子类通过 Python 继承机制引用这些 mixin 类
- 继承的字段不在子类中重复定义，通过继承获得
- 生成的代码包含必要的 import 语句

**生成示例**:

输入 TOML:
```toml
[templates.CreateModifyMixinModel]
[[templates.CreateModifyMixinModel.columns]]
name = "created_at"
type = "datetime"

[[templates.CreateModifyMixinModel.columns]]
name = "modified_at"
type = "datetime"

[entities.Translation]
extends = ["CreateModifyMixinModel"]
[[entities.Translation.columns]]
name = "id"
type = "bigint"
primary_key = true
```

生成的文件结构:
```
output/
├── mixins/
│   └── create_modify_mixin_model.py
└── models/
    └── translation.py
```

`mixins/create_modify_mixin_model.py`:
```python
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CreateModifyMixinModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)
```

`models/translation.py`:
```python
from sqlalchemy import Column, BigInteger
from mixins.create_modify_mixin_model import CreateModifyMixinModel

class Translation(CreateModifyMixinModel):
    __tablename__ = 'translation'
    
    id = Column(BigInteger, primary_key=True)
```

**优势**:
- 保持 DRY 原则，mixin 字段只定义一次
- 符合面向对象设计原则
- 修改 mixin 时自动影响所有子类
- 代码结构清晰，继承关系明确

**劣势**:
- 需要管理多个文件
- 需要正确处理 import 路径
- 理解完整的 model 需要查看多个文件

### Mode 2: Flatten Mode（展开模式）

**命令行参数**: `--inheritance-mode flatten`

**行为描述**:
- 不生成独立的 mixin 类文件
- 将所有继承的字段直接展开到子类的字段定义中
- 每个 entity 生成的文件是自包含的，包含所有字段
- 不使用 Python 继承（除非 template 有 `export_path` 指向外部真实类）
- 字段按继承顺序合并：先父类字段，后子类字段

**生成示例**:

使用相同的输入 TOML，生成的文件结构:
```
output/
└── models/
    └── translation.py
```

`models/translation.py`:
```python
from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Translation(Base):
    __tablename__ = 'translation'
    
    # Fields from CreateModifyMixinModel (inherited)
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)
    
    # Fields from Translation (own)
    id = Column(BigInteger, primary_key=True)
```

**优势**:
- 每个 model 文件自包含，易于理解
- 不需要管理 mixin 文件和 import 路径
- 适合代码生成场景（生成后不再修改）
- 调试时可以直接看到所有字段

**劣势**:
- 违反 DRY 原则，相同字段在多个文件中重复
- 修改公共字段需要更新所有使用它的 model
- 生成的代码量更大

### Command Line Interface Design

**参数名称**: `--inheritance-mode` 或 `-i`

**可选值**:
- `reference`: 引用模式（默认）
- `flatten`: 展开模式

**使用示例**:
```bash
# 使用引用模式（默认）
er-gen convert input.toml output/ --format sqlalchemy

# 显式指定引用模式
er-gen convert input.toml output/ --format sqlalchemy --inheritance-mode reference

# 使用展开模式
er-gen convert input.toml output/ --format sqlalchemy --inheritance-mode flatten

# 使用短参数
er-gen convert input.toml output/ --format sqlalchemy -i flatten
```

**参数验证**:
- 如果提供的值不是 `reference` 或 `flatten`，显示错误并退出
- 默认值为 `reference` 以保持向后兼容性

**配置文件支持**（可选）:
可以在配置文件中设置默认值：
```toml
# .er-gen.toml
[generator.sqlalchemy]
inheritance_mode = "flatten"
```

### Implementation Strategy

**Parser 层修改**:
- `TomlERParser` 接受 `inheritance_mode` 参数
- 在 `_parse_entities` 方法中根据模式决定字段展开策略：
  - `reference` 模式：只展开没有 `export_path` 的模板字段
  - `flatten` 模式：展开所有模板字段（除非 `export_path` 指向外部真实类）

**Generator 层修改**:
- SQLAlchemy generator 接受 `inheritance_mode` 参数
- 在 `reference` 模式下：
  - 为每个 template 生成独立的 mixin 类文件
  - 在 entity 类中添加继承和 import 语句
  - 使用 `inherited_column_names` 过滤已继承的字段
- 在 `flatten` 模式下：
  - 不生成 mixin 类文件
  - 在 entity 类中直接渲染所有字段
  - 添加注释标识哪些字段来自继承

**Jinja2 模板修改**:
- 模板接收 `inheritance_mode` 变量
- 根据模式条件渲染继承语句或展开字段
- 在 `flatten` 模式下添加字段来源注释

**CLI 层修改**:
- 在 `convert` 命令中添加 `--inheritance-mode` 参数
- 将参数传递给 parser 和 generator
- 添加参数验证和帮助文档

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- 字段类型映射（string → String, bigint → BigInteger 等）必须保持不变
- 外键和关系定义的生成逻辑必须保持不变
- Django 风格的关系命名（使用逻辑名称如 `code` 而不是 `i18ncode_rel`）必须保持不变
- 字段属性（nullable, unique, primary_key, comment 等）的处理必须保持不变
- 字段覆盖机制（子类字段覆盖父类同名字段）必须保持不变
- 多模板继承的顺序（后面的模板覆盖前面的）必须保持不变
- 当不指定 `--inheritance-mode` 时，默认使用 `reference` 模式以保持向后兼容

**Mode-Specific Behaviors:**

**Reference Mode 期望行为**:
- 有 `export_path` 的模板字段必须通过 Python 继承机制获得，不在子类中重复定义
- 没有 `export_path` 的模板应该生成独立的 mixin 类文件（在默认 mixins 目录）
- 子类必须包含正确的 import 语句和继承声明
- 生成的 mixin 类必须标记为 `__abstract__ = True`

**Flatten Mode 期望行为**:
- 所有模板字段（除了指向外部真实类的）必须直接展开到子类中
- 不生成独立的 mixin 类文件
- 展开的字段应该包含注释标识其来源（如 `# Fields from CreateModifyMixinModel`）
- 字段顺序：先继承字段（按 extends 顺序），后自有字段

**Scope:**
所有不涉及 `extends` 字段的 TOML 输入应该在两种模式下产生相同的结果。这包括：
- 没有继承关系的简单实体
- 关系定义和外键处理
- 字段类型和属性的映射

## Hypothesized Root Cause

基于 bug 描述和代码分析，最可能的问题是：

1. **字段展开逻辑不完整**: 在 `_parse_entities` 方法中（约第 130-140 行），代码检查 `if template_name in templates`，但只有当模板有 `export_path` 时才会跳过字段展开。然而，实际的逻辑是反的 - 代码注释说"如果不存在（如 Django 内置类或第三方库类），则跳过字段展开"，但实际上对于在 templates 中但没有 export_path 的模板，也应该展开字段。

2. **条件判断错误**: 当前代码逻辑：
   ```python
   if template_name in templates:
       # 复制模板字段
       for col in templates[template_name]['columns']:
           base_columns.append(Column(**col.__dict__))
   ```
   这个逻辑看起来是正确的，但问题可能在于 templates 字典的构建或者在 Jinja2 模板中的字段过滤逻辑。

3. **Jinja2 模板过滤逻辑**: 在 `sqlalchemy_model.j2` 和 `sqlalchemy_single_model.j2` 中（约第 30-45 行），`inherited_column_names` 列表的构建逻辑可能有问题：
   ```jinja2
   {%- if model.templates[template_name].export_path %}
   {# 只有有export_path的模板字段才排除，没有export_path的会展开 #}
   {%- for col in model.templates[template_name].columns %}
   {%- set _ = inherited_column_names.append(col.name) %}
   {%- endfor %}
   {%- endif %}
   ```
   这个逻辑是正确的 - 只有有 export_path 的字段才被排除。但如果 parser 没有正确展开字段到 entity.columns，那么即使模板不排除，字段也不会出现。

4. **实际根本原因**: 重新检查代码后，发现问题可能在于：当 TOML 文件中的 entity 有 `extends` 字段，但这些父类名称不在 `templates` 部分定义时（如示例中的 `kinkotech.common.infrastructure.models.base.CreateModifyMixinModel`），parser 会跳过字段展开。这是因为代码假设所有 extends 的类要么在 templates 中定义（会展开字段），要么是外部类（不展开字段）。但实际情况是，某些 mixin 类的字段信息可能需要从其他来源获取，或者 TOML 文件本身不完整。

## Correctness Properties

Property 1: Fault Condition - Reference Mode 继承字段处理

_For any_ TOML entity 其 `extends` 字段引用了在 `templates` 中定义的模板，当使用 `--inheritance-mode reference` 时，修复后的系统 SHALL 为没有 `export_path` 的模板生成独立的 mixin 类文件，并使子类通过 Python 继承引用这些类，确保所有继承字段可通过继承机制访问。

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Fault Condition - Flatten Mode 继承字段展开

_For any_ TOML entity 其 `extends` 字段引用了在 `templates` 中定义的模板，当使用 `--inheritance-mode flatten` 时，修复后的系统 SHALL 将所有模板字段直接展开到子类的字段定义中（除了指向外部真实类的模板），使生成的 model 自包含所有字段定义。

**Validates: Requirements 2.4, 2.5, 2.6**

Property 3: Preservation - 无继承实体行为一致

_For any_ TOML entity 不包含 `extends` 字段，修复后的系统 SHALL 在两种继承模式下产生完全相同的输出，保持所有现有的字段类型映射、关系生成和命名约定。

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

Property 4: Preservation - 默认模式向后兼容

_For any_ TOML 输入，当不指定 `--inheritance-mode` 参数时，修复后的系统 SHALL 使用 `reference` 模式作为默认值，确保向后兼容性。

**Validates: Requirements 3.6**

## Fix Implementation

### Changes Required

修复需要在多个层次进行更改以支持两种继承模式：

#### 1. CLI Layer Changes

**File**: `packages/er-gen-tool/src/x007007007/er_tool/convert.py`

**Changes**:
1. 添加 `--inheritance-mode` / `-i` 命令行参数
2. 参数验证：只接受 `reference` 或 `flatten`
3. 默认值设置为 `reference`
4. 将参数传递给 generator

```python
@click.option(
    '--inheritance-mode', '-i',
    type=click.Choice(['reference', 'flatten'], case_sensitive=False),
    default='reference',
    help='Inheritance handling mode: reference (generate mixin files) or flatten (expand all fields)'
)
def convert(input_file, output_dir, format, inheritance_mode):
    # Pass inheritance_mode to generator
    pass
```

#### 2. Parser Layer Changes

**File**: `packages/er-gen-core/src/x007007007/er/parser/toml_parser.py`

**Function**: `TomlERParser.__init__` 和 `_parse_entities`

**Changes**:
1. 在 `__init__` 中接受 `inheritance_mode` 参数
2. 在 `_parse_entities` 中根据模式调整字段展开逻辑：
   - **Reference Mode**: 
     - 为没有 `export_path` 的模板展开字段到 entity.columns
     - 为这些模板自动生成 `export_path`（如 `mixins.template_name`）
     - 有 `export_path` 的模板不展开字段（通过继承获得）
   - **Flatten Mode**:
     - 展开所有模板字段到 entity.columns（除了指向外部真实类的）
     - 在字段对象上添加元数据标识来源模板
     - 不生成 mixin 文件

```python
def __init__(self, inheritance_mode='reference'):
    self.inheritance_mode = inheritance_mode

def _parse_entities(self, data):
    # For each entity with extends
    for template_name in entity_extends:
        if template_name in templates:
            template = templates[template_name]
            
            if self.inheritance_mode == 'flatten':
                # Always expand fields (unless external class)
                if not template.get('export_path') or not is_external_class(template['export_path']):
                    for col in template['columns']:
                        col_copy = Column(**col.__dict__)
                        col_copy._source_template = template_name  # Add metadata
                        base_columns.append(col_copy)
            else:  # reference mode
                if not template.get('export_path'):
                    # Generate default export_path for mixin
                    template['export_path'] = f'mixins.{template_name.lower()}'
                    # Expand fields
                    for col in template['columns']:
                        base_columns.append(Column(**col.__dict__))
                # If has export_path, don't expand (will inherit)
```

#### 3. Generator Layer Changes

**File**: `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/generator.py`

**Changes**:
1. 接受 `inheritance_mode` 参数
2. 在 `reference` 模式下：
   - 为每个需要的 template 生成独立的 mixin 类文件
   - 在 entity 类中添加继承声明
   - 使用 `inherited_column_names` 过滤字段
3. 在 `flatten` 模式下：
   - 不生成 mixin 文件
   - 渲染所有字段（包括继承的）
   - 添加注释标识字段来源

```python
def generate(self, er_model, output_dir, inheritance_mode='reference'):
    if inheritance_mode == 'reference':
        # Generate mixin files
        self._generate_mixin_files(er_model, output_dir)
        # Generate entity files with inheritance
        self._generate_entity_files_with_inheritance(er_model, output_dir)
    else:  # flatten
        # Generate entity files with all fields expanded
        self._generate_entity_files_flattened(er_model, output_dir)
```

#### 4. Jinja2 Template Changes

**Files**: 
- `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_model.j2`
- `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_single_model.j2`

**Changes**:
1. 接受 `inheritance_mode` 变量
2. 条件渲染继承语句或展开字段
3. 在 `flatten` 模式下添加字段来源注释

```jinja2
{% if inheritance_mode == 'reference' %}
  {# Render inheritance and filter inherited fields #}
  {% set inherited_column_names = [] %}
  {% for template_name in entity.extends %}
    {% if entity.templates[template_name].export_path %}
      {% for col in entity.templates[template_name].columns %}
        {% set _ = inherited_column_names.append(col.name) %}
      {% endfor %}
    {% endif %}
  {% endfor %}
  
  class {{ entity.name }}({% for t in entity.extends %}{{ t }}{% if not loop.last %}, {% endif %}{% endfor %}):
      __tablename__ = '{{ entity.table_name }}'
      
      {% for col in entity.columns %}
        {% if col.name not in inherited_column_names %}
          {{ col.name }} = Column(...)
        {% endif %}
      {% endfor %}
{% else %}
  {# Flatten mode: render all fields with source comments #}
  class {{ entity.name }}(Base):
      __tablename__ = '{{ entity.table_name }}'
      
      {% set current_source = None %}
      {% for col in entity.columns %}
        {% if col._source_template and col._source_template != current_source %}
          {% set current_source = col._source_template %}
          # Fields from {{ current_source }}
        {% elif not col._source_template and current_source %}
          {% set current_source = None %}
          # Own fields
        {% endif %}
        {{ col.name }} = Column(...)
      {% endfor %}
{% endif %}
```

#### 5. New Template for Mixin Classes

**File**: `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_mixin.j2` (new)

**Content**:
```jinja2
from sqlalchemy import Column, {{ column_types|join(', ') }}
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class {{ mixin_name }}(Base):
    __abstract__ = True
    
    {% for col in columns %}
    {{ col.name }} = Column({{ col.type }}, {% if col.nullable %}nullable=True{% else %}nullable=False{% endif %}{% if col.primary_key %}, primary_key=True{% endif %})
    {% endfor %}
```

### Implementation Order

1. **Phase 1**: CLI 参数添加和验证
2. **Phase 2**: Parser 层修改（字段展开逻辑）
3. **Phase 3**: Generator 层修改（文件生成逻辑）
4. **Phase 4**: Jinja2 模板修改（渲染逻辑）
5. **Phase 5**: 测试和验证

### Edge Cases to Handle

1. **混合继承**：entity 同时继承有 `export_path` 和无 `export_path` 的模板
   - Reference mode: 生成 mixin 文件给无 export_path 的，继承外部类
   - Flatten mode: 展开所有字段（除了外部类的）

2. **字段覆盖**：子类定义与父类同名的字段
   - 两种模式都应该使用子类的字段定义

3. **多重继承顺序**：多个模板定义同名字段
   - 按 extends 列表顺序，后面的覆盖前面的

4. **循环继承**：模板之间存在循环引用
   - 在 parser 中检测并报错

5. **外部类检测**：区分真实的外部 Python 类和内部模板
   - 通过检查 `export_path` 是否指向项目外部来判断

## Testing Strategy

### Validation Approach

测试策略遵循两阶段方法：首先，在未修复的代码上运行探索性测试以暴露 bug 的反例；然后，验证修复后的代码在两种继承模式下都能正确处理继承字段并保持现有行为不变。

### Exploratory Fault Condition Checking

**Goal**: 在实施修复之前，在未修复的代码上暴露展示 bug 的反例。确认或反驳根本原因分析。如果反驳，需要重新假设。

**Test Plan**: 创建包含正确 templates 定义的测试 TOML 文件（包括无 export_path 的 mixin 模板），使用当前的 parser 和 generator 处理这些文件，观察生成的 SQLAlchemy models 是否缺少继承字段。在未修复的代码上运行这些测试以观察失败并理解根本原因。

**Test Cases**:
1. **Single Mixin Inheritance Test**: 创建一个 entity 继承单个无 export_path 的 mixin 模板，验证生成的 model 是否包含 mixin 字段（在未修复代码上会失败）
2. **Multiple Mixin Inheritance Test**: 创建一个 entity 继承多个无 export_path 的 mixin 模板，验证字段合并顺序和覆盖逻辑（在未修复代码上会失败）
3. **Mixed Inheritance Test**: 创建一个 entity 同时继承有 export_path 和无 export_path 的模板，验证字段展开和排除逻辑（在未修复代码上可能部分失败）
4. **Field Override Test**: 创建一个 entity 继承 mixin 但覆盖某些字段，验证覆盖逻辑（在未修复代码上可能失败）

**Expected Counterexamples**:
- 生成的 SQLAlchemy models 缺少从无 export_path 模板继承的字段
- 可能的原因：TOML 文件缺少 templates 定义，parser 跳过字段展开，generator 过滤掉字段

### Fix Checking

**Goal**: 验证对于所有触发 bug 条件的输入，修复后的系统在两种继承模式下都产生期望的行为。

**Pseudocode for Reference Mode:**
```
FOR ALL toml_input WHERE isBugCondition(toml_input.entity, toml_input.templates, "reference") DO
  output := parse_and_generate_fixed(toml_input, mode="reference")
  ASSERT mixinFilesGenerated(output, toml_input.templates)
  ASSERT entityInheritsFromMixins(output.entity_file)
  ASSERT inheritedFieldsNotDuplicated(output.entity_file)
  ASSERT importStatementsCorrect(output.entity_file)
END FOR
```

**Pseudocode for Flatten Mode:**
```
FOR ALL toml_input WHERE isBugCondition(toml_input.entity, toml_input.templates, "flatten") DO
  output := parse_and_generate_fixed(toml_input, mode="flatten")
  ASSERT noMixinFilesGenerated(output)
  ASSERT allFieldsExpanded(output.entity_file, toml_input.templates)
  ASSERT fieldSourceCommentsPresent(output.entity_file)
  ASSERT fieldOrderCorrect(output.entity_file)
END FOR
```

**Test Implementation**:
1. 创建多个测试 TOML 文件，每个包含不同的继承场景
2. 对每个文件分别使用 `reference` 和 `flatten` 模式处理
3. 验证 Reference Mode 输出：
   - Mixin 文件已生成且包含正确字段
   - Entity 文件包含继承声明
   - Entity 文件不重复继承字段
   - Import 语句正确
4. 验证 Flatten Mode 输出：
   - 没有生成 mixin 文件
   - Entity 文件包含所有展开的字段
   - 字段来源注释存在
   - 字段顺序正确（先继承后自有）

### Preservation Checking

**Goal**: 验证对于所有不触发 bug 条件的输入，修复后的系统产生与原系统完全相同的结果。

**Pseudocode:**
```
FOR ALL toml_input WHERE NOT hasInheritance(toml_input.entity) DO
  output_reference := parse_and_generate_fixed(toml_input, mode="reference")
  output_flatten := parse_and_generate_fixed(toml_input, mode="flatten")
  output_original := parse_and_generate_original(toml_input)
  
  ASSERT output_reference = output_flatten = output_original
END FOR
```

**Testing Approach**: 使用基于属性的测试（Property-Based Testing）进行保留检查，因为：
- 它自动生成大量跨输入域的测试用例
- 它能捕获手动单元测试可能遗漏的边缘情况
- 它为所有非 buggy 输入提供强有力的保证，确保行为不变

**Test Plan**: 首先在未修复的代码上观察现有行为（无继承、只有 export_path 继承、关系处理等），然后编写基于属性的测试捕获这些行为，验证修复后在两种模式下都保持不变。

**Test Cases**:
1. **No Inheritance Preservation**: 观察无继承关系的 entities 在未修复代码上正确生成，编写测试验证修复后在两种模式下都继续正确生成且输出相同
2. **Export Path Inheritance Preservation**: 观察只继承有 export_path 模板的 entities 在未修复代码上正确生成（继承 Python 类，不重复字段），编写测试验证修复后在 reference 模式下继续正确
3. **Relationship Preservation**: 观察外键和关系定义在未修复代码上正确生成，编写测试验证修复后在两种模式下都继续正确
4. **Field Type Mapping Preservation**: 观察各种字段类型映射在未修复代码上正确工作，编写测试验证修复后在两种模式下都继续正确
5. **Django Naming Preservation**: 观察 Django 风格的关系命名在未修复代码上正确工作，编写测试验证修复后在两种模式下都继续正确
6. **Default Mode Preservation**: 验证不指定 `--inheritance-mode` 时默认使用 `reference` 模式

### Unit Tests

**Parser Tests**:
- 测试 `_parse_entities` 方法在 reference 模式下正确处理各种 extends 场景
- 测试 `_parse_entities` 方法在 flatten 模式下正确展开所有字段
- 测试字段覆盖逻辑（子类覆盖父类，后模板覆盖前模板）在两种模式下都正确
- 测试边缘情况（空 extends，不存在的模板，循环继承等）
- 测试字段元数据（`_source_template`）在 flatten 模式下正确添加

**Generator Tests**:
- 测试 reference 模式下 mixin 文件生成逻辑
- 测试 reference 模式下 entity 文件的继承声明和 import 语句
- 测试 flatten 模式下字段展开和注释生成
- 测试两种模式下字段过滤逻辑的正确性

**Template Tests**:
- 测试 Jinja2 模板在 reference 模式下正确渲染继承语句
- 测试 Jinja2 模板在 flatten 模式下正确渲染展开字段
- 测试 `inherited_column_names` 过滤逻辑在 reference 模式下正确工作
- 测试字段来源注释在 flatten 模式下正确生成

**CLI Tests**:
- 测试 `--inheritance-mode` 参数解析和验证
- 测试默认值为 `reference`
- 测试无效值被拒绝
- 测试参数正确传递给 parser 和 generator

### Property-Based Tests

**Reference Mode Properties**:
- 生成随机 TOML 结构（包含各种 templates 和 entities 组合），验证 reference 模式下 mixin 文件和 entity 文件都正确生成
- 生成随机继承层次结构，验证字段合并和覆盖逻辑的正确性
- 测试大量无继承场景，确保 reference 模式不影响简单情况

**Flatten Mode Properties**:
- 生成随机 TOML 结构，验证 flatten 模式下所有字段正确展开
- 生成随机继承层次结构，验证字段顺序和来源注释的正确性
- 测试大量无继承场景，确保 flatten 模式不影响简单情况

**Cross-Mode Properties**:
- 对于无继承的 entities，验证两种模式产生相同输出
- 生成随机字段类型和属性组合，验证类型映射和属性处理在两种模式下都保持一致
- 验证关系定义在两种模式下都正确生成

### Integration Tests

**Reference Mode Integration**:
- 端到端测试：从完整的 TOML 文件到生成的 SQLAlchemy models（包含 mixin 文件）
- 测试真实的 Django models 转换场景（包含 CreateModifyMixinModel 等常见 mixins）
- 测试生成的 mixin 类可以被 entity 类正确继承
- 测试生成的 models 可以被 SQLAlchemy 正确加载和使用
- 测试生成的 models 可以执行数据库操作（创建表、插入数据等）

**Flatten Mode Integration**:
- 端到端测试：从完整的 TOML 文件到生成的自包含 SQLAlchemy models
- 测试真实的 Django models 转换场景，验证所有字段都正确展开
- 测试生成的 models 可以被 SQLAlchemy 正确加载和使用
- 测试生成的 models 可以执行数据库操作（创建表、插入数据等）
- 验证展开的字段与 reference 模式下通过继承获得的字段功能等价

**Cross-Mode Integration**:
- 测试同一个 TOML 文件在两种模式下生成的 models 在数据库层面功能等价
- 测试多文件生成场景（每个 entity 一个文件 vs 所有 entities 一个文件）在两种模式下都正确工作
- 测试复杂的继承场景（多重继承、混合继承、字段覆盖）在两种模式下都正确处理

### Test Data Preparation

**Minimal Test Cases**:
1. `test_single_mixin_reference.toml` - 单个 mixin，reference 模式
2. `test_single_mixin_flatten.toml` - 单个 mixin，flatten 模式
3. `test_multiple_mixins_reference.toml` - 多个 mixins，reference 模式
4. `test_multiple_mixins_flatten.toml` - 多个 mixins，flatten 模式
5. `test_mixed_inheritance_reference.toml` - 混合继承，reference 模式
6. `test_mixed_inheritance_flatten.toml` - 混合继承，flatten 模式
7. `test_no_inheritance.toml` - 无继承（两种模式应产生相同输出）

**Real-World Test Cases**:
1. Django blog app models（包含 CreateModifyMixinModel）
2. E-commerce models（包含 TimestampMixin, SoftDeleteMixin）
3. Multi-tenant models（包含 TenantMixin）

### Success Criteria

修复被认为成功当且仅当：
1. 所有探索性测试在未修复代码上失败（暴露 bug）
2. 所有探索性测试在修复代码上通过（bug 已修复）
3. 所有保留测试在修复代码上通过（无回归）
4. Reference 模式生成正确的 mixin 文件和继承结构
5. Flatten 模式生成正确的自包含 entity 文件
6. 无继承的 entities 在两种模式下产生相同输出
7. 默认模式为 reference（向后兼容）
8. 所有单元测试、属性测试和集成测试都通过
