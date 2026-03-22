# Design Document: Django-Style Foreign Key Relationships

## Overview

This feature enhances the SQLAlchemy model generator to support Django-style foreign key relationship naming conventions. The core issue is that when a TOML definition specifies a foreign key with a logical name (e.g., "code") and a database column name (e.g., "code_id"), the current generator creates awkward relationship names (e.g., "i18ncode_rel") instead of using the intuitive logical name.

The solution implements a naming convention where:
- Database columns use the `_id` suffix (e.g., `code_id`)
- Relationship objects use the logical name without suffix (e.g., `code`)
- The relationship's `foreign_keys` parameter explicitly references the column

This aligns with Django ORM conventions and makes SQLAlchemy models more intuitive for developers migrating from Django.

## Architecture

### Component Overview

The feature modifies the SQLAlchemy renderer component within the er-gen-core package:

```
packages/er-gen-core/
└── src/x007007007/er/
    ├── models.py                    # Data models (Column, Entity, Relationship)
    ├── renderers/python/sqlalchemy/
    │   ├── renderer.py              # Main renderer class
    │   └── templates/
    │       ├── sqlalchemy_model.j2         # Single-file template
    │       └── sqlalchemy_single_model.j2  # Multi-file template
    └── converters/toml_parser.py    # TOML parsing (marks columns as FK)
```

### Data Flow

1. **Input**: TOML definition with entities, columns, and relationships
2. **Parsing**: TOML parser creates ERModel with entities and relationships
3. **FK Detection**: Parser marks columns as foreign keys based on relationship definitions
4. **Template Rendering**: Jinja2 templates generate SQLAlchemy model code
5. **Output**: Python files with SQLAlchemy model classes

### Key Design Decisions

**Decision 1: Use Jinja2 Template Logic for Naming**
- Rationale: Keeps rendering logic in templates, making it easier to maintain and customize
- Alternative considered: Pre-processing in Python code (rejected due to complexity)

**Decision 2: Explicit `foreign_keys` Parameter**
- Rationale: SQLAlchemy requires explicit foreign_keys when the column name doesn't match the relationship name
- This is necessary for Django-style naming to work correctly

**Decision 3: Infer `db_column` from Logical Name**
- Rationale: Backward compatibility - if db_column is not specified, append `_id` to the logical name
- This allows existing TOML files to work without modification

## Components and Interfaces

### Modified Components

#### 1. SQLAlchemy Jinja2 Templates

**Template: sqlalchemy_model.j2 and sqlalchemy_single_model.j2**

Current behavior:
- Uses `col.name` for both column definition and relationship naming
- Generates relationship names like `{entity_name}_rel`

New behavior:
- Uses `col.db_column` for column definition (with _id suffix)
- Uses `col.name` for relationship object naming (without _id suffix)
- Adds `foreign_keys=[{col.db_column}]` parameter to relationship

**Key Template Variables:**
- `col.name`: Logical field name (e.g., "code")
- `col.db_column`: Database column name (e.g., "code_id")
- `col.is_fk`: Boolean flag indicating foreign key
- `rel.left_entity`, `rel.right_entity`: Related entity names
- `rel.left_column`, `rel.right_column`: Foreign key column names

#### 2. TOML Parser (FK Detection)

**File: converters/toml_parser.py**

The parser already marks columns as foreign keys by setting `col.is_fk = True` when a column name matches a relationship's `right_column`. This logic needs to be enhanced to:

1. Match against both `col.name` and `col.db_column`
2. Ensure `db_column` is set (infer from `name` + "_id" if not specified)
3. Validate that foreign key columns end with `_id`

#### 3. Renderer Class

**File: renderers/python/sqlalchemy/renderer.py**

No significant changes required. The renderer passes the ERModel to templates, which handle the naming logic.

### Component Interfaces

#### Column Data Model

```python
@dataclass
class Column:
    name: str           # Logical name (e.g., "code")
    db_column: str      # Database column name (e.g., "code_id")
    type: str
    is_fk: bool = False
    nullable: bool = True
    # ... other attributes
```

#### Relationship Data Model

```python
@dataclass
class Relationship:
    left_entity: str
    right_entity: str
    relation_type: str  # "one-to-one", "one-to-many", "many-to-many"
    left_column: Optional[str] = None
    right_column: Optional[str] = None
```

