# Requirements Document / 需求文档

## Introduction / 简介

This document specifies requirements for two improvements to the ER diagram converter project:

本文档规定了 ER 图转换器项目的两项改进需求：

1. Changing the default intermediate format from Mermaid to TOML
   将默认中间格式从 Mermaid 更改为 TOML
2. Creating a Python code value serializer module to fix string escaping issues in generated Django code
   创建 Python 代码值序列化器模块以修复生成的 Django 代码中的字符串转义问题

The TOML format has fewer limitations and better structure compared to Mermaid, making it a more suitable default. The code serializer will ensure that generated Django models have proper string escaping and use the most readable quote style automatically.

TOML 格式相比 Mermaid 具有更少的限制和更好的结构，使其成为更合适的默认格式。代码序列化器将确保生成的 Django 模型具有正确的字符串转义，并自动使用最易读的引号样式。

## Glossary / 术语表

- **CLI**: Command-Line Interface - the er-convert command / 命令行界面 - er-convert 命令
- **TOML**: Tom's Obvious Minimal Language - a configuration file format / 一种配置文件格式
- **Mermaid**: A diagramming and charting tool that uses text definitions / 使用文本定义的图表工具
- **Django_Renderer**: The component that generates Django model code from ER models / 从 ER 模型生成 Django 模型代码的组件
- **SQLAlchemy_Renderer**: The component that generates SQLAlchemy model code from ER models / 从 ER 模型生成 SQLAlchemy 模型代码的组件
- **Jinja2**: A templating engine for Python / Python 的模板引擎
- **Code_Serializer**: The new module that converts Python values to code strings / 将 Python 值转换为代码字符串的新模块
- **Template_Filter**: A Jinja2 custom filter function / Jinja2 自定义过滤器函数
- **Default_Value**: A Python value assigned to a model field as its default / 分配给模型字段作为其默认值的 Python 值
- **Help_Text**: A string describing a Django model field / 描述 Django 模型字段的字符串
- **Quote_Style**: The choice between single quotes ('') and double quotes ("") for string literals / 字符串字面量的单引号和双引号选择

## Requirements / 需求

### Requirement 1: Change CLI Default Input Type / 更改 CLI 默认输入类型

**User Story / 用户故事:** As a developer, I want the CLI to default to TOML format, so that I can use the more structured format without specifying it explicitly.

作为开发者，我希望 CLI 默认使用 TOML 格式，这样我可以使用更结构化的格式而无需显式指定。

#### Acceptance Criteria / 验收标准

1. WHEN the CLI is invoked without --input-type flag, THE CLI SHALL use 'toml' as the default input type
   当 CLI 在没有 --input-type 标志的情况下调用时，CLI 应使用 'toml' 作为默认输入类型
2. WHEN the CLI is invoked with --input-type mermaid, THE CLI SHALL use 'mermaid' as the input type
   当 CLI 使用 --input-type mermaid 调用时，CLI 应使用 'mermaid' 作为输入类型
3. WHEN the CLI help is displayed, THE CLI SHALL show 'toml' as the default value for --input-type
   当显示 CLI 帮助时，CLI 应显示 'toml' 作为 --input-type 的默认值

### Requirement 2: Update Documentation for TOML Default / 更新 TOML 默认值文档

**User Story / 用户故事:** As a developer, I want the documentation to reflect the new default, so that I understand the current behavior.

作为开发者，我希望文档反映新的默认值，以便我了解当前的行为。

#### Acceptance Criteria / 验收标准

1. WHEN the README is read, THE README SHALL show examples using TOML as the primary format
   当阅读 README 时，README 应显示使用 TOML 作为主要格式的示例
2. WHEN the README describes the --input-type option, THE README SHALL indicate 'toml' as the default
   当 README 描述 --input-type 选项时，README 应指示 'toml' 为默认值
3. WHEN the README shows basic usage examples, THE README SHALL demonstrate TOML format first
   当 README 显示基本使用示例时，README 应首先演示 TOML 格式

