# Implementation Tasks / 实施任务

## Phase 0: Package Restructuring / 包重构

- [x] 0. Create New Package Structure / 创建新包结构
  - [x] 0.1 Create `src/x007007007/er/renderers/` package directory
  - [x] 0.2 Create `src/x007007007/er/renderers/base.py` with Renderer base class
  - [x] 0.3 Create `src/x007007007/er/renderers/python/` package directory
  - [x] 0.4 Create `src/x007007007/er/renderers/python/base.py` with PythonRenderer
  - [x] 0.5 Create `src/x007007007/er/renderers/python/django/` package directory
  - [x] 0.6 Create `src/x007007007/er/renderers/python/django/templates/` directory
  - [x] 0.7 Create `src/x007007007/er/renderers/python/sqlalchemy/` package directory
  - [x] 0.8 Create `src/x007007007/er/renderers/python/sqlalchemy/templates/` directory
  - [x] 0.9 Create all necessary `__init__.py` files with proper exports
  - [x] 0.10 Set up backward-compatible imports in `renderers/__init__.py`

## Phase 1: Core Infrastructure / 核心基础设施

- [x] 1. Implement Base Renderer / 实现基础渲染器
  - [x] 1.1 Implement `Renderer` base class in `renderers/base.py`
  - [x] 1.2 Add `render` abstract method
  - [x] 1.3 Add `serialize_value` abstract method with documentation
  - [x] 1.4 Write unit tests for base class structure

- [x] 2. Implement PythonRenderer Base Class / 实现 PythonRenderer 基类
  - [x] 2.1 Implement `PythonRenderer` class in `renderers/python/base.py`
  - [x] 2.2 Implement `serialize_value` method with support for None, bool, int, float, str, list, dict
  - [x] 2.3 Implement `_serialize_string` method with smart quote selection logic
  - [x] 2.4 Implement `_setup_jinja_env` method with whitespace control settings
  - [x] 2.5 Add proper error handling for unsupported types
  - [x] 2.6 Write unit tests for `serialize_value` covering all data types
  - [x] 2.7 Write unit tests for `_serialize_string` covering all quote scenarios
  - [x] 2.8 Write unit tests for `_setup_jinja_env` verifying whitespace settings
  - [x] 2.9 Write property-based test for Property 1: Serialization Round Trip
  - [x] 2.10 Write property-based test for Property 2: Smart Quote Selection
  - [x] 2.11 Write property-based test for Property 3: Escape Sequence Preservation
  - [x] 2.12 Write property-based test for Property 4: Nested Structure Serialization
  - [x] 2.13 Write property-based test for Property 15: No Extra Blank Lines
  - [x] 2.14 Write property-based test for Property 16: Correct Python Indentation

## Phase 2: Django Renderer Implementation / Django 渲染器实现

- [x] 3. Move and Update Django Templates / 移动和更新 Django 模板
  - [x] 3.1 Move `django_model.j2` to `renderers/python/django/templates/`
  - [x] 3.2 Move `django_model_single.j2` to `renderers/python/django/templates/`
  - [x] 3.3 Move `django_init.j2` to `renderers/python/django/templates/`
  - [x] 3.4 Update all Django templates to use `code_value` filter for default values
  - [x] 3.5 Update all Django templates to use `code_value` filter for help_text
  - [x] 3.6 Update template loader paths in renderer code

- [x] 4. Create New Django Templates for Three-File Structure / 创建三文件结构的新 Django 模板
  - [x] 4.1 Create `django_queryset_only.j2` template for QuerySet class
  - [x] 4.2 Create `django_manager_only.j2` template for Manager class
  - [x] 4.3 Create `django_model_only.j2` template for Model class with imports
  - [x] 4.4 Update `django_init.j2` template to import from `_model.py` files
  - [x] 4.5 Add `code_value` filter usage to all new templates

- [x] 5. Implement Django Renderers / 实现 Django 渲染器
  - [x] 5.1 Create `renderers/python/django/renderer.py`
  - [x] 5.2 Implement `DjangoRenderer` class inheriting from `PythonRenderer`
  - [x] 5.3 Implement `DjangoPackageRenderer` class inheriting from `PythonRenderer`
  - [x] 5.4 Implement three-file generation logic in `DjangoPackageRenderer`
  - [x] 5.5 Implement proper file naming with snake_case convention
  - [x] 5.6 Ensure correct imports between files (Model → Manager → QuerySet)
  - [x] 5.7 Move `to_snake_case` helper function to Django renderer module
  - [x] 5.8 Register `code_value` filter in both renderers
  - [x] 5.9 Write unit tests for `DjangoRenderer`
  - [x] 5.10 Write unit tests for `DjangoPackageRenderer`
  - [x] 5.11 Write unit tests for three-file generation
  - [x] 5.12 Write unit tests for file naming convention
  - [x] 5.13 Write property-based test for Property 5: Django Template Integration
  - [x] 5.14 Write property-based test for Property 7: Generated Code Validity (Django)
  - [x] 5.15 Write property-based test for Property 9: Three-File Structure Generation
  - [x] 5.16 Write property-based test for Property 10: File Naming Convention
  - [x] 5.17 Write property-based test for Property 11: Import Correctness
  - [x] 5.18 Write property-based test for Property 12: Generated Package Validity

