# Implementation Plan: Django-Style Foreign Key Relationships

## Overview

This implementation plan transforms the SQLAlchemy model generator to support Django-style foreign key naming conventions. The approach focuses on modifying Jinja2 templates and enhancing the TOML parser to correctly detect and name foreign key columns and relationship objects. Implementation follows an incremental approach: first establishing the core naming logic, then adding validation, and finally ensuring comprehensive test coverage.

## Tasks

- [x] 1. Set up test infrastructure and fixtures
  - Create test fixture TOML files with Django-style foreign key examples
  - Set up test data including the Translation/I18nCode example from requirements
  - Create fixtures for multiple foreign keys, self-referential FKs, and table prefixes
  - _Requirements: All requirements (foundation for testing)_

- [ ] 2. Enhance TOML parser for foreign key detection
  - [x] 2.1 Update foreign key detection logic in converters/toml_parser.py
    - Modify FK detection to match against both `col.name` and `col.db_column`
    - Implement implicit `db_column` inference (append `_id` to `name` if not specified)
    - Ensure all foreign key columns have `is_fk=True` flag set correctly
    - _Requirements: 3.2, 4.1, 8.4_
  
  - [x] 2.2 Write property test for foreign key detection
    - **Property 8: Foreign Key Detection from Relationships**
    - **Validates: Requirements 3.2**
  
  - [x] 2.3 Write unit tests for parser FK detection
    - Test explicit db_column with _id suffix
    - Test implicit db_column inference
    - Test matching against relationship right_column
    - _Requirements: 3.2, 4.1_

- [ ] 3. Implement Django-style naming in templates
  - [x] 3.1 Modify sqlalchemy_model.j2 template
    - Update column definition to use `col.db_column` for foreign key columns
    - Update relationship definition to use `col.name` (without _id suffix)
    - Add `foreign_keys=[{col.db_column}]` parameter to relationship objects
    - Ensure ForeignKey constraint uses correct table.column format
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.2, 5.4_
  
  - [x] 3.2 Modify sqlalchemy_single_model.j2 template
    - Apply same changes as sqlalchemy_model.j2 for consistency
    - Ensure both templates generate identical output for same input
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.2, 5.4_
  
  - [x] 3.3 Write property test for Django-style naming
    - **Property 1: Django-Style Naming Convention**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
  
  - [x] 3.4 Write unit tests for template rendering
    - Test basic Django-style naming (Translation/I18nCode example)
    - Test that column uses db_column and relationship uses name
    - Test foreign_keys parameter is included
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 4. Checkpoint - Ensure core naming logic works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement foreign key constraint generation
  - [x] 5.1 Add ForeignKey constraint logic to templates
    - Generate ForeignKey references in format `table_name.column_name`
    - Implement table prefix support: `{prefix}_{table_name}.column_name`
    - Ensure constraint references correct target entity's primary key
    - _Requirements: 2.2, 3.3, 5.4, 7.1, 7.2, 7.3_
  
  - [x] 5.2 Implement foreign key type matching
    - Ensure FK column type matches referenced primary key type
    - Handle BigInteger, Integer, String, and other common types
    - _Requirements: 5.3_
  
  - [x] 5.3 Write property test for FK constraint correctness
    - **Property 3: Foreign Key Constraint Correctness**
    - **Validates: Requirements 2.2, 3.3, 5.4, 7.1, 7.2, 7.3**
  
  - [x] 5.4 Write property test for FK type matching
    - **Property 4: Foreign Key Type Matching**
    - **Validates: Requirements 5.3**
  
  - [x] 5.5 Write unit tests for FK constraints
    - Test ForeignKey format without table prefix
    - Test ForeignKey format with table prefix
    - Test type matching for various column types
    - _Requirements: 2.2, 5.3, 5.4, 7.1, 7.2, 7.3_

- [x] 6. Implement column attribute preservation
  - [x] 6.1 Ensure FK columns preserve all attributes
    - Preserve nullable, unique, indexed, default, comment attributes
    - Ensure attributes are rendered correctly in Column definition
    - Test that ForeignKey constraint doesn't override other attributes
    - _Requirements: 2.3_
  
  - [x] 6.2 Write property test for attribute preservation
    - **Property 2: Foreign Key Column Attributes Preservation**
    - **Validates: Requirements 2.3**
  
  - [x] 6.3 Write unit tests for attribute preservation
    - Test nullable foreign keys
    - Test unique foreign keys
    - Test foreign keys with defaults and comments
    - _Requirements: 2.3_