### Requirement 3: Create Code Serializer Module / 创建代码序列化器模块

**User Story / 用户故事:** As a developer, I want a dedicated module for serializing Python values to code strings, so that generated code has proper escaping.

作为开发者，我希望有一个专门的模块将 Python 值序列化为代码字符串，以便生成的代码具有正确的转义。

#### Acceptance Criteria / 验收标准

1. THE Code_Serializer SHALL provide a function that converts Python values to code strings
   Code_Serializer 应提供一个将 Python 值转换为代码字符串的函数
2. WHEN given a Python value, THE Code_Serializer SHALL return a valid Python code string representation
   当给定 Python 值时，Code_Serializer 应返回有效的 Python 代码字符串表示
3. WHEN given None, THE Code_Serializer SHALL return "None"
   当给定 None 时，Code_Serializer 应返回 "None"
4. WHEN given a boolean, THE Code_Serializer SHALL return "True" or "False"
   当给定布尔值时，Code_Serializer 应返回 "True" 或 "False"
5. WHEN given a number, THE Code_Serializer SHALL return the number as a string
   当给定数字时，Code_Serializer 应将数字作为字符串返回
6. WHEN given a list, THE Code_Serializer SHALL return a bracketed list representation
   当给定列表时，Code_Serializer 应返回带括号的列表表示
7. WHEN given a dict, THE Code_Serializer SHALL return a braced dict representation
   当给定字典时，Code_Serializer 应返回带大括号的字典表示

### Requirement 4: Smart Quote Selection for Strings / 字符串的智能引号选择

**User Story / 用户故事:** As a developer, I want the serializer to choose the most readable quote style, so that generated code is clean and doesn't have unnecessary escaping.

作为开发者，我希望序列化器选择最易读的引号样式，以便生成的代码干净且没有不必要的转义。

#### Acceptance Criteria / 验收标准

1. WHEN a string contains only double quotes and no single quotes, THE Code_Serializer SHALL use single quotes for the outer string
   当字符串仅包含双引号而不包含单引号时，Code_Serializer 应使用单引号作为外部字符串
2. WHEN a string contains only single quotes and no double quotes, THE Code_Serializer SHALL use double quotes for the outer string
   当字符串仅包含单引号而不包含双引号时，Code_Serializer 应使用双引号作为外部字符串
3. WHEN a string contains both single and double quotes, THE Code_Serializer SHALL use double quotes and escape internal double quotes
   当字符串同时包含单引号和双引号时，Code_Serializer 应使用双引号并转义内部双引号
4. WHEN a string contains neither single nor double quotes, THE Code_Serializer SHALL use double quotes for the outer string
   当字符串既不包含单引号也不包含双引号时，Code_Serializer 应使用双引号作为外部字符串
5. WHEN a string contains escape sequences, THE Code_Serializer SHALL preserve them correctly
   当字符串包含转义序列时，Code_Serializer 应正确保留它们

### Requirement 5: Language-Specific Serialization / 特定语言序列化

**User Story / 用户故事:** As a developer, I want the serializer to support different target languages, so that Django and SQLAlchemy code can have language-specific formatting.

作为开发者，我希望序列化器支持不同的目标语言，以便 Django 和 SQLAlchemy 代码可以具有特定于语言的格式。

#### Acceptance Criteria / 验收标准

1. THE Code_Serializer SHALL accept a language parameter ('django' or 'sqlalchemy')
   Code_Serializer 应接受语言参数（'django' 或 'sqlalchemy'）
2. WHEN language is 'django', THE Code_Serializer SHALL format values according to Django conventions
   当语言为 'django' 时，Code_Serializer 应根据 Django 约定格式化值
3. WHEN language is 'sqlalchemy', THE Code_Serializer SHALL format values according to SQLAlchemy conventions
   当语言为 'sqlalchemy' 时，Code_Serializer 应根据 SQLAlchemy 约定格式化值
