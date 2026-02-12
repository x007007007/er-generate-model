# Design Document / 设计文档

## Overview / 概述

This design document describes the implementation approach for two improvements to the ER diagram converter:

本设计文档描述了 ER 图转换器两项改进的实现方法：

1. **Change CLI default input type from 'mermaid' to 'toml'**
   **将 CLI 默认输入类型从 'mermaid' 更改为 'toml'**
   
   This is a simple one-line change in the CLI module to update the default parameter value.
   
   这是 CLI 模块中的一行简单更改，用于更新默认参数值。

2. **Create a Python code value serializer module**
   **创建 Python 代码值序列化器模块**
   
   This involves creating a new module that intelligently converts Python values to their code string representations with proper escaping and quote selection. The serializer will be integrated into the Jinja2 template system as a custom filter.
   
   这涉及创建一个新模块，该模块智能地将 Python 值转换为其代码字符串表示，并具有正确的转义和引号选择。序列化器将作为自定义过滤器集成到 Jinja2 模板系统中。

## Architecture / 架构

### Current Architecture / 当前架构

```
CLI (cli.py)
  ↓
Parser (MermaidAntlrParser, PlantUMLAntlrParser, TomlERParser, DBParser)
  ↓
ERModel (models.py)
  ↓
Renderer (DjangoRenderer, SQLAlchemyRenderer)
  ├─ Prepares data for templates
  ├─ Manages Jinja2 environment
  └─ Decides output strategy (single/multiple files)
  ↓
Jinja2 Templates (django_model.j2, sqlalchemy_model.j2)
  ↓
Generated Code
```

### Problem Analysis / 问题分析

Currently, the templates directly output values without proper code serialization:

当前，模板直接输出值而没有正确的代码序列化：

```jinja2
{# Current problematic approach / 当前有问题的方法: #}
{%- if col.default %}
{%- set _ = param_list.append('default=' + col.default|string) %}
{%- endif %}
{%- if col.comment %}
{%- set _ = param_list.append('help_text="' + col.comment + '"') %}
{%- endif %}
```

This causes issues when:
- `col.default` contains quotes: `default="say "hi""` → syntax error
- `col.comment` contains quotes: `help_text="用户(必须)"` → works, but `help_text="say "hi""` → syntax error

这会导致以下问题：
- `col.default` 包含引号：`default="say "hi""` → 语法错误
- `col.comment` 包含引号：`help_text="用户(必须)"` → 可以工作，但 `help_text="say "hi""` → 语法错误

### New Architecture / 新架构

```
CLI (cli.py) [default='toml']
  ↓
Parser (MermaidAntlrParser, PlantUMLAntlrParser, TomlERParser, DBParser)
  ↓
ERModel (models.py)
  ↓
Renderer Package Structure (renderers/)
  ├─ base.py (Renderer base class)
  ├─ python/
  │   ├─ __init__.py
  │   ├─ base.py (PythonRenderer base class)
  │   ├─ django/
  │   │   ├─ __init__.py
  │   │   ├─ renderer.py (DjangoRenderer, DjangoPackageRenderer)
  │   │   └─ templates/
  │   │       ├─ django_model.j2
  │   │       ├─ django_model_only.j2
  │   │       ├─ django_manager_only.j2
  │   │       ├─ django_queryset_only.j2
  │   │       └─ django_init.j2
  │   └─ sqlalchemy/
  │       ├─ __init__.py
  │       ├─ renderer.py (SQLAlchemyRenderer)
  │       └─ templates/
  │           └─ sqlalchemy_model.j2
  ├─ [Future] go/
  │   ├─ __init__.py
  │   ├─ base.py (GoRenderer base class)
  │   └─ gorm/
  │       ├─ __init__.py
  │       ├─ renderer.py (GormRenderer)
  │       └─ templates/
  ├─ [Future] rust/
  │   ├─ __init__.py
  │   ├─ base.py (RustRenderer base class)
  │   └─ diesel/
  │       ├─ __init__.py
  │       ├─ renderer.py (DieselRenderer)
  │       └─ templates/
  └─ [Future] typescript/
      ├─ __init__.py
      ├─ base.py (TypeScriptRenderer base class)
      └─ typeorm/
          ├─ __init__.py
          ├─ renderer.py (TypeOrmRenderer)
          └─ templates/
  ↓
Each Renderer:
  ├─ Prepares code fragments (serialize_value method)
  ├─ Manages Jinja2 environment with language-specific filters
  ├─ Decides output strategy (single/multiple files)
  └─ Provides language-specific type mapping
  ↓
Jinja2 Templates (receive properly formatted code fragments)
  ↓
Generated Code (with correct escaping and formatting)
```

### Key Design Principles / 关键设计原则

1. **Renderer Responsibility / 渲染器职责**
   - Renderer prepares all code fragments before passing to templates
   - Renderer 在传递给模板之前准备所有代码片段
   - Templates only handle structure and layout, not code formatting
   - 模板仅处理结构和布局，不处理代码格式

2. **Language-Specific Logic / 特定语言逻辑**
   - Each language has its own renderer class
   - 每种语言都有自己的渲染器类
   - Common logic is shared in base classes
   - 通用逻辑在基类中共享
   - Language-specific rules (quote styles, naming conventions) are encapsulated
   - 特定语言规则（引号样式、命名约定）被封装

3. **Extensibility / 可扩展性**
   - Easy to add new language renderers (Go, Rust, TypeScript)
   - 易于添加新的语言渲染器（Go、Rust、TypeScript）
   - Shared code serialization logic can be reused
   - 共享的代码序列化逻辑可以重用

## Components and Interfaces / 组件和接口

### Package Structure / 包结构

The new package structure organizes renderers by language and framework:

新的包结构按语言和框架组织渲染器：

```
src/x007007007/er/
├── renderers/
│   ├── __init__.py                    # Export all public renderers
│   ├── base.py                        # Renderer base class
│   └── python/
│       ├── __init__.py                # Export Python renderers
│       ├── base.py                    # PythonRenderer base class
│       ├── django/
│       │   ├── __init__.py            # Export Django renderers
│       │   ├── renderer.py            # DjangoRenderer, DjangoPackageRenderer
│       │   └── templates/             # Django-specific templates
│       │       ├── django_model.j2
│       │       ├── django_model_only.j2
│       │       ├── django_manager_only.j2
│       │       ├── django_queryset_only.j2
│       │       └── django_init.j2
│       └── sqlalchemy/
│           ├── __init__.py            # Export SQLAlchemy renderers
│           ├── renderer.py            # SQLAlchemyRenderer
│           └── templates/             # SQLAlchemy-specific templates
│               └── sqlalchemy_model.j2
```

### Migration Strategy / 迁移策略

To maintain backward compatibility during migration:

为了在迁移期间保持向后兼容性：

1. **Phase 1**: Create new package structure alongside existing `renderers.py`
   **阶段 1**：在现有 `renderers.py` 旁边创建新的包结构

