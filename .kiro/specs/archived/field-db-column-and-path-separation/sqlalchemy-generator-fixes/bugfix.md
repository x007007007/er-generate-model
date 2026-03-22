# Bugfix Requirements Document

## Introduction

The SQLAlchemy model generator produces incorrect code when generating models from TOML specifications. Three critical issues prevent the generated models from working correctly:

1. Primary key columns are missing the `primary_key=True` parameter
2. Foreign key columns use incorrect field names (relationship names instead of ID field names)
3. Reverse relationship definitions lack the `foreign_keys` parameter, causing ambiguity

These issues affect all generated SQLAlchemy models and prevent them from being used in production.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a column has `primary_key = true` in the TOML specification THEN the generated SQLAlchemy Column is missing the `primary_key=True` parameter

1.2 WHEN a foreign key relationship is defined with a `db_column` (e.g., `code_id`) THEN the generated Column uses the relationship name (e.g., `code`) instead of the foreign key field name (e.g., `code_id`)

1.3 WHEN a foreign key relationship is defined THEN the generated Column uses `Integer` type instead of the correct type from the TOML specification (e.g., `BigInteger`)

1.4 WHEN a reverse relationship is defined THEN the generated `relationship()` is missing the `foreign_keys` parameter, causing SQLAlchemy to fail with ambiguous foreign key errors

1.5 WHEN a foreign key column has `nullable = true` in the TOML specification THEN the generated Column is missing the `nullable=True` parameter

### Expected Behavior (Correct)

2.1 WHEN a column has `primary_key = true` in the TOML specification THEN the generated SQLAlchemy Column SHALL include `primary_key=True` parameter

2.2 WHEN a foreign key relationship is defined with a `db_column` (e.g., `code_id`) THEN the generated Column SHALL use the foreign key field name from `db_column` (e.g., `code_id`) instead of the relationship name

2.3 WHEN a foreign key relationship is defined THEN the generated Column SHALL use the correct type from the TOML specification (e.g., `BigInteger` when type is `bigint`)

2.4 WHEN a reverse relationship is defined THEN the generated `relationship()` SHALL include the `foreign_keys` parameter pointing to the foreign key column (e.g., `foreign_keys=[code_id]`)

2.5 WHEN a foreign key column has `nullable = true` in the TOML specification THEN the generated Column SHALL include `nullable=True` parameter

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a column is not a primary key THEN the system SHALL CONTINUE TO generate the Column without `primary_key=True`

3.2 WHEN a column is not a foreign key THEN the system SHALL CONTINUE TO generate the Column with the correct field name from the TOML specification

3.3 WHEN a column has a specific type in the TOML specification THEN the system SHALL CONTINUE TO map it to the correct SQLAlchemy type

3.4 WHEN a relationship does not have ambiguous foreign keys THEN the system SHALL CONTINUE TO generate valid `relationship()` definitions

3.5 WHEN generating table names, imports, and other model attributes THEN the system SHALL CONTINUE TO generate them correctly as before


## Bug Condition Analysis

### Bug Condition Function

The bug is triggered when generating SQLAlchemy models from TOML specifications. The bug condition can be defined as:

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type ColumnDefinition
  OUTPUT: boolean
  
  // Returns true when any of these conditions are met:
  RETURN (X.is_pk = true) OR 
         (X.is_fk = true AND X.db_column IS NOT NULL) OR
         (X.is_fk = true AND X.type = "bigint") OR
         (X.is_fk = true AND X.nullable = true) OR
         (X.has_reverse_relationship = true)
END FUNCTION
```

### Fix Checking Property

The property that must hold for all buggy inputs after the fix:

```pascal
// Property: Fix Checking - Correct SQLAlchemy Column Generation
FOR ALL X WHERE isBugCondition(X) DO
  result ← generateSQLAlchemyColumn'(X)
  
  // For primary keys
  IF X.is_pk = true THEN
    ASSERT result.contains("primary_key=True")
  END IF
  
  // For foreign keys with db_column
  IF X.is_fk = true AND X.db_column IS NOT NULL THEN
    ASSERT result.column_name = X.db_column
  END IF
  
  // For foreign keys with bigint type
  IF X.is_fk = true AND X.type = "bigint" THEN
    ASSERT result.column_type = "BigInteger"
  END IF
  
  // For nullable foreign keys
  IF X.is_fk = true AND X.nullable = true THEN
    ASSERT result.contains("nullable=True")
  END IF
  
  // For reverse relationships
  IF X.has_reverse_relationship = true THEN
    ASSERT result.contains("foreign_keys=[")
  END IF
END FOR
```

### Preservation Checking Property

For all non-buggy inputs, the behavior must remain unchanged:

```pascal
// Property: Preservation Checking
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT generateSQLAlchemyColumn(X) = generateSQLAlchemyColumn'(X)
END FOR
```

This ensures that columns without primary keys, foreign keys, or special attributes continue to be generated correctly as before.

## Concrete Examples

### Example 1: Primary Key Missing

**Input (TOML):**
```toml
[[entities.Translation.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false
unique = true
```

**Current Output (Incorrect):**
```python
id = Column(Integer, nullable=False, unique=True)
```

**Expected Output (Correct):**
```python
id = Column(Integer, primary_key=True, autoincrement=True)
```

### Example 2: Foreign Key Field Naming

**Input (TOML):**
```toml
[[entities.Translation.columns]]
name = "code"
type = "string"
db_column = "code_id"

[[relationships]]
left = "I18nCode"
right = "Translation"
type = "one-to-many"
left_column = "id"
right_column = "code_id"
```

**Current Output (Incorrect):**
```python
code = Column(String(255))
```

**Expected Output (Correct):**
```python
code_id = Column(BigInteger, ForeignKey("kkt_i18n_translations_i18ncodemodel.id"), nullable=True)
```

### Example 3: Reverse Relationship Missing foreign_keys

**Input (TOML):**
```toml
[[relationships]]
left = "I18nCode"
right = "Translation"
type = "one-to-many"
```

**Current Output (Incorrect):**
```python
i18ncode_rel = relationship("I18nCode", back_populates="translation_set")
```

**Expected Output (Correct):**
```python
i18ncode_rel = relationship("I18nCode", back_populates="translation_set", foreign_keys=[code_id])
```
