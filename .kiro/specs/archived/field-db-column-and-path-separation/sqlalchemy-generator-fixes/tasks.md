# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - SQLAlchemy Generator Produces Incorrect Code
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Test the concrete failing cases from the bug examples
  - Test implementation details from Fault Condition in design:
    - Generate SQLAlchemy models from `examples/bug/django/models.toml` using UNFIXED template
    - Assert primary key columns include `primary_key=True` parameter
    - Assert foreign key columns use `db_column` field name (e.g., `code_id`) instead of relationship name (e.g., `code`)
    - Assert foreign key columns use correct type from TOML (e.g., `BigInteger` for `bigint`)
    - Assert nullable foreign key columns include `nullable=True` parameter
    - Assert reverse relationships include `foreign_keys` parameter
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found:
    - Primary key columns missing `primary_key=True`
    - Foreign key columns using wrong field names
    - Foreign key columns using `Integer` instead of `BigInteger`
    - Nullable foreign keys missing `nullable=True`
    - Reverse relationships missing `foreign_keys` parameter
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Buggy Column and Relationship Generation
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs:
    - Regular columns (string, text, integer, boolean, date, datetime) without primary_key or foreign_key
    - Columns without `primary_key=true` in TOML
    - Columns without `is_fk=true`
    - Forward relationships (left entity side)
    - Table names, imports, and other model attributes
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements:
    - Test that non-primary key columns don't include `primary_key=True`
    - Test that non-foreign key columns use correct field names from TOML
    - Test that type mapping for non-FK columns remains correct
    - Test that forward relationships generate valid definitions
    - Test that table names and imports generate correctly
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix SQLAlchemy generator template issues

  - [x] 3.1 Fix primary key parameter for foreign keys
    - Open `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_model.j2`
    - Locate the foreign key branch (around lines 52-72)
    - Add logic to check `col.is_pk` and append `'primary_key=True'` to param_list
    - Add `'autoincrement=True'` when primary key is present
    - _Bug_Condition: isBugCondition(input) where input.is_pk = true_
    - _Expected_Behavior: Generated Column includes primary_key=True parameter_
    - _Preservation: Non-primary key columns continue without primary_key=True_
    - _Requirements: 1.1, 2.1, 3.1_

  - [x] 3.2 Fix foreign key field naming
    - In the same template file, locate foreign key column generation (line 72)
    - Change `{{ col.name }}` to `{{ col.db_column if col.db_column else col.name }}`
    - This uses db_column when available, otherwise falls back to name
    - _Bug_Condition: isBugCondition(input) where input.is_fk = true AND input.db_column IS NOT NULL_
    - _Expected_Behavior: Generated Column uses db_column field name_
    - _Preservation: Non-FK columns continue to use correct field names_
    - _Requirements: 1.2, 2.2, 3.2_

  - [x] 3.3 Fix foreign key type mapping
    - Replace hardcoded `Integer` type with dynamic type from TOML
    - Use `sqlalchemy_column_type` filter: `{% set column_type, params = col | sqlalchemy_column_type %}`
    - Replace `Integer` with `{{ column_type }}`
    - _Bug_Condition: isBugCondition(input) where input.is_fk = true AND input.type = "bigint"_
    - _Expected_Behavior: Generated Column uses correct type from TOML (e.g., BigInteger)_
    - _Preservation: Type mapping for non-FK columns remains unchanged_
    - _Requirements: 1.3, 2.3, 3.3_

  - [x] 3.4 Fix nullable parameter for foreign keys
    - Add logic to include `nullable=True` when `col.nullable` is true
    - Change condition from `if not col.nullable` to handle both true and false cases
    - Add `'nullable=True'` to param_list when `col.nullable` is true
    - _Bug_Condition: isBugCondition(input) where input.is_fk = true AND input.nullable = true_
    - _Expected_Behavior: Generated Column includes nullable=True parameter_
    - _Preservation: Non-nullable columns continue to work correctly_
    - _Requirements: 1.5, 2.5_

  - [x] 3.5 Fix reverse relationship foreign_keys parameter
    - Locate relationship generation section (lines 127-149)
    - Identify the foreign key column name from the relationship definition
    - Add `foreign_keys=[{{ fk_column_name }}]` to relationship() calls for reverse relationships (right entity side)
    - _Bug_Condition: isBugCondition(input) where input.is_reverse_relationship = true_
    - _Expected_Behavior: Generated relationship() includes foreign_keys parameter_
    - _Preservation: Relationships without ambiguous FKs continue to work_
    - _Requirements: 1.4, 2.4, 3.4_

  - [x] 3.6 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - SQLAlchemy Generator Produces Correct Code
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify all 5 issues are resolved:
      - Primary key columns include `primary_key=True`
      - Foreign key columns use correct field names from db_column
      - Foreign key columns use correct types from TOML
      - Nullable foreign keys include `nullable=True`
      - Reverse relationships include `foreign_keys` parameter
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.7 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Buggy Column and Relationship Generation
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all preservation requirements are met:
      - Non-primary key columns work correctly
      - Non-FK columns use correct field names
      - Type mapping for non-FK columns unchanged
      - Forward relationships generate correctly
      - Table names and imports work correctly
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Add unit tests for specific scenarios

  - [x] 4.1 Test primary key column generation
    - Create unit test for column with `primary_key=True` parameter
    - Verify generated code includes `primary_key=True` and `autoincrement=True`
    - Test edge case: primary key foreign key (both is_pk and is_fk true)

  - [x] 4.2 Test foreign key field naming
    - Create unit test for FK column with db_column attribute
    - Verify generated code uses db_column value instead of name
    - Test edge case: FK without db_column (should use name)

  - [x] 4.3 Test foreign key type mapping
    - Create unit test for FK column with bigint type
    - Verify generated code uses BigInteger instead of Integer
    - Test other FK types (string, datetime, etc.)

  - [x] 4.4 Test nullable foreign key generation
    - Create unit test for FK column with nullable=true
    - Verify generated code includes `nullable=True` parameter
    - Test edge case: non-nullable FK (should include `nullable=False`)

  - [x] 4.5 Test reverse relationship foreign_keys parameter
    - Create unit test for reverse relationship
    - Verify generated code includes `foreign_keys=[column_name]`
    - Test edge case: multiple FKs to same table

- [x] 5. Add integration tests

  - [x] 5.1 Test full Translation model generation
    - Generate complete Translation model from `examples/bug/django/models.toml`
    - Compare output with `examples/bug/django/sqlalchemy_right_models.py`
    - Verify all 5 issues are fixed in the generated model

  - [x] 5.2 Test generated models can be imported
    - Import generated SQLAlchemy models
    - Verify no import errors or syntax errors
    - Verify SQLAlchemy can parse the model definitions

  - [x] 5.3 Test generated models work with SQLAlchemy
    - Create in-memory SQLite database
    - Use generated models to create tables
    - Verify relationships work without ambiguity errors
    - Test basic CRUD operations

  - [x] 5.4 Test fix works across different configurations
    - Test with entities that have templates
    - Test with entities that have table prefixes
    - Test with entities that have multiple foreign keys
    - Test with entities that have self-referential relationships

- [x] 6. Checkpoint - Ensure all tests pass
  - Run all unit tests and verify they pass
  - Run all integration tests and verify they pass
  - Run preservation tests and verify no regressions
  - Verify generated models match expected output in `examples/bug/django/sqlalchemy_right_models.py`
  - If any issues arise, document them and ask the user for guidance