2. **Phase 2**: Move code to new structure, keep old imports working via `__init__.py`
   **阶段 2**：将代码移动到新结构，通过 `__init__.py` 保持旧导入工作

3. **Phase 3**: Update all internal imports to use new structure
   **阶段 3**：更新所有内部导入以使用新结构

4. **Phase 4**: Deprecate old `renderers.py` (optional, can keep for compatibility)
   **阶段 4**：弃用旧的 `renderers.py`（可选，可以保留以兼容）

### 1. CLI Module Update / CLI 模块更新

**File / 文件:** `src/x007007007/er/cli.py`

**Change / 更改:**
```python
# Before / 之前:
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db', 'toml']), default='mermaid', help='Input type')

# After / 之后:
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db', 'toml']), default='toml', help='Input type')

# Update imports / 更新导入:
# Before / 之前:
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer, DjangoPackageRenderer

# After / 之后:
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer

# Or use backward-compatible imports / 或使用向后兼容的导入:
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer, DjangoPackageRenderer
```

### 2. Base Renderer / 基础渲染器

**File / 文件:** `src/x007007007/er/renderers/base.py`

**Content / 内容:**

```python
"""Base renderer class for all code generators."""
from abc import ABC, abstractmethod
from typing import Any
from x007007007.er.models import ERModel


class Renderer(ABC):
    """
    Base class for all renderers.
    所有渲染器的基类。
    """
    
    @abstractmethod
    def render(self, model: ERModel) -> str:
        """
        Render the model to code.
        将模型渲染为代码。
        
        Args:
            model: The ERModel to render / 要渲染的 ERModel
            
        Returns:
            Generated code as string / 生成的代码字符串
        """
        pass
    
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        """
        Convert a Python value to its code string representation.
        将 Python 值转换为其代码字符串表示。
        
        This method should be overridden by language-specific renderers
        to provide appropriate serialization for that language.
        此方法应由特定语言的渲染器覆盖，以提供该语言的适当序列化。
        
        Args:
            value: The Python value to serialize / 要序列化的 Python 值
            context: Context hint ('default', 'comment', 'name', etc.) / 上下文提示
            
        Returns:
            A string suitable for direct insertion into code / 适合直接插入代码的字符串
        """
        raise NotImplementedError("Subclasses must implement serialize_value")
```

### 3. Python Renderer Base Class / Python 渲染器基类

**File / 文件:** `src/x007007007/er/renderers/python/base.py`

**Content / 内容:**

```python
"""Base class for Python code renderers."""
from typing import Any
from x007007007.er.renderers.base import Renderer


class PythonRenderer(Renderer):
    """
    Base class for Python code renderers (Django, SQLAlchemy, etc.)
    Python 代码渲染器的基类（Django、SQLAlchemy 等）
    
    Provides shared Python code serialization logic.
    提供共享的 Python 代码序列化逻辑。
    """
    
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        """
        Serialize a Python value to its code representation.
        将 Python 值序列化为其代码表示。
        
        Examples / 示例:
            serialize_value(None) -> "None"
            serialize_value(True) -> "True"
            serialize_value(42) -> "42"
            serialize_value("hello") -> '"hello"'
            serialize_value('say "hi"') -> '\'say "hi"\''
            serialize_value([1, 2, 3]) -> "[1, 2, 3]"
        """
        if value is None:
            return "None"
        
        if isinstance(value, bool):
            return "True" if value else "False"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, str):
            return self._serialize_string(value)
        
        if isinstance(value, list):
            elements = [self.serialize_value(item, context) for item in value]
            return "[" + ", ".join(elements) + "]"
        
        if isinstance(value, dict):
            items = [
                f"{self.serialize_value(k, context)}: {self.serialize_value(v, context)}"
                for k, v in value.items()
            ]
            return "{" + ", ".join(items) + "}"
        
        raise ValueError(f"Unsupported type for serialization: {type(value)}")
    
    def _serialize_string(self, s: str) -> str:
        """
        Serialize a string with smart quote selection.
        使用智能引号选择序列化字符串。
        
        Strategy / 策略:
        1. If string has only double quotes (no single), use single quotes
           如果字符串只有双引号（无单引号），使用单引号
        2. If string has only single quotes (no double), use double quotes
           如果字符串只有单引号（无双引号），使用双引号
        3. If string has both or neither, use double quotes
           如果字符串两者都有或都没有，使用双引号
        """
        # First, escape special characters / 首先，转义特殊字符
        s = s.replace('\\', '\\\\')  # Backslash must be first / 反斜杠必须首先
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        s = s.replace('\r', '\\r')
        
        has_single = "'" in s
        has_double = '"' in s
        
        if has_double and not has_single:
            # Use single quotes / 使用单引号
            return f"'{s}'"
        elif has_single and not has_double:
            # Use double quotes / 使用双引号
            return f'"{s}"'
        elif has_double and has_single:
            # Use double quotes and escape them / 使用双引号并转义
            s = s.replace('"', '\\"')
            return f'"{s}"'
        else:
            # No quotes, use double quotes / 无引号，使用双引号
            return f'"{s}"'
    
    def _setup_jinja_env(self, loader):
        """
        Set up Jinja2 environment with proper whitespace control.
        设置 Jinja2 环境并进行适当的空白控制。
        
        This configures Jinja2 to automatically strip whitespace from lines
        that contain only Jinja2 directives, preventing extra blank lines
        in generated code while maintaining template readability.
        
        这配置 Jinja2 自动从仅包含 Jinja2 指令的行中删除空白，
        防止生成的代码中出现额外的空行，同时保持模板的可读性。
        """
        from jinja2 import Environment, select_autoescape
        
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(),
            # Whitespace control settings / 空白控制设置
            trim_blocks=True,        # Remove first newline after block
            lstrip_blocks=True,      # Strip leading spaces/tabs from block lines
            keep_trailing_newline=True  # Keep final newline in template
        )
        
        return env
```

**Jinja2 Whitespace Control Explanation / Jinja2 空白控制说明:**

Jinja2 provides three environment settings for whitespace control:

Jinja2 提供三个环境设置用于空白控制：

1. **`trim_blocks=True`**: Removes the first newline after a template tag (e.g., `{% if %}`, `{% for %}`)
   **`trim_blocks=True`**：删除模板标签后的第一个换行符（例如，`{% if %}`、`{% for %}`）

2. **`lstrip_blocks=True`**: Strips leading whitespace (spaces and tabs) from the start of a line to the start of a block tag
   **`lstrip_blocks=True`**：从行首到块标签开始处删除前导空白（空格和制表符）

3. **`keep_trailing_newline=True`**: Preserves the trailing newline at the end of the template
   **`keep_trailing_newline=True`**：保留模板末尾的尾随换行符

**Example / 示例:**

