# Requirements Document

## Introduction

This document specifies the requirements for automatic namespace-based mixin generation in the ER model generator. The system enables automatic generation of SQLAlchemy mixin classes from TOML templates with automatic namespace transformation, allowing entities across multiple TOML files to reference shared mixins.

## Glossary

- **Template**: A reusable definition of columns that can be inherited by entities
- **Mixin**: A SQLAlchemy abstract base class that provides shared columns to entities
- **Namespace**: A Python package path (e.g., "kinkotech.common.models.base")
- **Export_Path**: The SQLAlchemy-specific package path where mixins are generated
- **Namespace_Transformer**: Component that converts Django package paths to SQLAlchemy equivalents
- **Template_Registry**: Component that discovers and manages templates across multiple TOML files
- **Mixin_Generator**: Component that generates SQLAlchemy mixin class files from templates
- **Entity_Renderer**: Component that renders entities with mixin inheritance support
- **Reference_Mode**: Inheritance mode where entities import and inherit from mixin classes
- **Flatten_Mode**: Inheritance mode where mixin fields are expanded inline in entities

## Requirements

### Requirement 1: Namespace Transformation

**User Story:** As a developer, I want Django package namespaces automatically transformed to SQLAlchemy equivalents, so that I can maintain consistent naming conventions across frameworks.

#### Acceptance Criteria

1. WHEN a Django package path is provided, THE Namespace_Transformer SHALL append `_sqlalchemy` suffix to the last component
2. WHEN a package path already has the `_sqlalchemy` suffix, THE Namespace_Transformer SHALL return it unchanged
3. WHEN transformation is applied twice to the same package, THE Namespace_Transformer SHALL return the same result (idempotence)
4. THE Namespace_Transformer SHALL preserve all package components except the last one
5. WHEN an empty or null package is provided, THE Namespace_Transformer SHALL raise a validation error

### Requirement 2: Template Discovery

**User Story:** As a developer, I want templates discovered from multiple TOML files, so that I can organize my model definitions across multiple files.

#### Acceptance Criteria

1. WHEN multiple TOML files are provided, THE Template_Registry SHALL discover all templates from all files
2. WHEN a template has a `package` but no `export_path`, THE Template_Registry SHALL auto-derive the `export_path` using namespace transformation
3. WHEN a template has both `package` and `export_path`, THE Template_Registry SHALL use the explicit `export_path`
4. WHEN duplicate template names exist across files, THE Template_Registry SHALL raise a conflict error
5. WHEN a TOML file is malformed, THE Template_Registry SHALL raise a parsing error with file details

### Requirement 3: Template Resolution

**User Story:** As a developer, I want to reference templates by name from any TOML file, so that I can reuse common mixins across my project.

#### Acceptance Criteria

1. WHEN an entity references a template by name, THE Template_Registry SHALL resolve it from any loaded TOML file
2. WHEN a template name cannot be resolved, THE Template_Registry SHALL raise a TemplateNotFoundError
3. THE Template_Registry SHALL maintain a unified registry of all templates across files
4. WHEN templates are discovered, THE Template_Registry SHALL validate that all have valid export paths

### Requirement 4: Mixin File Generation

**User Story:** As a developer, I want mixin classes automatically generated from templates, so that I don't have to manually create base classes.

#### Acceptance Criteria

1. WHEN a template is processed, THE Mixin_Generator SHALL create a Python file at the path derived from export_path
2. THE Mixin_Generator SHALL generate a class with `__abstract__ = True` attribute
3. THE Mixin_Generator SHALL include all columns from the template in the generated class
4. THE Mixin_Generator SHALL create the directory structure if it doesn't exist
5. WHEN the output directory is not writable, THE Mixin_Generator SHALL raise a permission error

### Requirement 5: Entity Rendering with Mixin Inheritance

**User Story:** As a developer, I want entities to inherit from generated mixins, so that I can reuse common fields across entities.

#### Acceptance Criteria

1. WHEN an entity extends templates in reference mode, THE Entity_Renderer SHALL generate import statements for the mixin classes
2. WHEN an entity extends templates in reference mode, THE Entity_Renderer SHALL include mixins in the class inheritance list
3. WHEN an entity extends templates in flatten mode, THE Entity_Renderer SHALL expand all mixin fields inline
4. THE Entity_Renderer SHALL preserve the order of fields from templates and entity-specific columns
5. WHEN a referenced template doesn't exist, THE Entity_Renderer SHALL raise a TemplateNotFoundError

### Requirement 6: File Path Construction

**User Story:** As a developer, I want mixin files placed in the correct directory structure, so that Python imports work correctly.

#### Acceptance Criteria

1. WHEN generating a mixin file, THE Mixin_Generator SHALL convert export_path dots to directory separators
2. WHEN generating a mixin file, THE Mixin_Generator SHALL convert the class name to snake_case for the filename
3. THE Mixin_Generator SHALL append `.py` extension to the filename
4. THE Mixin_Generator SHALL create all intermediate directories in the path
5. WHEN the file path contains invalid characters, THE Mixin_Generator SHALL raise a validation error

### Requirement 7: Template Validation

**User Story:** As a developer, I want templates validated during discovery, so that I catch configuration errors early.

#### Acceptance Criteria

1. WHEN a template has neither `package` nor `export_path`, THE Template_Registry SHALL raise a validation error
2. WHEN a template has an empty columns list, THE Template_Registry SHALL raise a validation error
3. WHEN a package path contains invalid Python identifiers, THE Template_Registry SHALL raise a validation error
4. THE Template_Registry SHALL validate that export_path is a valid Python package path
5. THE Template_Registry SHALL validate that template names are valid Python identifiers

### Requirement 8: Cross-File Template References

**User Story:** As a developer, I want to reference templates defined in other TOML files, so that I can share common mixins across my project structure.

#### Acceptance Criteria

1. WHEN an entity in file A references a template defined in file B, THE Template_Registry SHALL resolve the template successfully
2. THE Template_Registry SHALL maintain metadata about which file each template comes from
3. WHEN generating entities, THE Entity_Renderer SHALL generate correct import paths regardless of which file defined the template
4. THE Template_Registry SHALL support templates and entities in the same TOML file
5. THE Template_Registry SHALL support templates and entities in different TOML files

### Requirement 9: Code Generation Quality

**User Story:** As a developer, I want generated code to be valid and well-formatted, so that I can use it immediately without manual fixes.

#### Acceptance Criteria

1. THE Mixin_Generator SHALL generate syntactically valid Python code
2. THE Mixin_Generator SHALL include proper SQLAlchemy imports in generated files
3. THE Mixin_Generator SHALL format code according to Python conventions
4. THE Entity_Renderer SHALL generate valid import statements for mixin classes
5. THE Entity_Renderer SHALL generate valid class inheritance syntax

### Requirement 10: Error Reporting

**User Story:** As a developer, I want clear error messages when configuration is invalid, so that I can quickly fix issues.

#### Acceptance Criteria

1. WHEN a template conflict occurs, THE Template_Registry SHALL report both conflicting file paths
2. WHEN a template is not found, THE Template_Registry SHALL report the template name and requesting entity
3. WHEN a package path is invalid, THE Namespace_Transformer SHALL report the invalid component
4. WHEN file generation fails, THE Mixin_Generator SHALL report the target path and error reason
5. WHEN TOML parsing fails, THE Template_Registry SHALL report the file path and line number if available
