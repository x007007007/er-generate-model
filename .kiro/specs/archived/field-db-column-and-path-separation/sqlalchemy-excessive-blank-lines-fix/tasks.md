# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Fault Condition** - SQLAlchemy 模板空行控制缺陷
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility
  - Test that template rendering produces excessive blank lines in multiple locations:
    - Import block: 7 blank lines between `from sqlalchemy.orm import relationship` and base model import (expected: 1)
    - External imports: 6 blank lines between last import and class definition (expected: 2)
    - Field definitions: 3 blank lines between consecutive fields (expected: 0)
    - Relationship definitions: 3 blank lines between consecutive relationships (expected: 0)
    - Field-to-relationship transition: 2 blank lines (expected: 1)
  - Test implementation details from Fault Condition in design (isBugCondition pseudocode)
  - The test assertions should match the Expected Behavior Properties from design (Property 1)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - 模板功能保持不变
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (semantic correctness of generated code)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements:
    - `__tablename__` attribute rendering (no blank line after class declaration)
    - First field definition spacing (1 blank line after `__tablename__`)
    - Inheritance mode handling (flatten/reference field inclusion/exclusion logic)
    - Foreign key constraints and types generation
    - Relationship back_populates and foreign_keys parameters
    - Django-style naming strategy (logical names vs db_column)
    - Different relationship types configuration (one-to-one, one-to-many, many-to-many)
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [ ] 3. Fix for SQLAlchemy 模板空行控制

  - [-] 3.1 Implement the fix in sqlalchemy_single_model.j2
    - Analyze template file to identify exact locations where blank line control is needed
    - Add or adjust Jinja2 whitespace control markers (`{%-`, `-%}`) at key positions:
      - Import block transitions (ensure 1 blank line between import groups)
      - Import-to-class transition (ensure 2 blank lines per PEP 8)
      - Field definition loops (ensure 0 blank lines between fields)
      - Relationship definition loops (ensure 0 blank lines between relationships)
      - Field-to-relationship transition (ensure 1 blank line)
    - Verify all existing whitespace control markers are correctly placed
    - Test changes incrementally to avoid breaking template logic
    - _Bug_Condition: isBugCondition(template_content) where template lacks proper whitespace control markers_
    - _Expected_Behavior: correctBlankLineCount(result) from design - import blocks: 1 line, import-to-class: 2 lines, fields: 0 lines, relationships: 0 lines, field-to-relationship: 1 line_
    - _Preservation: All template functionality from Preservation Requirements - tablename rendering, field logic, inheritance modes, FK constraints, relationship config, Django naming, relationship types_
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [~] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - SQLAlchemy 模板空行控制正确性
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [~] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - 模板功能保持不变
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [~] 4. Checkpoint - Ensure all tests pass
  - Run all tests (exploration + preservation) to verify complete fix
  - Verify generated code passes PEP 8 validation (optional: run flake8 or black)
  - Ensure no regressions in existing functionality
  - Ask the user if questions arise