```jinja2
{# Without whitespace control / 不使用空白控制: #}
class MyModel(models.Model):
{% if entity.comment %}
    """{{ entity.comment }}"""
{% endif %}
    name = models.CharField(max_length=100)

{# Output has extra blank line / 输出有额外的空行: #}
class MyModel(models.Model):

    """My comment"""

    name = models.CharField(max_length=100)

{# With trim_blocks=True, lstrip_blocks=True / 使用 trim_blocks=True, lstrip_blocks=True: #}
class MyModel(models.Model):
{% if entity.comment %}
    """{{ entity.comment }}"""
{% endif %}
    name = models.CharField(max_length=100)

{# Output is clean / 输出干净: #}
class MyModel(models.Model):
    """My comment"""
    name = models.CharField(max_length=100)
```

**Manual Whitespace Control / 手动空白控制:**

For fine-grained control, Jinja2 also supports manual whitespace stripping using `-` in tags:

对于细粒度控制，Jinja2 还支持在标签中使用 `-` 进行手动空白删除：

- `{%-` strips whitespace before the tag / 删除标签前的空白
- `-%}` strips whitespace after the tag / 删除标签后的空白

```jinja2
{# Example / 示例: #}
{%- if condition %}
    content
{%- endif %}
```

### 4. Django Renderer / Django 渲染器

**File / 文件:** `src/x007007007/er/renderers/python/django/renderer.py`

**Content / 内容:**

```python
"""Django model code renderers."""
import logging
import re
from pathlib import Path
from typing import Dict
from jinja2 import PackageLoader
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper
from x007007007.er.renderers.python.base import PythonRenderer

logger = logging.getLogger(__name__)


def to_snake_case(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def django_field_type(col):
    """Jinja2 filter for Django field type."""
    field_type, params = TypeMapper.get_django_type(col.type, col.max_length)
    return field_type, params


class DjangoRenderer(PythonRenderer):
    """Django model code renderer (single file output)."""
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.app_label = app_label
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment with whitespace control
        loader = PackageLoader("x007007007.er.renderers.python.django", "templates")
        self.env = self._setup_jinja_env(loader)
        
        # Register filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['code_value'] = self.serialize_value
        
        self.template = self.env.get_template("django_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            app_label=self.app_label,
            table_prefix=self.table_prefix
        )


class DjangoPackageRenderer(PythonRenderer):
    """
    Django model code renderer (package output with three files per entity).
    Django 模型代码渲染器（包输出，每个实体三个文件）。
    """
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.app_label = app_label
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment with whitespace control
        loader = PackageLoader("x007007007.er.renderers.python.django", "templates")
        self.env = self._setup_jinja_env(loader)
        
        # Register filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['code_value'] = self.serialize_value
        
        # Load templates for each component
        self.model_template = self.env.get_template("django_model_only.j2")
        self.manager_template = self.env.get_template("django_manager_only.j2")
        self.queryset_template = self.env.get_template("django_queryset_only.j2")
        self.init_template = self.env.get_template("django_init.j2")
    
    def render(self, model: ERModel) -> Dict[str, str]:
        """
        Render Django models as multiple files (3 files per entity).
        
        Returns:
            Dict[str, str]: Dictionary mapping file paths to content
        """
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        
        files = {}
        entity_names = list(model.entities.keys())
        
        # Generate __init__.py
        entity_info = [
            {'name': name, 'filename': to_snake_case(name)}
            for name in entity_names
        ]
        files['__init__.py'] = self.init_template.render(
            entity_names=entity_names,
            entity_info=entity_info
        )
        
        # Generate three files for each entity
        for entity_name, entity in model.entities.items():
            base_filename = to_snake_case(entity_name)
            
            # 1. QuerySet file
            queryset_filename = f"{base_filename}_queryset.py"
            files[queryset_filename] = self.queryset_template.render(
                entity=entity,
                model=model
            )
            
            # 2. Manager file
            manager_filename = f"{base_filename}_manager.py"
            files[manager_filename] = self.manager_template.render(
                entity=entity,
                model=model,
                base_filename=base_filename
            )
            
            # 3. Model file
            model_filename = f"{base_filename}_model.py"
            files[model_filename] = self.model_template.render(
                entity=entity,
                model=model,
                app_label=self.app_label,
                table_prefix=self.table_prefix,
                base_filename=base_filename
            )
        
        return files
    
    def write_to_directory(self, model: ERModel, output_dir: str) -> None:
        """Write rendered models to a directory."""
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        assert isinstance(output_dir, str), "output_dir must be a string"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = self.render(model)
        
        for filename, content in files.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Generated: {file_path}")
```

### 5. SQLAlchemy Renderer / SQLAlchemy 渲染器

**File / 文件:** `src/x007007007/er/renderers/python/sqlalchemy/renderer.py`

**Content / 内容:**

```python
"""SQLAlchemy model code renderer."""
from jinja2 import PackageLoader
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper
from x007007007.er.renderers.python.base import PythonRenderer


def sqlalchemy_column_type(col):
    """Jinja2 filter for SQLAlchemy column type."""
    column_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
    return column_type, params


class SQLAlchemyRenderer(PythonRenderer):
    """SQLAlchemy model code renderer."""
    
    def __init__(self, table_prefix: str = ''):
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment with whitespace control
        loader = PackageLoader("x007007007.er.renderers.python.sqlalchemy", "templates")
        self.env = self._setup_jinja_env(loader)
        
        # Register filters
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.env.filters['code_value'] = self.serialize_value
        
        self.template = self.env.get_template("sqlalchemy_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            table_prefix=self.table_prefix
        )
```

### 6. Package __init__.py Files / 包 __init__.py 文件

**File / 文件:** `src/x007007007/er/renderers/__init__.py`

```python
"""Renderers for generating code from ER models."""
# Backward-compatible imports
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer

__all__ = [
    'DjangoRenderer',
    'DjangoPackageRenderer',
    'SQLAlchemyRenderer',
]
```

**File / 文件:** `src/x007007007/er/renderers/python/__init__.py`

```python
"""Python code renderers."""
from x007007007.er.renderers.python.base import PythonRenderer
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer

__all__ = [
    'PythonRenderer',
    'DjangoRenderer',
    'DjangoPackageRenderer',
    'SQLAlchemyRenderer',
]
```

**File / 文件:** `src/x007007007/er/renderers/python/django/__init__.py`

```python
"""Django model code renderers."""
from x007007007.er.renderers.python.django.renderer import (
    DjangoRenderer,
    DjangoPackageRenderer,
    to_snake_case,
    django_field_type,
)

__all__ = [
    'DjangoRenderer',
    'DjangoPackageRenderer',
    'to_snake_case',
    'django_field_type',
]
```

**File / 文件:** `src/x007007007/er/renderers/python/sqlalchemy/__init__.py`

```python
"""SQLAlchemy model code renderer."""
from x007007007.er.renderers.python.sqlalchemy.renderer import (
    SQLAlchemyRenderer,
    sqlalchemy_column_type,
)

__all__ = [
    'SQLAlchemyRenderer',
    'sqlalchemy_column_type',
]
```