## Phase 3: SQLAlchemy Renderer Implementation / SQLAlchemy 渲染器实现

- [x] 6. Move and Update SQLAlchemy Templates / 移动和更新 SQLAlchemy 模板
  - [x] 6.1 Move `sqlalchemy_model.j2` to `renderers/python/sqlalchemy/templates/`
  - [x] 6.2 Update SQLAlchemy template to use `code_value` filter for default values
  - [x] 6.3 Update SQLAlchemy template to use `code_value` filter for comments
  - [x] 6.4 Update template loader path in renderer code

- [x] 7. Implement SQLAlchemy Renderer / 实现 SQLAlchemy 渲染器
  - [x] 7.1 Create `renderers/python/sqlalchemy/renderer.py`
  - [x] 7.2 Implement `SQLAlchemyRenderer` class inheriting from `PythonRenderer`
  - [x] 7.3 Register `code_value` filter in renderer
  - [x] 7.4 Write unit tests for `SQLAlchemyRenderer`
  - [x] 7.5 Write property-based test for Property 6: SQLAlchemy Template Integration
  - [x] 7.6 Write property-based test for Property 7: Generated Code Validity (SQLAlchemy)

## Phase 4: CLI and Import Updates / CLI 和导入更新

- [x] 8. Update CLI and Imports / 更新 CLI 和导入
  - [x] 8.1 Update imports in `cli.py` to use new package structure
  - [x] 8.2 Change `--input-type` default from 'mermaid' to 'toml' in `cli.py`
  - [x] 8.3 Update CLI help text to reflect new default
  - [x] 8.4 Update imports in `converters.py` if needed
  - [x] 8.5 Update imports in any other modules that use renderers
  - [x] 8.6 Write unit tests for CLI default behavior
  - [x] 8.7 Write unit tests for explicit --input-type mermaid (backward compatibility)
  - [x] 8.8 Write property-based test for Property 8: Filter Registration

## Phase 5: Deprecate Old Structure (Optional) / 弃用旧结构（可选）

- [x] 9. Handle Old renderers.py File / 处理旧的 renderers.py 文件
  - [x] 9.1 Add deprecation warning to old `renderers.py` (optional)
  - [x] 9.2 Keep old file for backward compatibility or remove after migration
  - [x] 9.3 Update any external documentation referencing old import paths

## Phase 6: Documentation / 文档

- [x] 10. Update README / 更新 README
  - [x] 10.1 Update basic usage examples to show TOML as primary format
  - [x] 10.2 Update command-line options section to show 'toml' as default
  - [x] 10.3 Add section explaining three-file structure for Django package mode
  - [x] 10.4 Add examples of generated three-file structure
  - [x] 10.5 Update feature list to mention smart quote selection and code serialization
  - [x] 10.6 Update package structure documentation to reflect new organization

- [x] 11. Update CHANGELOG / 更新 CHANGELOG
  - [x] 11.1 Add entry for package restructuring
  - [x] 11.2 Add entry for TOML default change
  - [x] 11.3 Add entry for code serializer feature
  - [x] 11.4 Add entry for three-file Django package structure

## Phase 7: Integration Testing / 集成测试

- [x] 12. Integration Tests / 集成测试
  - [x] 12.1 Write full pipeline test (TOML → Django with quotes)
  - [x] 12.2 Write backward compatibility test (existing tests still pass)
  - [x] 12.3 Write three-file package generation test
  - [x] 12.4 Write cross-file import test
  - [x] 12.5 Test that old import paths still work (backward compatibility)
  - [x] 12.6 Run all existing tests to ensure no regressions

## Phase 8: Final Validation / 最终验证

- [x] 13. Final Checks / 最终检查
  - [x] 13.1 Run full test suite and ensure all tests pass
  - [x] 13.2 Verify code coverage meets targets (100% for new code)
  - [x] 13.3 Test CLI manually with various input formats
  - [x] 13.4 Test generated Django package in a real Django project
  - [x] 13.5 Verify all imports work correctly (both old and new paths)
  - [x] 13.6 Review all code for adherence to project standards (assert for validation, no try-except abuse)
  - [x] 13.7 Update version number if needed
  - [x] 13.8 Verify package structure is clean and well-organized
