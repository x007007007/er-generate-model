# Django-Style Foreign Key Test Fixtures

This directory contains test fixtures for the Django-style foreign key relationships feature. Each fixture is designed to test specific aspects of the feature as outlined in the requirements and design documents.

## Fixture Overview

### 1. django_fk_basic/
**Purpose:** Basic Django-style foreign key naming convention  
**Key Test Case:** Translation entity with foreign key to I18nCode (primary example from requirements)  
**Tests:**
- Column uses `db_column` name with `_id` suffix (code_id)
- Relationship uses logical `name` without suffix (code)
- ForeignKey constraint references correct table and column
- Relationship includes `foreign_keys=[code_id]` parameter

**Requirements Validated:** 1.1, 1.2, 1.3, 1.4, 2.2, 3.3, 5.4

### 2. django_fk_multiple/
**Purpose:** Multiple foreign keys in a single entity  
**Key Test Case:** Translation entity with FKs to both I18nCode and I18nBlock  
**Tests:**
- Each FK column has unique name (code_id, block_id)
- Each relationship object has unique name (code, block)
- Each relationship references its corresponding FK column
- All FKs are correctly detected and marked

**Requirements Validated:** 6.1, 6.2, 6.3, 6.4

### 3. django_fk_self_referential/
**Purpose:** Self-referential foreign key  
**Key Test Case:** Category entity with parent-child relationship to itself  
**Tests:**
- Self-referential FK is correctly detected
- Relationship references same entity for both sides
- ForeignKey constraint references same table
- Nullable FK for optional parent

**Requirements Validated:** 1.1, 1.2, 1.3, 2.3, 6.1

### 4. django_fk_with_prefix/
**Purpose:** Foreign keys with table prefix  
**Key Test Case:** User-Post relationship with "app" table prefix  
**Tests:**
- ForeignKey constraint uses format `{prefix}_{table_name}.{column_name}`
- Table prefix is applied consistently
- Relationship naming remains unchanged by prefix

**Requirements Validated:** 7.1, 7.2, 7.3, 7.4

### 5. django_fk_attributes/
**Purpose:** Foreign keys with various column attributes  
**Key Test Case:** Employee entity with FKs having different attributes  
**Tests:**
- Nullable FK (department_id with nullable=true)
- Non-nullable FK (company_id with nullable=false)
- Indexed FK columns
- FK columns with comments
- All attributes are preserved in Column definition

**Requirements Validated:** 2.3

### 6. django_fk_implicit_db_column/
**Purpose:** Foreign key without explicit db_column specification  
**Key Test Case:** Book entity with author FK where db_column is not specified  
**Tests:**
- db_column is inferred as `{name}_id` (author → author_id)
- Backward compatibility with existing TOML files
- Implicit inference happens before template rendering

**Requirements Validated:** 4.1

### 7. django_fk_complex/
**Purpose:** Complex scenario combining multiple features  
**Key Test Case:** Blog system with multiple entities, FKs, table prefix, and self-referential FK  
**Tests:**
- Multiple FKs in same entity (Post has author_id and category_id)
- Self-referential FK (Comment has parent_id)
- Table prefix applied to all ForeignKey constraints
- Various column attributes (nullable, indexed, unique, comments)
- Multiple relationship types (one-to-many)
- Integration of all features working together

**Requirements Validated:** Multiple requirements combined (1.x, 2.x, 6.x, 7.x)

## Usage in Tests

These fixtures are used in three types of tests:

### Unit Tests
- Test specific examples demonstrating correct behavior
- Test edge cases and error conditions
- Verify template rendering produces expected output
- Located in: `test_unit_sqlalchemy_generator.py`

### Property-Based Tests
- Test universal properties across all valid inputs
- Use Hypothesis to generate variations of these fixtures
- Validate correctness properties from design document
- Located in: `test_property_django_fk_naming.py`

### Integration Tests
- Test end-to-end TOML → ERModel → SQLAlchemy code pipeline
- Verify generated code is valid and executable Python
- Ensure SQLAlchemy validates generated models
- Located in: `test_integration_sqlalchemy_generator.py`

## Expected Output Patterns

For a fixture with:
```toml
[[entities.Translation.columns]]
name = "code"
db_column = "code_id"
type = "bigint"
```

Expected SQLAlchemy output:
```python
class Translation(Base):
    __tablename__ = 'translation'
    
    # Column uses db_column name
    code_id = Column(BigInteger, ForeignKey('i18n_code.id'))
    
    # Relationship uses logical name
    code = relationship("I18nCode", foreign_keys=[code_id], back_populates="translation_set")
```

## Adding New Fixtures

When adding new fixtures:
1. Create a new directory under `tests/assets/`
2. Name it with `django_fk_` prefix for consistency
3. Include an `input.toml` file with the test data
4. Add documentation to this README
5. Reference specific requirements being validated
6. Update relevant test files to use the new fixture

## Related Files

- **Requirements:** `.kiro/specs/django-style-foreign-key-relationships/requirements.md`
- **Design:** `.kiro/specs/django-style-foreign-key-relationships/design.md`
- **Tasks:** `.kiro/specs/django-style-foreign-key-relationships/tasks.md`
- **Templates:** `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/`
- **Parser:** `packages/er-gen-core/src/x007007007/er/converters/toml_parser.py`