## Data Models

### Input: TOML Definition

```toml
[[relationships]]
left = "I18nCode"
right = "Translation"
type = "one-to-many"
left_column = "id"
right_column = "code_id"

[entities.Translation]
table_name = "translation"

[[entities.Translation.columns]]
name = "code"           # Logical name for relationship
db_column = "code_id"   # Database column name
type = "bigint"
```

### Internal: ERModel Structure

```python
ERModel(
    entities={
        "Translation": Entity(
            name="Translation",
            table_name="translation",
            columns=[
                Column(
                    name="code",
                    db_column="code_id",
                    type="bigint",
                    is_fk=True
                )
            ]
        ),
        "I18nCode": Entity(...)
    },
    relationships=[
        Relationship(
            left_entity="I18nCode",
            right_entity="Translation",
            relation_type="one-to-many",
            left_column="id",
            right_column="code_id"
        )
    ]
)
```

### Output: SQLAlchemy Model

```python
class Translation(Base):
    __tablename__ = 'translation'
    
    # Column uses db_column name with _id suffix
    code_id = Column(
        BigInteger,
        ForeignKey('i18ncode.id'),
        nullable=True
    )
    
    # Relationship uses logical name without _id suffix
    code = relationship(
        "I18nCode",
        back_populates="translation_set",
        foreign_keys=[code_id]  # Explicit reference
    )
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Django-Style Naming Convention

*For any* TOML definition with a foreign key column where `name` is specified and `db_column` ends with `_id`, the generated SQLAlchemy model SHALL create:
- A Column definition using the `db_column` name (with `_id` suffix)
- A relationship object using the `name` (without `_id` suffix)
- The relationship SHALL include `foreign_keys=[{db_column}]` parameter

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Foreign Key Column Attributes Preservation

*For any* foreign key column with attributes (nullable, unique, indexed, default, comment), the generated Column definition SHALL preserve all specified attributes in addition to the ForeignKey constraint.

**Validates: Requirements 2.3**

### Property 3: Foreign Key Constraint Correctness

*For any* relationship definition, the generated ForeignKey constraint SHALL reference the correct target table and column in the format:
- `{table_prefix}_{table_name}.{column_name}` when table_prefix is configured
- `{table_name}.{column_name}` when table_prefix is not configured

**Validates: Requirements 2.2, 3.3, 5.4, 7.1, 7.2, 7.3**

### Property 4: Foreign Key Type Matching

*For any* foreign key column, the generated Column type (BigInteger, Integer, etc.) SHALL match the type of the referenced primary key column in the target entity.

**Validates: Requirements 5.3**

### Property 5: Bidirectional Relationship Configuration

*For any* relationship definition, the generator SHALL create relationship objects on both entities with correct `back_populates` parameters that reference each other, and the `uselist` parameter SHALL be set correctly based on the relationship type (False for one-to-one, True for one-to-many).

**Validates: Requirements 3.1, 3.4, 5.2**

### Property 6: Multiple Foreign Keys Handling

*For any* entity with multiple foreign key columns, the generator SHALL create:
- Separate Column definitions for each foreign key with unique names
- Separate relationship objects for each foreign key with unique names
- Each relationship SHALL reference its corresponding foreign key column in the `foreign_keys` parameter

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 7: Implicit db_column Inference

*For any* foreign key column where `db_column` is not explicitly specified in the TOML definition, the generator SHALL infer the database column name by appending `_id` to the logical `name`.

**Validates: Requirements 4.1**

### Property 8: Foreign Key Detection from Relationships

*For any* column where the column's `name` or `db_column` matches a relationship's `right_column`, the generator SHALL mark that column as a foreign key (is_fk=True) and generate appropriate ForeignKey constraint.

**Validates: Requirements 3.2**

### Property 9: Table Prefix Consistency

*For any* ERModel with a configured table_prefix, all ForeignKey constraint references SHALL consistently apply the prefix to all table names in the format `{prefix}_{table_name}`.

**Validates: Requirements 7.4**

### Property 10: Relationship Column Validation

*For any* relationship definition, if the `left_column` or `right_column` references a column that does not exist in the respective entity, the generator SHALL produce a descriptive error message identifying the missing column and entity.

**Validates: Requirements 8.4**

## Error Handling

### Validation Errors

The generator will validate TOML input and produce clear error messages for:

1. **Missing Relationship for Foreign Key**
   - Error: "Column '{column_name}' in entity '{entity_name}' is marked as foreign key but no matching relationship found"
   - Occurs when: `is_fk=True` but no relationship references this column

2. **Non-existent Entity Reference**
   - Error: "Relationship references non-existent entity: '{entity_name}'"
   - Occurs when: Relationship's left_entity or right_entity doesn't exist in the model

3. **Non-existent Column Reference**
   - Error: "Relationship references non-existent column '{column_name}' in entity '{entity_name}'"
   - Occurs when: Relationship's left_column or right_column doesn't exist

4. **Missing _id Suffix Warning**
   - Warning: "Foreign key column '{column_name}' in entity '{entity_name}' has db_column '{db_column}' without '_id' suffix. Consider using Django-style naming."
   - Occurs when: Column is a foreign key but db_column doesn't end with `_id`

### Error Recovery

- Validation errors will halt code generation and display all errors at once
- Warnings will be displayed but won't prevent code generation
- The ERModel.validate() method will be enhanced to check these conditions

### Backward Compatibility

To maintain backward compatibility:

1. **Existing TOML files without db_column**: Will automatically infer `{name}_id` as the database column name
2. **Existing templates and mixins**: Will continue to work as the Column and Entity data models are unchanged
3. **Existing relationship naming**: If a TOML file explicitly uses the old naming convention, it will be preserved

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior (e.g., the Translation/I18nCode example from requirements)
- Edge cases (empty entities, missing attributes, etc.)
- Error conditions (invalid TOML, missing relationships, etc.)
- Integration between parser and renderer

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs (the 10 correctness properties above)
- Comprehensive input coverage through randomization
- Ensuring the generator handles all valid TOML variations correctly

### Property-Based Testing Configuration

**Library**: Use Hypothesis for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test must reference its design document property using the tag format:
  - `# Feature: django-style-foreign-key-relationships, Property 1: Django-Style Naming Convention`