**File / 文件:** `src/x007007007/er/cli.py`

**Change / 更改:**
```python
# Before / 之前:
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db', 'toml']), default='mermaid', help='Input type')

# After / 之后:
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db', 'toml']), default='toml', help='Input type')
```

### 7. Template Updates / 模板更新

**File / 文件:** `src/x007007007/er/base.py`

**Add new method to Renderer base class / 向 Renderer 基类添加新方法:**

```python
from abc import ABC, abstractmethod
from typing import Any

class Renderer(ABC):
    """Base class for all renderers / 所有渲染器的基类"""
    
    @abstractmethod
    def render(self, model: ERModel) -> str:
        """Render the model to code / 将模型渲染为代码"""
        pass
    
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        """
        Convert a Python value to its code string representation.
        将 Python 值转换为其代码字符串表示。
        
        This method should be overridden by language-specific renderers
        to provide appropriate serialization for that language.
        此方法应由特定语言的渲染器覆盖，以提供该语言的适当序列化。
        
        Args:
            value: The Python value to serialize / 要序列化的 Python 值
            context: Context hint ('default', 'comment', 'name', etc.) / 上下文提示
            
        Returns:
            A string suitable for direct insertion into code / 适合直接插入代码的字符串
        """
        raise NotImplementedError("Subclasses must implement serialize_value")
```

### 3. Python Renderer Base Class / Python 渲染器基类

**File / 文件:** `src/x007007007/er/renderers.py` (modify existing file / 修改现有文件)

**Add new PythonRenderer base class / 添加新的 PythonRenderer 基类:**

```python
class PythonRenderer(Renderer):
    """
    Base class for Python code renderers (Django, SQLAlchemy, etc.)
    Python 代码渲染器的基类（Django、SQLAlchemy 等）
    
    Provides shared Python code serialization logic.
    提供共享的 Python 代码序列化逻辑。
    """
    
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        """
        Serialize a Python value to its code representation.
        将 Python 值序列化为其代码表示。
        
        Examples / 示例:
            serialize_value(None) -> "None"
            serialize_value(True) -> "True"
            serialize_value(42) -> "42"
            serialize_value("hello") -> '"hello"'
            serialize_value('say "hi"') -> '\'say "hi"\''
            serialize_value([1, 2, 3]) -> "[1, 2, 3]"
        """
        if value is None:
            return "None"
        
        if isinstance(value, bool):
            return "True" if value else "False"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, str):
            return self._serialize_string(value)
        
        if isinstance(value, list):
            elements = [self.serialize_value(item, context) for item in value]
            return "[" + ", ".join(elements) + "]"
        
        if isinstance(value, dict):
            items = [
                f"{self.serialize_value(k, context)}: {self.serialize_value(v, context)}"
                for k, v in value.items()
            ]
            return "{" + ", ".join(items) + "}"
        
        raise ValueError(f"Unsupported type for serialization: {type(value)}")
    
    def _serialize_string(self, s: str) -> str:
        """
        Serialize a string with smart quote selection.
        使用智能引号选择序列化字符串。
        
        Strategy / 策略:
        1. If string has only double quotes (no single), use single quotes
           如果字符串只有双引号（无单引号），使用单引号
        2. If string has only single quotes (no double), use double quotes
           如果字符串只有单引号（无双引号），使用双引号
        3. If string has both or neither, use double quotes
           如果字符串两者都有或都没有，使用双引号
        """
        # First, escape special characters / 首先，转义特殊字符
        s = s.replace('\\', '\\\\')  # Backslash must be first / 反斜杠必须首先
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        s = s.replace('\r', '\\r')
        
        has_single = "'" in s
        has_double = '"' in s
        
        if has_double and not has_single:
            # Use single quotes / 使用单引号
            return f"'{s}'"
        elif has_single and not has_double:
            # Use double quotes / 使用双引号
            return f'"{s}"'
        elif has_double and has_single:
            # Use double quotes and escape them / 使用双引号并转义
            s = s.replace('"', '\\"')
            return f'"{s}"'
        else:
            # No quotes, use double quotes / 无引号，使用双引号
            return f'"{s}"'
```

### 4. Update Django Renderer / 更新 Django 渲染器

**File / 文件:** `src/x007007007/er/renderers.py`

**Modify DjangoRenderer to inherit from PythonRenderer / 修改 DjangoRenderer 以继承 PythonRenderer:**

```python
class DjangoRenderer(PythonRenderer):
    """Django model code renderer / Django 模型代码渲染器"""
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.app_label = app_label
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment / 设置 Jinja2 环境
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        
        # Register filters / 注册过滤器
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['code_value'] = self.serialize_value  # NEW / 新增
        
        self.template = self.env.get_template("django_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            app_label=self.app_label,
            table_prefix=self.table_prefix
        )
```

### 5. Update SQLAlchemy Renderer / 更新 SQLAlchemy 渲染器

**File / 文件:** `src/x007007007/er/renderers.py`

**Modify SQLAlchemyRenderer to inherit from PythonRenderer / 修改 SQLAlchemyRenderer 以继承 PythonRenderer:**

```python
class SQLAlchemyRenderer(PythonRenderer):
    """SQLAlchemy model code renderer / SQLAlchemy 模型代码渲染器"""
    
    def __init__(self, table_prefix: str = ''):
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment / 设置 Jinja2 环境
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        
        # Register filters / 注册过滤器
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.env.filters['code_value'] = self.serialize_value  # NEW / 新增
        
        self.template = self.env.get_template("sqlalchemy_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            table_prefix=self.table_prefix
        )
```

### 6. Update Django Package Renderer / 更新 Django 包渲染器

**File / 文件:** `src/x007007007/er/renderers.py`

**Modify DjangoPackageRenderer to inherit from PythonRenderer and generate three files per entity / 修改 DjangoPackageRenderer 以继承 PythonRenderer 并为每个实体生成三个文件:**