4. WHEN language is not specified, THE Code_Serializer SHALL default to 'django'
   当未指定语言时，Code_Serializer 应默认为 'django'

### Requirement 6: Integrate Serializer with Jinja2 Templates / 将序列化器与 Jinja2 模板集成

**User Story / 用户故事:** As a developer, I want the serializer available as a Jinja2 filter, so that templates can use it easily.

作为开发者，我希望序列化器作为 Jinja2 过滤器可用，以便模板可以轻松使用它。

#### Acceptance Criteria / 验收标准

1. THE Django_Renderer SHALL register the Code_Serializer as a Jinja2 filter
   Django_Renderer 应将 Code_Serializer 注册为 Jinja2 过滤器
2. THE SQLAlchemy_Renderer SHALL register the Code_Serializer as a Jinja2 filter
   SQLAlchemy_Renderer 应将 Code_Serializer 注册为 Jinja2 过滤器
3. WHEN a template uses the filter, THE Template SHALL receive properly serialized code strings
   当模板使用过滤器时，模板应接收正确序列化的代码字符串
4. WHEN the filter is called with a value, THE Filter SHALL return a string suitable for direct insertion into code
   当使用值调用过滤器时，过滤器应返回适合直接插入代码的字符串

### Requirement 7: Update Django Template to Use Serializer / 更新 Django 模板以使用序列化器

**User Story / 用户故事:** As a developer, I want the Django template to use the serializer for default values and help_text, so that generated code has no escaping issues.

作为开发者，我希望 Django 模板使用序列化器处理默认值和 help_text，以便生成的代码没有转义问题。

#### Acceptance Criteria / 验收标准

1. WHEN rendering a field with a default value, THE Django_Renderer SHALL use the Code_Serializer to format the default
   当渲染具有默认值的字段时，Django_Renderer 应使用 Code_Serializer 格式化默认值
2. WHEN rendering a field with help_text, THE Django_Renderer SHALL use the Code_Serializer to format the help_text
   当渲染具有 help_text 的字段时，Django_Renderer 应使用 Code_Serializer 格式化 help_text
3. WHEN rendering a field with both default and help_text, THE Django_Renderer SHALL serialize both values correctly
   当渲染同时具有 default 和 help_text 的字段时，Django_Renderer 应正确序列化两个值
4. WHEN the generated code is parsed by Python, THE Generated_Code SHALL have no syntax errors
   当 Python 解析生成的代码时，生成的代码应没有语法错误

### Requirement 8: Update SQLAlchemy Template to Use Serializer / 更新 SQLAlchemy 模板以使用序列化器

**User Story / 用户故事:** As a developer, I want the SQLAlchemy template to use the serializer for default values and comments, so that generated code has no escaping issues.

作为开发者，我希望 SQLAlchemy 模板使用序列化器处理默认值和注释，以便生成的代码没有转义问题。

#### Acceptance Criteria / 验收标准

1. WHEN rendering a column with a default value, THE SQLAlchemy_Renderer SHALL use the Code_Serializer to format the default
   当渲染具有默认值的列时，SQLAlchemy_Renderer 应使用 Code_Serializer 格式化默认值
2. WHEN rendering a column with a comment, THE SQLAlchemy_Renderer SHALL use the Code_Serializer to format the comment
   当渲染具有注释的列时，SQLAlchemy_Renderer 应使用 Code_Serializer 格式化注释
3. WHEN the generated code is parsed by Python, THE Generated_Code SHALL have no syntax errors
   当 Python 解析生成的代码时，生成的代码应没有语法错误

### Requirement 9: Handle Edge Cases in Serialization / 处理序列化中的边缘情况

**User Story / 用户故事:** As a developer, I want the serializer to handle edge cases correctly, so that all valid Python values can be serialized.

作为开发者，我希望序列化器正确处理边缘情况，以便可以序列化所有有效的 Python 值。

