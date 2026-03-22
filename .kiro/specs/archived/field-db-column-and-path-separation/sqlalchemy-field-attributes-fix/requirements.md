# Requirements Document

## Introduction

本功能旨在修复 Django 到 SQLAlchemy 模型转换过程中字段属性丢失的问题。当前系统在解析阶段能够正确提取 Django 字段的 `unique`、`db_index` 和 `null` 属性，但在渲染 SQLAlchemy 代码时未能将这些属性完整地包含在生成的代码中。具体问题包括：

1. `unique=True` 属性被解析但未在 SQLAlchemy 代码中渲染
2. `db_index=True` 属性被解析为 `indexed=True` 但未在 SQLAlchemy 代码中渲染为 `index=True`
3. `null=False` 属性被解析为 `nullable=False` 并在某些情况下正确渲染，但在其他情况下（如带有 `max_length` 的字段）会被遗漏

这导致生成的 SQLAlchemy 模型缺少重要的数据库约束和索引定义。

## Glossary

- **Parser**: Django 模型解析器，负责将 Django 模型转换为中间表示（ERModel）
- **Renderer**: SQLAlchemy 渲染器，负责将中间表示（ERModel）转换为 SQLAlchemy 代码
- **Column**: 字段对象，包含字段的所有属性（name, type, unique, indexed 等）
- **Template**: Jinja2 模板文件，用于生成 SQLAlchemy 代码
- **ERModel**: 实体关系模型，作为 Django 和 SQLAlchemy 之间的中间表示

## Requirements

### Requirement 1: 渲染 unique 属性

**User Story:** 作为开发者，我希望 Django 字段的 `unique=True` 属性能够在生成的 SQLAlchemy 代码中体现为 `unique=True` 参数，以便保持数据库约束的一致性。

#### Acceptance Criteria

1. WHEN 一个 Column 对象的 unique 属性为 True，THEN THE Renderer SHALL 在生成的 SQLAlchemy Column 定义中包含 `unique=True` 参数
2. WHEN 一个 Column 对象的 unique 属性为 False，THEN THE Renderer SHALL NOT 在生成的 SQLAlchemy Column 定义中包含 `unique` 参数
3. WHEN 一个字段同时具有 unique=True 和其他属性（如 nullable, default），THEN THE Renderer SHALL 在参数列表中正确包含所有属性

### Requirement 2: 渲染 indexed 属性

**User Story:** 作为开发者，我希望 Django 字段的 `db_index=True` 属性能够在生成的 SQLAlchemy 代码中体现为 `index=True` 参数，以便保持数据库索引的一致性。

#### Acceptance Criteria

1. WHEN 一个 Column 对象的 indexed 属性为 True，THEN THE Renderer SHALL 在生成的 SQLAlchemy Column 定义中包含 `index=True` 参数
2. WHEN 一个 Column 对象的 indexed 属性为 False，THEN THE Renderer SHALL NOT 在生成的 SQLAlchemy Column 定义中包含 `index` 参数
3. WHEN 一个字段同时具有 indexed=True 和其他属性（如 nullable, default），THEN THE Renderer SHALL 在参数列表中正确包含所有属性

### Requirement 3: 修复 nullable 属性渲染不一致

**User Story:** 作为开发者，我希望 Django 字段的 `null=False` 属性能够在所有情况下都正确渲染为 SQLAlchemy 的 `nullable=False` 参数，以确保数据库约束的完整性。

#### Acceptance Criteria

1. WHEN 一个 Column 对象的 nullable 属性为 False 且字段有 max_length，THEN THE Renderer SHALL 在生成的 SQLAlchemy Column 定义中包含 `nullable=False` 参数
2. WHEN 一个 Column 对象的 nullable 属性为 False 且字段没有 max_length，THEN THE Renderer SHALL 在生成的 SQLAlchemy Column 定义中包含 `nullable=False` 参数
3. WHEN 一个 Column 对象的 nullable 属性为 True，THEN THE Renderer SHALL NOT 在生成的 SQLAlchemy Column 定义中包含 `nullable` 参数

### Requirement 4: 保持解析器的正确性

**User Story:** 作为开发者，我希望确认 Django 模型解析器能够正确提取字段属性，以便为渲染器提供完整的数据。

#### Acceptance Criteria

1. WHEN Parser 解析一个带有 `unique=True` 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中设置 `unique=True`
2. WHEN Parser 解析一个带有 `db_index=True` 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中设置 `indexed=True`
3. WHEN Parser 解析一个同时具有 unique 和 db_index 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中正确设置两个属性