```python
class DjangoPackageRenderer(PythonRenderer):
    """
    Renderer that generates Django models as a package with separate files.
    渲染器将 Django 模型生成为包，每个实体有独立的文件。
    
    For each entity, generates three files:
    为每个实体生成三个文件：
    - <entity_name>_model.py: Model class definition / 模型类定义
    - <entity_name>_manager.py: Manager class definition / Manager 类定义
    - <entity_name>_queryset.py: QuerySet class definition / QuerySet 类定义
    """
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.app_label = app_label
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment / 设置 Jinja2 环境
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        
        # Register filters / 注册过滤器
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['code_value'] = self.serialize_value  # NEW / 新增
        
        # Load templates for each component / 加载每个组件的模板
        self.model_template = self.env.get_template("django_model_only.j2")
        self.manager_template = self.env.get_template("django_manager_only.j2")
        self.queryset_template = self.env.get_template("django_queryset_only.j2")
        self.init_template = self.env.get_template("django_init.j2")
    
    def render(self, model: ERModel) -> Dict[str, str]:
        """
        Render Django models as multiple files (3 files per entity).
        将 Django 模型渲染为多个文件（每个实体 3 个文件）。
        
        Returns:
            Dict[str, str]: Dictionary mapping file paths to content
                - '__init__.py': Package init file / 包初始化文件
                - '<entity_name>_model.py': Model class / 模型类
                - '<entity_name>_manager.py': Manager class / Manager 类
                - '<entity_name>_queryset.py': QuerySet class / QuerySet 类
        """
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        
        files = {}
        entity_names = list(model.entities.keys())
        
        # Generate __init__.py with imports for all components
        # 生成 __init__.py，导入所有组件
        entity_info = [
            {'name': name, 'filename': to_snake_case(name)}
            for name in entity_names
        ]
        files['__init__.py'] = self.init_template.render(
            entity_names=entity_names,
            entity_info=entity_info
        )
        
        # Generate three files for each entity
        # 为每个实体生成三个文件
        for entity_name, entity in model.entities.items():
            base_filename = to_snake_case(entity_name)
            
            # 1. QuerySet file / QuerySet 文件
            queryset_filename = f"{base_filename}_queryset.py"
            files[queryset_filename] = self.queryset_template.render(
                entity=entity,
                model=model
            )
            
            # 2. Manager file / Manager 文件
            manager_filename = f"{base_filename}_manager.py"
            files[manager_filename] = self.manager_template.render(
                entity=entity,
                model=model,
                base_filename=base_filename
            )
            
            # 3. Model file / 模型文件
            model_filename = f"{base_filename}_model.py"
            files[model_filename] = self.model_template.render(
                entity=entity,
                model=model,
                app_label=self.app_label,
                table_prefix=self.table_prefix,
                base_filename=base_filename
            )
        
        return files
    
    # write_to_directory method remains the same
    # write_to_directory 方法保持不变
```

**New Template Files Required / 需要的新模板文件:**

1. **`django_queryset_only.j2`**: Template for QuerySet class only
   仅 QuerySet 类的模板

2. **`django_manager_only.j2`**: Template for Manager class only
   仅 Manager 类的模板

3. **`django_model_only.j2`**: Template for Model class only (imports Manager and QuerySet)
   仅 Model 类的模板（导入 Manager 和 QuerySet）

**File Structure Example / 文件结构示例:**

```
output_dir/
├── __init__.py                    # Imports all models / 导入所有模型
├── user_queryset.py              # UserQuerySet class / UserQuerySet 类
├── user_manager.py               # UserManager class / UserManager 类
├── user_model.py                 # User model class / User 模型类
├── post_queryset.py              # PostQuerySet class / PostQuerySet 类
├── post_manager.py               # PostManager class / PostManager 类
└── post_model.py                 # Post model class / Post 模型类
```

### 7. Template Updates / 模板更新

Templates will be moved to their respective framework directories:

模板将移动到各自的框架目录：

**Django Templates / Django 模板:**
- Location / 位置: `src/x007007007/er/renderers/python/django/templates/`
- Files / 文件:
  - `django_model.j2` (single file output)
  - `django_model_only.j2` (model class only)
  - `django_manager_only.j2` (manager class only)
  - `django_queryset_only.j2` (queryset class only)
  - `django_init.j2` (package __init__.py)

**SQLAlchemy Templates / SQLAlchemy 模板:**
- Location / 位置: `src/x007007007/er/renderers/python/sqlalchemy/templates/`
- Files / 文件:
  - `sqlalchemy_model.j2`

**Template Changes / 模板更改:**

All templates should use the `code_value` filter for serializing default values and comments:

所有模板都应使用 `code_value` 过滤器来序列化默认值和注释：

```jinja2
{# Before / 之前: #}
{%- if col.default %}
{%- set _ = param_list.append('default=' + col.default|string) %}
{%- endif %}
{%- if col.comment %}
{%- set _ = param_list.append('help_text="' + col.comment + '"') %}
{%- endif %}

{# After / 之后: #}
{%- if col.default %}
{%- set _ = param_list.append('default=' + (col.default | code_value)) %}
{%- endif %}
{%- if col.comment %}
{%- set _ = param_list.append('help_text=' + (col.comment | code_value)) %}
{%- endif %}
```

### 8. New Template Files for Three-File Structure / 三文件结构的新模板文件

**File / 文件:** `src/x007007007/er/templates/django_queryset_only.j2`

```jinja2
"""QuerySet for {{ entity.name }} model."""
from django.db import models


class {{ entity.name }}QuerySet(models.QuerySet):
    """Custom QuerySet for {{ entity.name }}."""
{%- if entity.comment %}
    # {{ entity.comment }}
{%- endif %}
    
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass
```

**File / 文件:** `src/x007007007/er/templates/django_manager_only.j2`

```jinja2
"""Manager for {{ entity.name }} model."""
from django.db import models
from .{{ base_filename }}_queryset import {{ entity.name }}QuerySet


class {{ entity.name }}Manager(models.Manager):
    """Custom Manager for {{ entity.name }}."""
    
    def get_queryset(self):
        return {{ entity.name }}QuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
```

**File / 文件:** `src/x007007007/er/templates/django_model_only.j2`