- [x] 7. Implement bidirectional relationship configuration
  - [x] 7.1 Add back_populates logic to templates
    - Generate correct back_populates parameter for both sides of relationship
    - Implement uselist parameter based on relationship type
    - Handle one-to-one (uselist=False) and one-to-many (uselist=True)
    - _Requirements: 3.1, 3.4, 5.2_
  
  - [x] 7.2 Write property test for bidirectional relationships
    - **Property 5: Bidirectional Relationship Configuration**
    - **Validates: Requirements 3.1, 3.4, 5.2**
  
  - [x] 7.3 Write unit tests for relationship configuration
    - Test one-to-one relationships with correct uselist
    - Test one-to-many relationships with correct back_populates
    - Test that both entities have matching relationship objects
    - _Requirements: 3.1, 3.4, 5.2_

- [ ] 8. Checkpoint - Ensure relationship logic works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement multiple foreign keys support
  - [x] 9.1 Handle entities with multiple foreign keys
    - Ensure each FK column has unique name
    - Ensure each relationship object has unique name
    - Ensure each relationship references correct FK column
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 9.2 Write property test for multiple foreign keys
    - **Property 6: Multiple Foreign Keys Handling**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
  
  - [x] 9.3 Write unit tests for multiple foreign keys
    - Test entity with 2 foreign keys to different entities
    - Test entity with 3+ foreign keys
    - Test self-referential foreign keys
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 10. Implement table prefix consistency
  - [x] 10.1 Add table prefix handling to FK constraints
    - Apply table prefix to all ForeignKey references
    - Ensure consistency across all relationships in model
    - Handle cases with and without prefix configuration
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 10.2 Write property test for table prefix consistency
    - **Property 9: Table Prefix Consistency**
    - **Validates: Requirements 7.4**
  
  - [x] 10.3 Write unit tests for table prefixes
    - Test FK references with table prefix
    - Test FK references without table prefix
    - Test mixed scenarios in same model
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 11. Implement validation and error handling
  - [x] 11.1 Add validation logic to ERModel or parser
    - Validate that FK columns have matching relationships
    - Validate that relationships reference existing entities
    - Validate that relationships reference existing columns
    - Generate descriptive error messages for each validation failure
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 11.2 Add warning for missing _id suffix
    - Check if FK db_column ends with _id
    - Generate warning message if suffix is missing
    - Allow generation to continue (warning, not error)
    - _Requirements: 8.3_
  
  - [x] 11.3 Write property test for column validation
    - **Property 10: Relationship Column Validation**
    - **Validates: Requirements 8.4**
  
  - [x] 11.4 Write unit tests for validation
    - Test error for FK without matching relationship
    - Test error for relationship with non-existent entity
    - Test error for relationship with non-existent column
    - Test warning for FK without _id suffix
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 12. Implement implicit db_column inference
  - [x] 12.1 Add db_column inference logic
    - Check if db_column is specified for FK columns
    - If not specified, set db_column to `{name}_id`
    - Ensure inference happens before template rendering
    - _Requirements: 4.1_
  
  - [x] 12.2 Write property test for db_column inference
    - **Property 7: Implicit db_column Inference**
    - **Validates: Requirements 4.1**
  
  - [x] 12.3 Write unit tests for db_column inference
    - Test FK column without explicit db_column
    - Test FK column with explicit db_column (should not override)
    - Test backward compatibility with existing TOML files
    - _Requirements: 4.1_

- [ ] 13. Checkpoint - Ensure validation and inference work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Integration testing and backward compatibility
  - [x] 14.1 Write integration tests for end-to-end generation
    - Test TOML → ERModel → SQLAlchemy code pipeline
    - Test that generated code is valid Python
    - Test that generated models can be imported
    - Test that SQLAlchemy validates generated models
    - _Requirements: All requirements (integration validation)_
  
  - [x] 14.2 Write backward compatibility tests
    - Test existing TOML files without db_column specification
    - Test existing templates and mixins continue to work
    - Test that old naming convention is preserved when explicitly used
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 14.3 Write tests for complex scenarios
    - Test combination of multiple FKs, table prefixes, and attributes
    - Test self-referential FKs with Django-style naming
    - Test many-to-many relationships (if applicable)
    - _Requirements: Multiple requirements combined_

- [x] 15. Documentation and examples
  - [x] 15.1 Update example TOML files
    - Add Django-style FK examples to examples directory
    - Update existing examples to demonstrate new naming convention
    - Create examples showing migration from old to new style
    - _Requirements: All requirements (documentation)_
  
  - [x] 15.2 Update code comments and docstrings
    - Document template variables and their usage
    - Document parser FK detection logic
    - Add inline comments explaining Django-style naming
    - _Requirements: All requirements (code documentation)_

- [ ] 16. Final checkpoint - Comprehensive validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at logical breakpoints
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: parser → templates → validation → integration
- Python is used throughout as SQLAlchemy is a Python library
- Hypothesis library is used for property-based testing with minimum 100 iterations per test