#### Acceptance Criteria / 验收标准

1. WHEN given an empty string, THE Code_Serializer SHALL return '""'
   当给定空字符串时，Code_Serializer 应返回 '""'
2. WHEN given a string with newlines, THE Code_Serializer SHALL escape newlines as '\n'
   当给定包含换行符的字符串时，Code_Serializer 应将换行符转义为 '\n'
3. WHEN given a string with tabs, THE Code_Serializer SHALL escape tabs as '\t'
   当给定包含制表符的字符串时，Code_Serializer 应将制表符转义为 '\t'
4. WHEN given a string with backslashes, THE Code_Serializer SHALL escape backslashes correctly
   当给定包含反斜杠的字符串时，Code_Serializer 应正确转义反斜杠
5. WHEN given a nested data structure, THE Code_Serializer SHALL serialize it recursively
   当给定嵌套数据结构时，Code_Serializer 应递归序列化它

### Requirement 10: Maintain Backward Compatibility / 保持向后兼容性

**User Story / 用户故事:** As a developer, I want existing functionality to continue working, so that the changes don't break existing code.

作为开发者，我希望现有功能继续工作，以便更改不会破坏现有代码。

#### Acceptance Criteria / 验收标准

1. WHEN the CLI is invoked with explicit --input-type mermaid, THE CLI SHALL work exactly as before
   当使用显式 --input-type mermaid 调用 CLI 时，CLI 应完全按照以前的方式工作
2. WHEN existing templates are rendered without using the new filter, THE Templates SHALL continue to work
   当在不使用新过滤器的情况下渲染现有模板时，模板应继续工作
3. WHEN existing tests are run, THE Tests SHALL pass without modification
   当运行现有测试时，测试应在不修改的情况下通过

### Requirement 11: Three-File Structure for Django Package Renderer / Django 包渲染器的三文件结构

**User Story / 用户故事:** As a developer, I want each Django model to be split into three separate files (model, manager, queryset), so that the code is better organized and follows separation of concerns.

作为开发者，我希望每个 Django 模型拆分为三个独立的文件（model、manager、queryset），以便代码更好地组织并遵循关注点分离。

#### Acceptance Criteria / 验收标准

1. WHEN DjangoPackageRenderer renders an entity, THE Renderer SHALL generate three separate files for that entity
   当 DjangoPackageRenderer 渲染实体时，渲染器应为该实体生成三个独立的文件
2. WHEN an entity is rendered, THE Renderer SHALL create a `<entity_name>_queryset.py` file containing only the QuerySet class
   当渲染实体时，渲染器应创建仅包含 QuerySet 类的 `<entity_name>_queryset.py` 文件
3. WHEN an entity is rendered, THE Renderer SHALL create a `<entity_name>_manager.py` file containing only the Manager class
   当渲染实体时，渲染器应创建仅包含 Manager 类的 `<entity_name>_manager.py` 文件
4. WHEN an entity is rendered, THE Renderer SHALL create a `<entity_name>_model.py` file containing only the Model class
   当渲染实体时，渲染器应创建仅包含 Model 类的 `<entity_name>_model.py` 文件
5. WHEN the Model file is generated, THE Model file SHALL import the Manager and QuerySet from their respective files
   当生成 Model 文件时，Model 文件应从各自的文件导入 Manager 和 QuerySet
6. WHEN the Manager file is generated, THE Manager file SHALL import the QuerySet from the queryset file
   当生成 Manager 文件时，Manager 文件应从 queryset 文件导入 QuerySet
7. WHEN the __init__.py file is generated, THE __init__.py file SHALL import all Model classes (not Manager or QuerySet)
   当生成 __init__.py 文件时，__init__.py 文件应导入所有 Model 类（不包括 Manager 或 QuerySet）
8. WHEN file names are generated, THE Renderer SHALL use snake_case naming convention
   当生成文件名时，渲染器应使用 snake_case 命名约定