```jinja2
"""Model definition for {{ entity.name }}."""
from django.db import models
from .{{ base_filename }}_manager import {{ entity.name }}Manager
{%- if entity.extends %}
{# 生成基类导入 #}
{%- for template_name in entity.extends %}
{%- if template_name in model.templates and model.templates[template_name].export_path %}
{%- set base_class_name = template_name | title | replace('_', '') + 'Mixin' %}
from {{ model.templates[template_name].export_path }} import {{ base_class_name }}
{%- endif %}
{%- endfor %}
{%- endif %}


{%- set base_classes = [] %}
{%- if entity.extends %}
{%- for template_name in entity.extends %}
{%- if template_name in model.templates and model.templates[template_name].export_path %}
{%- set base_class_name = template_name | title | replace('_', '') + 'Mixin' %}
{%- set _ = base_classes.append(base_class_name) %}
{%- endif %}
{%- endfor %}
{%- endif %}

class {{ entity.name }}({% if base_classes %}{{ base_classes|join(', ') }}{% else %}models.Model{% endif %}):
{%- if entity.comment %}
    """{{ entity.comment }}"""
{%- endif %}
{%- set fk_columns = {} %}
{%- for rel in model.relationships %}
{%- if rel.right_entity == entity.name and rel.right_column %}
{%- set _ = fk_columns.update({rel.right_column: rel}) %}
{%- endif %}
{%- endfor %}
{%- set inherited_column_names = [] %}
{%- if entity.extends %}
{%- for template_name in entity.extends %}
{%- if template_name in model.templates %}
{%- if model.templates[template_name].export_path %}
{# 只有有export_path的模板字段才排除 #}
{%- for col in model.templates[template_name].columns %}
{%- set _ = inherited_column_names.append(col.name) %}
{%- endfor %}
{%- endif %}
{%- endif %}
{%- endfor %}
{%- endif %}
{%- for col in entity.columns %}
{%- if col.name not in inherited_column_names %}
{%- if col.name in fk_columns %}
{%- set rel = fk_columns[col.name] %}
{%- if rel.relation_type == 'one-to-one' %}
    {{ col.name.replace('_id', '') if col.name.endswith('_id') else col.name }} = models.OneToOneField(
        '{{ rel.left_entity }}',
        on_delete=models.CASCADE,
        related_name='{{ entity.name|lower }}_rel'
{%- if col.comment %},
        help_text={{ col.comment | code_value }}
{%- endif %}
    )
{%- else %}
    {{ col.name.replace('_id', '') if col.name.endswith('_id') else col.name }} = models.ForeignKey(
        '{{ rel.left_entity }}',
        on_delete=models.CASCADE,
        related_name='{{ entity.name|lower }}_set'
{%- if col.comment %},
        help_text={{ col.comment | code_value }}
{%- endif %}
    )
{%- endif %}
{%- else %}
{%- set field_type, params = col | django_field_type %}
{%- set param_list = [] %}
{%- if 'max_length' in params %}
{%- set _ = param_list.append('max_length=' + params.max_length|string) %}
{%- endif %}
{%- if 'max_digits' in params %}
{%- set _ = param_list.append('max_digits=' + params.max_digits|string) %}
{%- endif %}
{%- if 'decimal_places' in params %}
{%- set _ = param_list.append('decimal_places=' + params.decimal_places|string) %}
{%- endif %}
{%- if col.is_pk %}
{%- set _ = param_list.append('primary_key=True') %}
{%- endif %}
{%- if col.unique %}
{%- set _ = param_list.append('unique=True') %}
{%- endif %}
{%- if not col.nullable %}
{%- set _ = param_list.append('null=' + col.nullable|string) %}
{%- endif %}
{%- if col.default %}
{%- set _ = param_list.append('default=' + (col.default | code_value)) %}
{%- endif %}
{%- if col.comment %}
{%- set _ = param_list.append('help_text=' + (col.comment | code_value)) %}
{%- endif %}
    {{ col.name }} = models.{{ field_type }}({% if param_list %}{{ param_list|join(', ') }}{% endif %})
{%- endif %}
{%- endif %}
{%- endfor %}
{%- for rel in model.relationships %}
{%- if rel.left_entity == entity.name %}
{%- if rel.relation_type == 'many-to-many' %}
    {{ rel.right_entity|lower }}_set = models.ManyToManyField(
        '{{ rel.right_entity }}',
        related_name='{{ entity.name|lower }}_set'
    )
{%- endif %}
{%- endif %}
{%- endfor %}
    
    objects = {{ entity.name }}Manager()
{%- set table_name = entity.name|lower %}
{%- if table_prefix %}
{%- set table_name = table_prefix + '_' + table_name %}
{%- endif %}
    
    class Meta:
        app_label = '{{ app_label }}'
        db_table = '{{ table_name }}'
{%- if entity.comment %}
        verbose_name = {{ entity.comment | code_value }}
        verbose_name_plural = {{ entity.comment | code_value }}
{%- endif %}
    
    def __str__(self):
        return f"{{ entity.name }}(id={self.pk})"
```

**File / 文件:** `src/x007007007/er/templates/django_init.j2` (Updated / 更新)

```jinja2
"""Django models package."""
{%- for info in entity_info %}
from .{{ info.filename }}_model import {{ info.name }}
{%- endfor %}

__all__ = [
{%- for name in entity_names %}
    '{{ name }}',
{%- endfor %}
]
```

### 9. Future Extensibility / 未来可扩展性

The design allows for easy addition of new language renderers:

该设计允许轻松添加新的语言渲染器：

```python
# Future: Go Renderer / 未来：Go 渲染器
class GoRenderer(Renderer):
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        # Go-specific serialization logic / Go 特定的序列化逻辑
        # e.g., nil instead of None, true/false instead of True/False
        # 例如，nil 而不是 None，true/false 而不是 True/False
        pass

# Future: Rust Renderer / 未来：Rust 渲染器
class RustRenderer(Renderer):
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        # Rust-specific serialization logic / Rust 特定的序列化逻辑
        # e.g., None instead of None, String::from("...") for strings
        # 例如，None 而不是 None，String::from("...") 用于字符串
        pass

# Future: TypeScript Renderer / 未来：TypeScript 渲染器
class TypeScriptRenderer(Renderer):
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        # TypeScript-specific serialization logic / TypeScript 特定的序列化逻辑
        # e.g., null instead of None, template literals for strings
        # 例如，null 而不是 None，模板字面量用于字符串
        pass
```

## Data Models / 数据模型

No changes to existing data models. The `Column` class already has `default` and `comment` fields that store string values.

现有数据模型无需更改。`Column` 类已经具有存储字符串值的 `default` 和 `comment` 字段。


## Correctness Properties / 正确性属性

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

属性是在系统的所有有效执行中应该保持为真的特征或行为——本质上是关于系统应该做什么的正式声明。属性充当人类可读规范和机器可验证正确性保证之间的桥梁。

### Property 1: Serialization Round Trip / 序列化往返

*For any* Python value that can be serialized (None, bool, int, float, str, list, dict), serializing the value and then evaluating the result should produce an equivalent value.

*对于任何*可以序列化的 Python 值（None、bool、int、float、str、list、dict），序列化该值然后评估结果应产生等效值。

**Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

### Property 2: Smart Quote Selection / 智能引号选择

*For any* string value, the serializer should choose the quote style that minimizes escaping:
- If the string contains only double quotes (no single quotes), use single quotes for the outer string
- If the string contains only single quotes (no double quotes), use double quotes for the outer string  
- If the string contains both or neither, use double quotes for the outer string

*对于任何*字符串值，序列化器应选择最小化转义的引号样式：
- 如果字符串仅包含双引号（无单引号），则对外部字符串使用单引号
- 如果字符串仅包含单引号（无双引号），则对外部字符串使用双引号
- 如果字符串同时包含两者或都不包含，则对外部字符串使用双引号

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 3: Escape Sequence Preservation / 转义序列保留

*For any* string containing special characters (newlines, tabs, backslashes), the serialized output should preserve these characters correctly such that when evaluated, the original string is recovered.

*对于任何*包含特殊字符（换行符、制表符、反斜杠）的字符串，序列化输出应正确保留这些字符，以便在评估时恢复原始字符串。

**Validates: Requirements 4.5, 9.2, 9.3, 9.4**

### Property 4: Nested Structure Serialization / 嵌套结构序列化

*For any* nested data structure (lists containing dicts, dicts containing lists, etc.), the serializer should recursively serialize all elements correctly.

*对于任何*嵌套数据结构（包含字典的列表、包含列表的字典等），序列化器应正确递归序列化所有元素。

**Validates: Requirements 9.5**

### Property 5: Django Template Integration / Django 模板集成

