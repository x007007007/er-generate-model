# Task 14.1 Verification: 实现文件名生成逻辑

## Task Description
实现文件名生成逻辑，将类名转换为 snake_case 格式用于文件命名。

## Requirements
- 需求 5.2: 生成的文件命名应使用 model 类名的 snake_case 形式作为文件名

## Implementation

### 1. Created Shared Utility Module
**File**: `packages/er-gen-core/src/x007007007/er/renderers/python/utils.py`

Created a shared utility module containing the `to_snake_case` function that handles:
- Simple CamelCase: `User` -> `user`
- Multi-word: `UserAccount` -> `user_account`
- Acronyms: `HTTPRequest` -> `http_request`
- Numbers: `Model3D` -> `model3_d`
- Already snake_case: `user_profile` -> `user_profile`

### 2. Refactored Django Renderer
**File**: `packages/er-gen-core/src/x007007007/er/renderers/python/django/renderer.py`

- Removed duplicate `to_snake_case` implementation
- Imported from shared utils module
- All existing functionality preserved

### 3. Updated SQLAlchemy Renderer
**File**: `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/renderer.py`

- Added import of `to_snake_case` from shared utils
- Function now available for use in SQLAlchemy multi-file output (Task 14.2)

### 4. Updated Exports
**Files**: 
- `packages/er-gen-core/src/x007007007/er/renderers/python/django/__init__.py`
- `packages/er-gen-core/src/x007007007/er/renderers/python/sqlalchemy/__init__.py`

Both modules now export `to_snake_case` for external use.

## Test Coverage

### Created New Test File
**File**: `packages/er-gen-core/tests/test_python_utils.py`

Comprehensive test suite covering:
- ✅ Simple CamelCase conversion
- ✅ Multi-word CamelCase conversion
- ✅ Complex CamelCase conversion
- ✅ Acronym handling (HTTPRequest, XMLParser)
- ✅ Already snake_case strings
- ✅ Single letter names
- ✅ Names with numbers (User2, Model3D)
- ✅ Special characters (edge cases)
- ✅ Consecutive uppercase letters
- ✅ Empty strings
- ✅ Lowercase only strings

### Test Results
```bash
$ uv run pytest packages/er-gen-core/tests/test_python_utils.py -v
================================ 11 passed in 0.13s =================================
```

### Verified Existing Tests
All existing Django renderer tests continue to pass:
```bash
$ uv run pytest packages/er-gen-core/tests/test_django_renderer.py -v
================================ 44 passed in 0.79s =================================
```

All existing SQLAlchemy renderer tests continue to pass:
```bash
$ uv run pytest packages/er-gen-core/tests/test_sqlalchemy_renderer.py -v
================================ 18 passed in 0.58s =================================
```

## Examples

```python
from x007007007.er.renderers.python.utils import to_snake_case

# Simple cases
assert to_snake_case("User") == "user"
assert to_snake_case("UserAccount") == "user_account"

# Acronyms (Requirement 5.2)
assert to_snake_case("HTTPRequest") == "http_request"
assert to_snake_case("XMLParser") == "xml_parser"

# Numbers (Requirement 5.2)
assert to_snake_case("User2") == "user2"
assert to_snake_case("Model3D") == "model3_d"

# Already snake_case
assert to_snake_case("user_profile") == "user_profile"
```

## Usage in SQLAlchemy Renderer

The function is now available for Task 14.2 (multi-file output):

```python
from x007007007.er.renderers.python.sqlalchemy import to_snake_case

# For entity named "UserAccount"
filename = f"{to_snake_case('UserAccount')}.py"  # "user_account.py"

# For entity named "HTTPRequest"
filename = f"{to_snake_case('HTTPRequest')}.py"  # "http_request.py"
```

## Verification Checklist

- [x] Created shared `to_snake_case` utility function
- [x] Handles simple CamelCase conversion
- [x] Handles multi-word CamelCase conversion
- [x] Handles acronyms (HTTPRequest -> http_request)
- [x] Handles numbers (Model3D -> model3_d)
- [x] Handles special characters gracefully
- [x] Refactored Django renderer to use shared function
- [x] Updated SQLAlchemy renderer to import function
- [x] Updated module exports
- [x] Created comprehensive test suite (11 tests)
- [x] All new tests pass
- [x] All existing Django renderer tests pass (44 tests)
- [x] All existing SQLAlchemy renderer tests pass (18 tests)
- [x] Function available for use in Task 14.2

## Status
✅ **COMPLETE** - Task 14.1 successfully implemented and verified.

The filename generation logic is now ready for use in Task 14.2 (multi-file output implementation).
