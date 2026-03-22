# SQLAlchemy Generator Fixes - Bugfix Design

## Overview

The SQLAlchemy model generator produces incorrect code when generating models from TOML specifications. This design addresses three critical issues: (1) missing `primary_key=True` parameter on primary key columns, (2) incorrect foreign key field naming using relationship names instead of ID field names, and (3) missing `foreign_keys` parameter in reverse relationships causing SQLAlchemy ambiguity errors. The fix involves modifying the Jinja2 template to correctly handle these cases while preserving all existing functionality for non-buggy inputs.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when columns have primary_key=true, foreign keys with db_column, or reverse relationships are defined in TOML
- **Property (P)**: The desired behavior - correct SQLAlchemy Column and relationship() generation with all required parameters
- **Preservation**: Existing column and relationship generation for non-buggy inputs that must remain unchanged
- **sqlalchemy_model.j2**: The Jinja2 template in `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_model.j2` that generates SQLAlchemy model code
- **db_column**: The TOML attribute that specifies the actual database column name for foreign keys (e.g., "code_id" when the relationship name is "code")
- **isBugCondition**: Function that identifies columns affected by the bug (primary keys, foreign keys with db_column, nullable foreign keys, or entities with reverse relationships)

## Bug Details

### Fault Condition

The bug manifests when the Jinja2 template processes TOML column definitions with specific attributes. The template is either missing parameter generation logic for primary keys, using incorrect field names for foreign keys, using wrong types for foreign key columns, missing nullable parameters, or omitting the foreign_keys parameter in reverse relationships.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type ColumnDefinition OR RelationshipDefinition
  OUTPUT: boolean
  
  RETURN (input.is_pk = true)
         OR (input.is_fk = true AND input.db_column IS NOT NULL)
         OR (input.is_fk = true AND input.type = "bigint")
         OR (input.is_fk = true AND input.nullable = true)
         OR (input.is_reverse_relationship = true)
END FUNCTION
```

### Examples

- **Primary Key Example**: Column with `primary_key = true` generates `id = Column(Integer, nullable=False, unique=True)` instead of `id = Column(Integer, primary_key=True, autoincrement=True)`
- **Foreign Key Naming Example**: Column with `name = "code"` and `db_column = "code_id"` generates `code = Column(Integer, ForeignKey(...))` instead of `code_id = Column(BigInteger, ForeignKey(...))`
- **Foreign Key Type Example**: Column with `type = "bigint"` generates `Column(Integer, ...)` instead of `Column(BigInteger, ...)`
- **Nullable Foreign Key Example**: Column with `nullable = true` generates `code_id = Column(BigInteger, ForeignKey(...))` without `nullable=True` parameter
- **Reverse Relationship Example**: Relationship generates `i18ncode_rel = relationship("I18nCode", back_populates="translation_set")` instead of `i18ncode_rel = relationship("I18nCode", back_populates="translation_set", foreign_keys=[code_id])`

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Non-primary key columns must continue to generate without `primary_key=True`
- Non-foreign key columns must continue to use their TOML-specified field names
- Type mapping for non-foreign key columns must remain unchanged
- Relationships without ambiguous foreign keys must continue to generate valid definitions
- Table names, imports, and other model attributes must continue to generate correctly

**Scope:**
All inputs that do NOT involve primary keys, foreign keys with db_column, bigint foreign keys, nullable foreign keys, or reverse relationships should be completely unaffected by this fix. This includes:
- Regular string, text, integer, boolean, date, datetime columns
- Columns without primary_key=true
- Columns without is_fk=true
- Forward relationships (left entity side)
- Many-to-many relationships

## Hypothesized Root Cause

Based on the bug description and template analysis, the most likely issues are:

1. **Missing Primary Key Parameter Logic**: The template's foreign key branch (lines 52-72) does not include `primary_key=True` in the param_list when `col.is_pk` is true, causing primary key foreign keys to lose their primary key designation

2. **Incorrect Field Name Usage**: The template uses `col.name` (line 72) for foreign key columns instead of checking for `col.db_column` first, causing the relationship name to be used instead of the actual database column name

3. **Hardcoded Integer Type**: The template uses hardcoded `Integer` type (line 72) for all foreign key columns instead of using the `sqlalchemy_column_type` filter to get the correct type from the TOML specification

4. **Missing Nullable Parameter**: The template only adds `nullable=False` when `not col.nullable` (line 56), but doesn't add `nullable=True` when `col.nullable` is true, causing nullable foreign keys to default to non-nullable

5. **Missing foreign_keys Parameter**: The template generates relationship() definitions (lines 127-149) without the `foreign_keys` parameter, causing SQLAlchemy to fail when multiple foreign keys point to the same table

## Correctness Properties

Property 1: Fault Condition - Correct SQLAlchemy Generation

_For any_ column or relationship definition where the bug condition holds (isBugCondition returns true), the fixed template SHALL generate correct SQLAlchemy code with: (1) `primary_key=True` for primary keys, (2) correct field names using db_column for foreign keys, (3) correct types from TOML for foreign keys, (4) `nullable=True` for nullable foreign keys, and (5) `foreign_keys` parameter for reverse relationships.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Preservation - Non-Buggy Input Behavior

_For any_ column or relationship definition where the bug condition does NOT hold (isBugCondition returns false), the fixed template SHALL produce exactly the same output as the original template, preserving all existing functionality for regular columns, non-foreign key columns, and unambiguous relationships.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_model.j2`