### Requirement 12: Make Three-File Structure the Default / 将三文件结构设为默认

**User Story / 用户故事:** As a developer, I want the three-file structure to be the default behavior for Django package rendering, so that I get better organized code by default.

作为开发者，我希望三文件结构成为 Django 包渲染的默认行为，以便默认获得更好组织的代码。

#### Acceptance Criteria / 验收标准

1. WHEN DjangoPackageRenderer is used, THE Renderer SHALL always generate three files per entity
   当使用 DjangoPackageRenderer 时，渲染器应始终为每个实体生成三个文件
2. WHEN the CLI is invoked with --split-models or --output-dir, THE CLI SHALL use DjangoPackageRenderer with three-file structure
   当使用 --split-models 或 --output-dir 调用 CLI 时，CLI 应使用具有三文件结构的 DjangoPackageRenderer
3. WHEN documentation describes the package mode, THE Documentation SHALL explain the three-file structure
   当文档描述包模式时，文档应解释三文件结构

### Requirement 13: Organize Renderers by Language and Framework / 按语言和框架组织渲染器

**User Story / 用户故事:** As a developer, I want renderers organized into packages by language and framework, so that the codebase is more maintainable and extensible.

作为开发者，我希望渲染器按语言和框架组织成包，以便代码库更易于维护和扩展。

#### Acceptance Criteria / 验收标准

1. THE Renderer code SHALL be organized in a package structure under `src/x007007007/er/renderers/`
   渲染器代码应在 `src/x007007007/er/renderers/` 下以包结构组织
2. THE Base Renderer class SHALL be in `renderers/base.py`
   基础 Renderer 类应在 `renderers/base.py` 中
3. THE Python renderers SHALL be in `renderers/python/` package
   Python 渲染器应在 `renderers/python/` 包中
4. THE Django renderers SHALL be in `renderers/python/django/` package
   Django 渲染器应在 `renderers/python/django/` 包中
5. THE SQLAlchemy renderer SHALL be in `renderers/python/sqlalchemy/` package
   SQLAlchemy 渲染器应在 `renderers/python/sqlalchemy/` 包中
6. THE Templates SHALL be in framework-specific `templates/` directories
   模板应在框架特定的 `templates/` 目录中
7. WHEN importing renderers, THE Old import paths SHALL still work for backward compatibility
   当导入渲染器时，旧的导入路径应仍然有效以保持向后兼容性
8. WHEN importing renderers, THE New import paths SHALL be available and documented
   当导入渲染器时，新的导入路径应可用并有文档记录

### Requirement 14: Jinja2 Whitespace Control / Jinja2 空白控制

**User Story / 用户故事:** As a developer, I want Jinja2 templates to automatically handle whitespace, so that generated code doesn't have extra blank lines while templates remain readable.

作为开发者，我希望 Jinja2 模板自动处理空白，以便生成的代码没有额外的空行，同时模板保持可读性。

#### Acceptance Criteria / 验收标准

1. THE Jinja2 environment SHALL be configured with `trim_blocks=True`
   Jinja2 环境应配置为 `trim_blocks=True`
2. THE Jinja2 environment SHALL be configured with `lstrip_blocks=True`
   Jinja2 环境应配置为 `lstrip_blocks=True`
3. THE Jinja2 environment SHALL be configured with `keep_trailing_newline=True`
   Jinja2 环境应配置为 `keep_trailing_newline=True`
4. WHEN a template line contains only Jinja2 directives, THE Generated code SHALL not have an extra blank line
   当模板行仅包含 Jinja2 指令时，生成的代码不应有额外的空行
5. WHEN a template has conditional blocks, THE Generated code SHALL have proper spacing without extra blank lines
   当模板有条件块时，生成的代码应有适当的间距而没有额外的空行
6. WHEN templates are written with proper indentation for readability, THE Generated code SHALL maintain correct Python indentation
   当模板以适当的缩进编写以提高可读性时，生成的代码应保持正确的 Python 缩进