**Test Structure**:
```python
from hypothesis import given, strategies as st
import hypothesis

@given(
    entity_name=st.text(min_size=1),
    logical_name=st.text(min_size=1),
    db_column=st.text(min_size=4).filter(lambda x: x.endswith('_id'))
)
@hypothesis.settings(max_examples=100)
def test_property_1_django_style_naming(entity_name, logical_name, db_column):
    """
    Feature: django-style-foreign-key-relationships
    Property 1: Django-Style Naming Convention
    
    For any TOML definition with a foreign key column where name is specified
    and db_column ends with _id, the generated SQLAlchemy model SHALL create
    a Column using db_column and a relationship using name.
    """
    # Test implementation
    pass
```

### Unit Test Coverage

Unit tests should cover:

1. **Basic Django-style naming**: The Translation/I18nCode example from requirements
2. **Multiple foreign keys**: Entity with 2+ foreign keys to different entities
3. **Self-referential foreign keys**: Entity with FK to itself
4. **Table prefixes**: Foreign keys with and without table prefixes
5. **Column attributes**: Foreign keys with various nullable, unique, indexed combinations
6. **Implicit db_column**: Foreign keys without explicit db_column specification
7. **Error cases**: Invalid relationships, missing entities, missing columns
8. **Backward compatibility**: Existing TOML files continue to work

### Integration Testing

Integration tests should verify:

1. **End-to-end generation**: TOML → ERModel → SQLAlchemy code → Valid Python
2. **Generated code is executable**: Import generated models without errors
3. **SQLAlchemy validation**: Generated models pass SQLAlchemy's internal validation
4. **Database schema creation**: Generated models can create actual database tables

### Test File Organization

```
packages/er-gen-core/tests/
├── test_unit_sqlalchemy_generator.py          # Unit tests
├── test_property_django_fk_naming.py          # Property-based tests
├── test_integration_sqlalchemy_generator.py   # Integration tests
└── fixtures/
    └── django_fk_examples.toml                # Test data
```