### Requirement 4: 保持解析器的正确性

**User Story:** 作为开发者，我希望确认 Django 模型解析器能够正确提取字段属性，以便为渲染器提供完整的数据。

#### Acceptance Criteria

1. WHEN Parser 解析一个带有 `unique=True` 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中设置 `unique=True`
2. WHEN Parser 解析一个带有 `db_index=True` 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中设置 `indexed=True`
3. WHEN Parser 解析一个带有 `null=False` 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中设置 `nullable=False`
4. WHEN Parser 解析一个同时具有 unique、db_index 和 null 的 Django 字段，THEN THE Parser SHALL 在生成的 Column 对象中正确设置所有属性

### Requirement 5: 端到端转换验证

**User Story:** 作为开发者，我希望通过端到端测试验证从 Django 模型到 SQLAlchemy 代码的完整转换流程，以确保字段属性不会在任何阶段丢失。

#### Acceptance Criteria

1. WHEN 一个 Django 模型包含 `unique=True` 字段，THEN THE System SHALL 生成包含 `unique=True` 参数的 SQLAlchemy 代码
2. WHEN 一个 Django 模型包含 `db_index=True` 字段，THEN THE System SHALL 生成包含 `index=True` 参数的 SQLAlchemy 代码
3. WHEN 一个 Django 模型包含多个具有不同属性组合的字段，THEN THE System SHALL 为每个字段生成正确的 SQLAlchemy Column 定义

### Requirement 5: 端到端转换验证

**User Story:** 作为开发者，我希望通过端到端测试验证从 Django 模型到 SQLAlchemy 代码的完整转换流程，以确保字段属性不会在任何阶段丢失。

#### Acceptance Criteria

1. WHEN 一个 Django 模型包含 `unique=True` 字段，THEN THE System SHALL 生成包含 `unique=True` 参数的 SQLAlchemy 代码
2. WHEN 一个 Django 模型包含 `db_index=True` 字段，THEN THE System SHALL 生成包含 `index=True` 参数的 SQLAlchemy 代码
3. WHEN 一个 Django 模型包含 `null=False` 字段，THEN THE System SHALL 生成包含 `nullable=False` 参数的 SQLAlchemy 代码
4. WHEN 一个 Django 模型包含多个具有不同属性组合的字段，THEN THE System SHALL 为每个字段生成正确的 SQLAlchemy Column 定义

### Requirement 6: 模板一致性

**User Story:** 作为维护者，我希望所有 SQLAlchemy 模板文件都能正确处理字段属性，以确保系统的一致性。

#### Acceptance Criteria

1. WHEN 使用 sqlalchemy_single_model.j2 模板渲染，THEN THE Template SHALL 正确包含 unique 和 index 参数
2. WHEN 使用 sqlalchemy_model.j2 模板渲染，THEN THE Template SHALL 正确包含 unique 和 index 参数
3. WHEN 模板处理外键字段时，THEN THE Template SHALL 仍然正确处理 unique 和 index 属性

### Requirement 6: 模板一致性

**User Story:** 作为维护者，我希望所有 SQLAlchemy 模板文件都能正确处理字段属性，以确保系统的一致性。

#### Acceptance Criteria

1. WHEN 使用 sqlalchemy_single_model.j2 模板渲染，THEN THE Template SHALL 正确包含 unique、index 和 nullable 参数
2. WHEN 使用 sqlalchemy_model.j2 模板渲染，THEN THE Template SHALL 正确包含 unique、index 和 nullable 参数
3. WHEN 模板处理外键字段时，THEN THE Template SHALL 仍然正确处理 unique、index 和 nullable 属性
4. WHEN 模板处理带有 max_length 的字段时，THEN THE Template SHALL 正确包含所有字段属性

### Requirement 7: 参数顺序和格式

**User Story:** 作为开发者，我希望生成的 SQLAlchemy 代码具有一致的参数顺序和格式，以提高代码的可读性和可维护性。

#### Acceptance Criteria

1. WHEN 生成 Column 定义时，THEN THE Renderer SHALL 按照固定顺序排列参数：primary_key, nullable, unique, index, default, comment
2. WHEN 一个参数的值为默认值（如 unique=False），THEN THE Renderer SHALL NOT 包含该参数
3. WHEN 生成的代码包含多个参数时，THEN THE Renderer SHALL 使用逗号和空格正确分隔参数
