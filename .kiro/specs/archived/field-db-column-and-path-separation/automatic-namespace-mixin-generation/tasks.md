# Implementation Plan: Automatic Namespace-Based Mixin Generation

## Overview

Implement automatic generation of SQLAlchemy mixin classes from TOML templates with namespace transformation. The system will discover templates across multiple TOML files, transform Django package namespaces to SQLAlchemy equivalents, generate mixin files, and enable entities to reference these mixins.

## Tasks

- [x] 1. Implement namespace transformation component
  - [x] 1.1 Create NamespaceTransformer class in new module `packages/er-gen-core/src/x007007007/er/namespace.py`
    - Implement `transform_package_to_export_path()` method
    - Handle idempotent transformation (already transformed packages)
    - Validate package paths and components
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 1.2 Write property test for namespace transformation
    - **Property 1: Namespace Transformation Idempotence**
    - **Property 2: Namespace Transformation Suffix Application**
    - **Validates: Requirements 1.2, 1.3, 1.1, 1.4**
  
  - [x] 1.3 Write unit tests for NamespaceTransformer
    - Test simple package transformation
    - Test already-transformed packages
    - Test single-component packages
    - Test invalid package paths
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement template registry component
  - [x] 2.1 Create TemplateInfo dataclass in `packages/er-gen-core/src/x007007007/er/models.py`
    - Add fields: name, package, export_path, columns, source_file
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 2.2 Create TemplateRegistry class in new module `packages/er-gen-core/src/x007007007/er/template_registry.py`
    - Implement `discover_templates()` method to scan multiple TOML files
    - Implement `resolve_template()` method for template lookup
    - Auto-derive export_path from package using NamespaceTransformer
    - Handle explicit export_path precedence
    - Detect and report duplicate template names
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.3, 3.4, 7.1, 7.2, 7.4, 7.5, 8.1, 8.2_
  
  - [x] 2.3 Write property tests for template registry
    - **Property 3: Template Discovery Completeness**
    - **Property 4: Export Path Auto-Derivation**
    - **Property 5: Export Path Precedence**
    - **Property 6: Template Resolution Across Files**
    - **Property 7: Registry Completeness Invariant**
    - **Validates: Requirements 2.1, 2.2, 2.3, 3.1, 8.1, 3.3, 3.4**
  
  - [x] 2.4 Write unit tests for TemplateRegistry
    - Test single file template discovery
    - Test multiple file template discovery
    - Test duplicate template detection
    - Test auto-derivation of export_path
    - Test explicit export_path precedence
    - Test template resolution by name
    - Test validation errors
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 7.1, 7.2, 7.4, 7.5_

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement mixin generator component
  - [x] 4.1 Create MixinGenerator class in new module `packages/er-gen-core/src/x007007007/er/mixin_generator.py`
    - Implement `generate_mixin_file()` method
    - Convert export_path to file path (dots to slashes)
    - Convert class name to snake_case for filename
    - Create directory structure
    - Generate Python code with SQLAlchemy columns
    - Mark class as abstract with `__abstract__ = True`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3, 6.4, 9.1, 9.2_
  
  - [x] 4.2 Create Jinja2 template for mixin class generation
    - Create template file `packages/er-gen-core/src/x007007007/er/templates/sqlalchemy_mixin.j2`
    - Include SQLAlchemy imports
    - Generate abstract base class
    - Generate column definitions
    - _Requirements: 4.2, 4.3, 9.1, 9.2_
  
  - [x] 4.3 Write property tests for mixin generator
    - **Property 8: Mixin File Path Construction**
    - **Property 9: Mixin Abstract Class Generation**
    - **Property 10: Mixin Column Completeness**
    - **Property 11: Directory Structure Creation**
    - **Property 20: Generated Code Syntactic Validity**
    - **Property 21: SQLAlchemy Import Presence**
    - **Validates: Requirements 4.1, 6.1, 6.2, 6.3, 4.2, 4.3, 4.4, 6.4, 9.1, 9.2**
  
  - [x] 4.4 Write unit tests for MixinGenerator
    - Test file path construction
    - Test directory creation
    - Test mixin class generation
    - Test abstract attribute presence
    - Test column completeness
    - Test invalid paths
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3, 6.4_