*For any* ERModel with entities containing columns with default values or comments, rendering the model with Django renderer should produce code where all default values and help_text are properly serialized using the code_value filter.

*对于任何*包含具有默认值或注释的列的实体的 ERModel，使用 Django 渲染器渲染模型应生成代码，其中所有默认值和 help_text 都使用 code_value 过滤器正确序列化。

**Validates: Requirements 7.1, 7.2**

### Property 6: SQLAlchemy Template Integration / SQLAlchemy 模板集成

*For any* ERModel with entities containing columns with default values or comments, rendering the model with SQLAlchemy renderer should produce code where all default values and comments are properly serialized using the code_value filter.

*对于任何*包含具有默认值或注释的列的实体的 ERModel，使用 SQLAlchemy 渲染器渲染模型应生成代码，其中所有默认值和注释都使用 code_value 过滤器正确序列化。

**Validates: Requirements 8.1, 8.2**

### Property 7: Generated Code Validity / 生成代码有效性

*For any* ERModel rendered to Django or SQLAlchemy code, the generated code should be syntactically valid Python that can be parsed without errors.

*对于任何*渲染为 Django 或 SQLAlchemy 代码的 ERModel，生成的代码应该是语法上有效的 Python，可以无错误地解析。

**Validates: Requirements 7.4, 8.3**

### Property 8: Filter Registration / 过滤器注册

*For any* renderer instance (Django or SQLAlchemy), the Jinja2 environment should have the 'code_value' filter registered and callable.

*对于任何*渲染器实例（Django 或 SQLAlchemy），Jinja2 环境应该注册并可调用 'code_value' 过滤器。

**Validates: Requirements 6.1, 6.2, 6.3**

### Property 9: Three-File Structure Generation / 三文件结构生成

*For any* ERModel with N entities, rendering with DjangoPackageRenderer should produce exactly 3N + 1 files (3 files per entity plus __init__.py).

*对于任何*具有 N 个实体的 ERModel，使用 DjangoPackageRenderer 渲染应恰好生成 3N + 1 个文件（每个实体 3 个文件加上 __init__.py）。

**Validates: Requirements 11.1**

### Property 10: File Naming Convention / 文件命名约定

*For any* entity with name EntityName, the generated files should be named:
- entity_name_queryset.py (QuerySet file)
- entity_name_manager.py (Manager file)
- entity_name_model.py (Model file)

*对于任何*名为 EntityName 的实体，生成的文件应命名为：
- entity_name_queryset.py（QuerySet 文件）
- entity_name_manager.py（Manager 文件）
- entity_name_model.py（Model 文件）

**Validates: Requirements 11.2, 11.3, 11.4, 11.8**

### Property 11: Import Correctness / 导入正确性

*For any* generated model file, the imports should be correct such that:
- Model file imports Manager from manager file
- Manager file imports QuerySet from queryset file
- __init__.py imports only Model classes

*对于任何*生成的模型文件，导入应该正确，使得：
- Model 文件从 manager 文件导入 Manager
- Manager 文件从 queryset 文件导入 QuerySet
- __init__.py 仅导入 Model 类

**Validates: Requirements 11.5, 11.6, 11.7**

### Property 12: Generated Package Validity / 生成包有效性

*For any* ERModel rendered as a Django package, the generated package should be importable without errors and all Model classes should be accessible from the package root.

*对于任何*渲染为 Django 包的 ERModel，生成的包应该可以无错误导入，并且所有 Model 类应该可以从包根访问。

**Validates: Requirements 11.7, 12.1**

### Property 13: Package Structure Organization / 包结构组织

*For any* renderer class, it should be located in the correct package hierarchy:
- Base renderers in `renderers/base.py`
- Language-specific base classes in `renderers/<language>/base.py`
- Framework-specific renderers in `renderers/<language>/<framework>/renderer.py`
- Templates in `renderers/<language>/<framework>/templates/`

*对于任何*渲染器类，它应该位于正确的包层次结构中：
- 基础渲染器在 `renderers/base.py`
- 特定语言的基类在 `renderers/<language>/base.py`
- 特定框架的渲染器在 `renderers/<language>/<framework>/renderer.py`
- 模板在 `renderers/<language>/<framework>/templates/`

**Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6**

### Property 14: Backward Compatible Imports / 向后兼容的导入

*For any* old import path (e.g., `from x007007007.er.renderers import DjangoRenderer`), the import should still work and provide the same functionality as before.

*对于任何*旧的导入路径（例如，`from x007007007.er.renderers import DjangoRenderer`），导入应该仍然有效并提供与以前相同的功能。

**Validates: Requirements 13.7**

### Property 15: No Extra Blank Lines in Generated Code / 生成代码中没有额外的空行

*For any* ERModel rendered to code, the generated code should not contain consecutive blank lines (more than one blank line in a row) caused by Jinja2 directive lines.

*对于任何*渲染为代码的 ERModel，生成的代码不应包含由 Jinja2 指令行引起的连续空行（连续多于一个空行）。

**Validates: Requirements 14.4, 14.5**

### Property 16: Correct Python Indentation / 正确的 Python 缩进

*For any* generated Python code, all lines should have correct indentation according to Python syntax rules, regardless of how the template is formatted.

*对于任何*生成的 Python 代码，所有行都应根据 Python 语法规则具有正确的缩进，无论模板如何格式化。

**Validates: Requirements 14.6**

## Error Handling / 错误处理

### Code Serializer Error Handling / 代码序列化器错误处理

The code serializer should handle the following error cases:

代码序列化器应处理以下错误情况：

1. **Unsupported Types / 不支持的类型**: If given a value of an unsupported type (e.g., custom objects, functions), the serializer should raise a `ValueError` with a clear message indicating the unsupported type.

   如果给定不支持类型的值（例如自定义对象、函数），序列化器应引发 `ValueError`，并显示清楚的消息指示不支持的类型。

2. **Circular References / 循环引用**: If given a data structure with circular references, the serializer should detect this and raise a `ValueError` to prevent infinite recursion.

   如果给定具有循环引用的数据结构，序列化器应检测到这一点并引发 `ValueError` 以防止无限递归。

3. **Invalid Language Parameter / 无效的语言参数**: If given a language parameter other than 'django' or 'sqlalchemy', the serializer should raise a `ValueError`.

   如果给定除 'django' 或 'sqlalchemy' 之外的语言参数，序列化器应引发 `ValueError`。

### Template Rendering Error Handling / 模板渲染错误处理

If the code_value filter encounters an error during template rendering:

如果 code_value 过滤器在模板渲染期间遇到错误：

1. The error should propagate to the renderer
   错误应传播到渲染器
2. The renderer should provide context about which field/column caused the error
   渲染器应提供有关哪个字段/列导致错误的上下文
3. The error message should be clear and actionable
   错误消息应清晰且可操作

## Testing Strategy / 测试策略

### Unit Tests / 单元测试

Unit tests should focus on specific examples and edge cases:

单元测试应关注特定示例和边缘情况：