**Specific Changes**:

1. **Fix Primary Key Parameter for Foreign Keys**: In the foreign key branch (around line 52-72), add logic to include `primary_key=True` in param_list when `col.is_pk` is true
   - Check `col.is_pk` and append `'primary_key=True'` to param_list
   - Add `'autoincrement=True'` when primary key is present

2. **Fix Foreign Key Field Naming**: In the foreign key column generation (line 72), use `col.db_column` if it exists, otherwise fall back to `col.name`
   - Change `{{ col.name }}` to `{{ col.db_column if col.db_column else col.name }}`

3. **Fix Foreign Key Type Mapping**: Replace hardcoded `Integer` type with dynamic type from TOML specification
   - Use `sqlalchemy_column_type` filter to get correct type: `{% set column_type, params = col | sqlalchemy_column_type %}`
   - Replace `Integer` with `{{ column_type }}`

4. **Fix Nullable Parameter**: Add logic to include `nullable=True` when `col.nullable` is true
   - Change condition from `if not col.nullable` to handle both true and false cases
   - Add `'nullable=True'` to param_list when `col.nullable` is true

5. **Fix Reverse Relationship foreign_keys Parameter**: In relationship generation (lines 127-149), add `foreign_keys` parameter for reverse relationships
   - Identify the foreign key column name from the relationship definition
   - Add `foreign_keys=[{{ fk_column_name }}]` to relationship() calls for reverse relationships (right entity side)

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Generate SQLAlchemy models from the TOML specification in `examples/bug/django/models.toml` using the UNFIXED template. Compare the output with `examples/bug/django/sqlalchemy_error_models.py` to confirm the bug exists, then compare with `examples/bug/django/sqlalchemy_right_models.py` to understand the expected correct output.

**Test Cases**:
1. **Primary Key Test**: Generate Translation model and verify `id` column is missing `primary_key=True` (will fail on unfixed code)
2. **Foreign Key Naming Test**: Generate Translation model and verify `code` is used instead of `code_id` (will fail on unfixed code)
3. **Foreign Key Type Test**: Generate Translation model and verify `Integer` is used instead of `BigInteger` (will fail on unfixed code)
4. **Nullable Foreign Key Test**: Generate Translation model and verify `nullable=True` is missing (will fail on unfixed code)
5. **Reverse Relationship Test**: Generate Translation model and verify `foreign_keys` parameter is missing (will fail on unfixed code)

**Expected Counterexamples**:
- Primary key columns generate without `primary_key=True` parameter
- Foreign key columns use relationship name instead of db_column value
- Foreign key columns use `Integer` instead of `BigInteger`
- Nullable foreign keys don't include `nullable=True`
- Reverse relationships don't include `foreign_keys` parameter
- Possible causes: missing template logic, incorrect field name usage, hardcoded types, incomplete parameter generation

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed template produces the expected behavior.

**Pseudocode:**
```
FOR ALL column WHERE isBugCondition(column) DO
  result := generateSQLAlchemyColumn_fixed(column)
  ASSERT expectedBehavior(result)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed template produces the same result as the original template.

**Pseudocode:**
```
FOR ALL column WHERE NOT isBugCondition(column) DO
  ASSERT generateSQLAlchemyColumn_original(column) = generateSQLAlchemyColumn_fixed(column)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Generate models from various TOML specifications on UNFIXED code first to capture baseline behavior, then write property-based tests capturing that behavior and verify it remains unchanged after the fix.

**Test Cases**:
1. **Regular Column Preservation**: Observe that regular string, text, integer columns generate correctly on unfixed code, then verify this continues after fix
2. **Non-FK Column Preservation**: Observe that columns without foreign keys use correct field names on unfixed code, then verify this continues after fix
3. **Type Mapping Preservation**: Observe that non-FK columns map types correctly on unfixed code, then verify this continues after fix
4. **Forward Relationship Preservation**: Observe that forward relationships (left entity side) generate correctly on unfixed code, then verify this continues after fix

### Unit Tests

- Test primary key column generation with `primary_key=True` parameter
- Test foreign key column generation with correct field name from db_column
- Test foreign key column generation with correct type (BigInteger for bigint)
- Test nullable foreign key column generation with `nullable=True` parameter
- Test reverse relationship generation with `foreign_keys` parameter
- Test edge cases (primary key foreign keys, multiple foreign keys to same table)

### Property-Based Tests

- Generate random TOML specifications with various column types and verify correct SQLAlchemy output
- Generate random foreign key configurations and verify correct field naming and types
- Generate random relationship configurations and verify correct foreign_keys parameters
- Test that all non-buggy columns continue to generate correctly across many scenarios

### Integration Tests

- Test full model generation from TOML to SQLAlchemy for the Translation example
- Test that generated models can be imported and used with SQLAlchemy
- Test that generated models correctly define relationships without ambiguity errors
- Test that the fix works across different entity configurations (with/without templates, with/without table prefixes)
