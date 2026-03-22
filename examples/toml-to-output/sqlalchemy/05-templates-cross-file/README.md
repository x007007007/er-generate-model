# Template Example - Cross-File References

This example demonstrates how to define templates in one TOML file and reference them from entities in another TOML file.

## Features Demonstrated

- **Cross-File Template References**: Define templates in one file, use them in another
- **Template Registry**: The system maintains a unified registry of templates across all files
- **Shared Base Templates**: Create a library of reusable templates for your organization
- **Correct Import Paths**: Generated code uses correct import paths regardless of which file defined the template

## File Structure

```
05-templates-cross-file/
├── base_templates.toml    # Shared templates
├── entities.toml           # Entities that use the templates
└── README.md
```

## Template Organization

### base_templates.toml

Contains shared templates that can be used across your entire project:

```toml
[templates.AuditMixin]
package = "company.common.models.base"
# Defines audit trail fields: created_at, created_by, updated_at, updated_by

[templates.VersionMixin]
package = "company.common.models.base"
# Defines optimistic locking: version
```

### entities.toml

Defines entities that reference the templates:

```toml
[entities.PRODUCT]
extends = ["AuditMixin", "VersionMixin"]
# Product inherits audit trail and versioning
```

## Running the Example

You must specify both TOML files using the `--toml-files` option:

```bash
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/05-templates-cross-file/entities.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/05-templates-cross-file/output/ \
  --inheritance-mode reference \
  --toml-files examples/toml-to-output/sqlalchemy/05-templates-cross-file/base_templates.toml
```

**Important**: 
- The main input file is `entities.toml`
- Additional template files are specified with `--toml-files`
- You can specify `--toml-files` multiple times for multiple template files

## How It Works

1. **Template Discovery**: The system scans both `entities.toml` and `base_templates.toml`
2. **Registry Building**: All templates are registered in a unified registry
3. **Template Resolution**: When an entity references a template, it's resolved from the registry
4. **Mixin Generation**: Mixin files are generated based on the template's `package` field
5. **Entity Generation**: Entities import and inherit from the generated mixins

## Expected Output (Reference Mode)

### Mixin Files

Generated in `company/common/models/base_sqlalchemy/`:

- `audit_mixin.py` - Contains AuditMixin class
- `version_mixin.py` - Contains VersionMixin class

### Entity Files

Generated entity files will import from the correct paths:

```python
from company.common.models.base_sqlalchemy.audit_mixin import AuditMixin
from company.common.models.base_sqlalchemy.version_mixin import VersionMixin

class Product(AuditMixin, VersionMixin):
    __tablename__ = 'product'
    # ... entity-specific fields
```

## Use Cases

This pattern is ideal for:

- **Enterprise Applications**: Share common templates across multiple microservices
- **Multi-Module Projects**: Define base templates once, use everywhere
- **Team Collaboration**: Different teams can define entities while using shared templates
- **Template Libraries**: Create a library of standard templates for your organization

## Namespace Transformation

The `package` field in templates uses Django-style naming:
- Input: `company.common.models.base`
- Transformed: `company.common.models.base_sqlalchemy`
- File path: `company/common/models/base_sqlalchemy/`

This transformation is automatic and ensures consistent naming across frameworks.