- [x] 5. Enhance entity renderer for mixin inheritance
  - [x] 5.1 Update SQLAlchemy renderer in `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/renderer.py`
    - Add support for reference mode: generate imports for mixins
    - Add support for reference mode: include mixins in class inheritance
    - Add support for flatten mode: expand mixin fields inline
    - Preserve field order (template fields first, then entity fields)
    - Use TemplateRegistry to resolve template references
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.3, 9.4, 9.5_
  
  - [x] 5.2 Update SQLAlchemy templates to support mixin inheritance
    - Modify `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/templates/sqlalchemy_model.j2`
    - Add mixin import generation
    - Add mixin inheritance syntax
    - _Requirements: 5.1, 5.2, 9.4, 9.5_
  
  - [x] 5.3 Write property tests for entity rendering with mixins
    - **Property 12: Reference Mode Import Generation**
    - **Property 13: Reference Mode Inheritance**
    - **Property 14: Flatten Mode Field Expansion**
    - **Property 15: Field Order Preservation**
    - **Property 19: Cross-File Import Path Correctness**
    - **Property 22: Entity Import Statement Validity**
    - **Property 23: Entity Inheritance Syntax Validity**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 8.3, 9.4, 9.5**
  
  - [x] 5.4 Write unit tests for entity renderer enhancements
    - Test reference mode import generation
    - Test reference mode inheritance
    - Test flatten mode field expansion
    - Test field order preservation
    - Test cross-file template references
    - Test missing template error handling
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.3_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Integrate components and update parser
  - [x] 7.1 Update TOML parser in `packages/er-gen-core/src/x007007007/er/parser/toml_parser.py`
    - Parse template definitions from TOML files
    - Store templates in ERModel.templates
    - Support both package and export_path fields
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 7.2 Create orchestration module `packages/er-gen-core/src/x007007007/er/mixin_orchestrator.py`
    - Coordinate template discovery across multiple files
    - Trigger mixin file generation for all templates
    - Provide templates to entity renderer
    - Handle inheritance mode selection (reference vs flatten)
    - _Requirements: 3.1, 8.1, 8.4, 8.5_
  
  - [x] 7.3 Write integration tests for end-to-end workflow
    - Test complete workflow: TOML parsing → template discovery → mixin generation → entity rendering
    - Test multiple TOML files with cross-file references
    - Test both reference and flatten modes
    - Test generated code validity
    - _Requirements: All requirements_

- [x] 8. Add error handling and validation
  - [x] 8.1 Implement error classes in new module `packages/er-gen-core/src/x007007007/er/exceptions.py`
    - ConflictError for duplicate templates
    - TemplateNotFoundError for missing templates
    - ValidationError for invalid configurations
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 8.2 Add comprehensive error reporting
    - Update TemplateRegistry with detailed error messages
    - Update MixinGenerator with path and reason reporting
    - Update NamespaceTransformer with component validation
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 8.3 Write unit tests for error handling
    - Test duplicate template error reporting
    - Test missing template error reporting
    - Test invalid package path error reporting
    - Test file generation failure reporting
    - Test TOML parsing error reporting
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 9. Final integration and wiring
  - [x] 9.1 Update main CLI or API entry points to use new components
    - Wire TemplateRegistry into generation pipeline
    - Wire MixinGenerator into generation pipeline
    - Add command-line options for inheritance mode
    - _Requirements: All requirements_
  
  - [x] 9.2 Update documentation and examples
    - Add example TOML files with templates
    - Document template syntax and usage
    - Document namespace transformation rules
    - _Requirements: All requirements_
  
  - [x] 9.3 Write integration tests for complete system
    - Test end-to-end generation with real TOML files
    - Verify generated code can be imported and used
    - Test both single-file and multi-file scenarios
    - _Requirements: All requirements_

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design
- Unit tests validate specific examples and edge cases
- The implementation follows the existing project structure in `packages/er-gen-core`
