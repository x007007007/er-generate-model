# Requirements Document

## Introduction

This feature enhances the SQLAlchemy model generator to support Django-style foreign key relationship naming conventions. Currently, when a TOML definition specifies a foreign key with a logical name (e.g., "code") and a database column name (e.g., "code_id"), the generator creates a database column with the correct name but generates relationship objects with awkward naming (e.g., "i18ncode_rel"). This feature will align the generator's output with Django ORM conventions, where the database column uses the `_id` suffix and the relationship object uses the original logical name.

## Glossary

- **Generator**: The SQLAlchemy model code generator that transforms TOML entity definitions into Python SQLAlchemy model classes
- **Foreign_Key_Column**: The database column that stores the foreign key ID value (e.g., `code_id`)
- **Relationship_Object**: The SQLAlchemy relationship attribute that provides ORM access to the related entity instance (e.g., `code`)
- **TOML_Definition**: The input configuration file that defines entities, columns, and relationships
- **Django_Style_Naming**: The naming convention where foreign key columns have `_id` suffix and relationship objects use the logical name without suffix

## Requirements

### Requirement 1: Generate Django-Style Relationship Names

**User Story:** As a developer migrating from Django to SQLAlchemy, I want relationship objects to use the logical field name, so that my code remains intuitive and consistent with Django conventions.

#### Acceptance Criteria

1. WHEN a TOML definition specifies a column with `name = "code"` and `db_column = "code_id"`, THE Generator SHALL create a Relationship_Object named `code`
2. WHEN a TOML definition specifies a column with `name = "code"` and `db_column = "code_id"`, THE Generator SHALL create a Foreign_Key_Column named `code_id`
3. THE Relationship_Object SHALL reference the Foreign_Key_Column in its `foreign_keys` parameter
4. FOR ALL foreign key columns, THE Generator SHALL produce both a Foreign_Key_Column with `_id` suffix and a Relationship_Object using the original name

### Requirement 2: Maintain Database Column Naming

**User Story:** As a database administrator, I want foreign key columns to maintain the `_id` suffix convention, so that database schema remains clear and consistent.

#### Acceptance Criteria

1. WHEN a TOML definition specifies `db_column` with an `_id` suffix, THE Generator SHALL create a Foreign_Key_Column with that exact name
2. THE Foreign_Key_Column SHALL include the ForeignKey constraint referencing the target table
3. THE Foreign_Key_Column SHALL preserve all column attributes (nullable, unique, indexed, default, comment)
4. WHEN a relationship is defined, THE Generator SHALL ensure the Foreign_Key_Column name ends with `_id`

### Requirement 3: Support Relationship Type Detection

**User Story:** As a developer, I want the generator to correctly identify foreign key relationships from TOML definitions, so that appropriate relationship objects are created.

#### Acceptance Criteria

1. WHEN a TOML definition includes a relationship with `type = "one-to-many"`, THE Generator SHALL create appropriate Relationship_Objects on both entities
2. WHEN a column name matches a relationship's `right_column`, THE Generator SHALL mark that column as a foreign key
3. THE Generator SHALL use the relationship's `left_entity` to determine the target entity for the ForeignKey constraint
4. THE Generator SHALL generate the `back_populates` parameter based on the relationship type and entity names

### Requirement 4: Preserve Backward Compatibility

**User Story:** As a maintainer of existing SQLAlchemy models, I want the generator to handle both old and new naming conventions, so that existing code continues to work during migration.

#### Acceptance Criteria

1. WHEN a TOML definition does not specify `db_column`, THE Generator SHALL infer the Foreign_Key_Column name by appending `_id` to the logical name
2. THE Generator SHALL continue to support all existing column types and attributes
3. THE Generator SHALL maintain compatibility with existing template inheritance and mixin patterns
4. WHERE a TOML definition explicitly specifies relationship naming preferences, THE Generator SHALL honor those preferences

### Requirement 5: Generate Correct SQLAlchemy Syntax

**User Story:** As a developer, I want generated models to use correct SQLAlchemy syntax, so that models work without manual corrections.

#### Acceptance Criteria

1. THE Relationship_Object SHALL include the `foreign_keys` parameter when the foreign key column is defined in the same class
2. THE Relationship_Object SHALL use the correct relationship type (uselist parameter) based on the relationship definition
3. THE Foreign_Key_Column SHALL use the correct SQLAlchemy column type (BigInteger, Integer, etc.) matching the referenced primary key
4. THE ForeignKey constraint SHALL reference the correct table and column using the format `table_name.column_name`

### Requirement 6: Handle Multiple Foreign Keys

**User Story:** As a developer working with complex data models, I want to define multiple foreign keys in a single entity, so that I can model real-world relationships.

#### Acceptance Criteria

1. WHEN an entity has multiple foreign key columns, THE Generator SHALL create separate Foreign_Key_Columns for each
2. WHEN an entity has multiple foreign key columns, THE Generator SHALL create separate Relationship_Objects for each
3. THE Generator SHALL ensure each Relationship_Object references its corresponding Foreign_Key_Column
4. THE Generator SHALL generate unique names for all Foreign_Key_Columns and Relationship_Objects within an entity

### Requirement 7: Support Table Name Prefixes

**User Story:** As a developer working in a multi-tenant or namespaced database, I want foreign key constraints to respect table prefixes, so that references remain valid.

#### Acceptance Criteria

1. WHERE a table_prefix is configured, THE Generator SHALL apply it to ForeignKey constraint references
2. THE Generator SHALL construct ForeignKey references as `{prefix}_{table_name}.{column_name}` when prefix is present
3. THE Generator SHALL construct ForeignKey references as `{table_name}.{column_name}` when prefix is absent
4. THE Generator SHALL apply table prefixes consistently across all relationship definitions

### Requirement 8: Validate TOML Input

**User Story:** As a developer, I want clear error messages when TOML definitions are invalid, so that I can quickly fix configuration issues.

#### Acceptance Criteria

1. WHEN a column is marked as a foreign key but no matching relationship exists, THE Generator SHALL produce a descriptive error message
2. WHEN a relationship references non-existent entities or columns, THE Generator SHALL produce a descriptive error message
3. WHEN a `db_column` is specified without an `_id` suffix for a foreign key, THE Generator SHALL produce a warning message
4. THE Generator SHALL validate that relationship `left_column` and `right_column` reference existing columns in their respective entities