1. **CLI Default Change / CLI 默认值更改**
   - Test that CLI without --input-type uses 'toml'
   - Test that CLI with explicit --input-type mermaid still works
   - Test that CLI help shows correct default

2. **Code Serializer Examples / 代码序列化器示例**
   - Test None → "None"
   - Test True → "True", False → "False"
   - Test 42 → "42", 3.14 → "3.14"
   - Test empty string → '""'
   - Test string with only double quotes → uses single quotes
   - Test string with only single quotes → uses double quotes
   - Test string with both quotes → uses double quotes with escaping
   - Test string with newlines, tabs, backslashes
   - Test simple list → "[1, 2, 3]"
   - Test simple dict → "{'key': 'value'}"

3. **Filter Registration / 过滤器注册**
   - Test that Django renderer has 'code_value' filter
   - Test that SQLAlchemy renderer has 'code_value' filter

4. **Error Cases / 错误情况**
   - Test unsupported type raises ValueError
   - Test invalid language parameter raises ValueError

### Property-Based Tests / 基于属性的测试

Property tests should verify universal properties across many generated inputs (minimum 100 iterations per test):

属性测试应验证许多生成输入的通用属性（每个测试最少 100 次迭代）：

1. **Property 1: Serialization Round Trip**
   - Generate random Python values (None, bool, int, float, str, list, dict)
   - Serialize each value
   - Evaluate the serialized string
   - Assert the evaluated value equals the original
   - **Tag**: Feature: toml-default-and-code-serializer, Property 1: Serialization round trip

2. **Property 2: Smart Quote Selection**
   - Generate random strings with various quote combinations
   - Serialize each string
   - Verify quote selection follows the rules
   - Verify minimal escaping is used
   - **Tag**: Feature: toml-default-and-code-serializer, Property 2: Smart quote selection

3. **Property 3: Escape Sequence Preservation**
   - Generate random strings with special characters
   - Serialize and evaluate
   - Assert original string is recovered
   - **Tag**: Feature: toml-default-and-code-serializer, Property 3: Escape sequence preservation

4. **Property 4: Nested Structure Serialization**
   - Generate random nested structures
   - Serialize and evaluate
   - Assert structure is preserved
   - **Tag**: Feature: toml-default-and-code-serializer, Property 4: Nested structure serialization

5. **Property 5: Django Template Integration**
   - Generate random ERModels with various default values and comments
   - Render with Django renderer
   - Verify all values are properly serialized
   - **Tag**: Feature: toml-default-and-code-serializer, Property 5: Django template integration

6. **Property 6: SQLAlchemy Template Integration**
   - Generate random ERModels with various default values and comments
   - Render with SQLAlchemy renderer
   - Verify all values are properly serialized
   - **Tag**: Feature: toml-default-and-code-serializer, Property 6: SQLAlchemy template integration

7. **Property 7: Generated Code Validity**
   - Generate random ERModels
   - Render to Django and SQLAlchemy code
   - Parse generated code with ast.parse()
   - Assert no syntax errors
   - **Tag**: Feature: toml-default-and-code-serializer, Property 7: Generated code validity

8. **Property 8: Filter Registration**
   - Create renderer instances
   - Verify 'code_value' filter exists and is callable
   - **Tag**: Feature: toml-default-and-code-serializer, Property 8: Filter registration

9. **Property 9: Three-File Structure Generation**
   - Generate random ERModels with various numbers of entities
   - Render with DjangoPackageRenderer
   - Verify exactly 3N + 1 files are generated
   - **Tag**: Feature: toml-default-and-code-serializer, Property 9: Three-file structure generation

10. **Property 10: File Naming Convention**
    - Generate random ERModels with various entity names
    - Render with DjangoPackageRenderer
    - Verify all file names follow snake_case convention
    - Verify file names match pattern: <entity_name>_{queryset|manager|model}.py
    - **Tag**: Feature: toml-default-and-code-serializer, Property 10: File naming convention

11. **Property 11: Import Correctness**
    - Generate random ERModels
    - Render with DjangoPackageRenderer
    - Parse each generated file
    - Verify imports are correct (Model imports Manager, Manager imports QuerySet)
    - **Tag**: Feature: toml-default-and-code-serializer, Property 11: Import correctness

12. **Property 12: Generated Package Validity**
    - Generate random ERModels
    - Render with DjangoPackageRenderer to temporary directory
    - Attempt to import the package
    - Verify all Model classes are accessible
    - **Tag**: Feature: toml-default-and-code-serializer, Property 12: Generated package validity

13. **Property 13: Package Structure Organization**
    - Verify all renderer classes are in correct package locations
    - Verify base classes are in correct locations
    - Verify templates are in framework-specific directories
    - **Tag**: Feature: toml-default-and-code-serializer, Property 13: Package structure organization

14. **Property 14: Backward Compatible Imports**
    - Test all old import paths still work
    - Verify imported classes are the same as new paths
    - **Tag**: Feature: toml-default-and-code-serializer, Property 14: Backward compatible imports

15. **Property 15: No Extra Blank Lines in Generated Code**
    - Generate random ERModels with various conditional structures
    - Render to Django and SQLAlchemy code
    - Parse generated code and check for consecutive blank lines
    - Verify no more than one consecutive blank line exists
    - **Tag**: Feature: toml-default-and-code-serializer, Property 15: No extra blank lines

16. **Property 16: Correct Python Indentation**
    - Generate random ERModels
    - Render to Django and SQLAlchemy code
    - Parse generated code with ast.parse()
    - Verify all indentation is correct (no IndentationError)
    - **Tag**: Feature: toml-default-and-code-serializer, Property 16: Correct Python indentation

### Integration Tests / 集成测试

Integration tests should verify end-to-end workflows:

集成测试应验证端到端工作流：

1. **Full Pipeline Test / 完整管道测试**
   - Create a TOML file with entities having default values and comments with quotes
   - Run CLI with default input type (should use TOML)
   - Verify generated Django code has proper escaping
   - Verify generated code can be imported without errors

2. **Backward Compatibility Test / 向后兼容性测试**
   - Run existing test suite
   - Verify all tests pass
   - Verify existing Mermaid/PlantUML workflows still work

3. **Three-File Package Generation Test / 三文件包生成测试**
   - Create a TOML file with multiple entities
   - Run CLI with --output-dir flag
   - Verify three files are generated per entity
   - Verify __init__.py is generated correctly
   - Verify all files can be imported
   - Verify Model classes are accessible from package root

4. **Cross-File Import Test / 跨文件导入测试**
   - Generate a Django package with three-file structure
   - Import the package in a test Django project
   - Verify Manager and QuerySet are properly connected to Model
   - Verify custom queryset methods can be called through Manager

### Test Coverage Goals / 测试覆盖率目标

- Code serializer module: 100% coverage
- Renderer changes: 100% coverage of new filter registration code
- Template changes: Verified through integration tests
- CLI changes: 100% coverage of default parameter change
