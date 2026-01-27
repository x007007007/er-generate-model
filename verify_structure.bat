@echo off
REM 验证项目结构的脚本 (Windows)

setlocal enabledelayedexpansion

echo ==========================================
echo 验证项目结构
echo ==========================================
echo.

set CHECKS_PASSED=0
set CHECKS_FAILED=0

echo 1. 核心包结构
echo ----------------------------------------
call :check_exists "src\x007007007\er" "核心 ER 模块"
call :check_exists "src\x007007007\er_migrate" "迁移系统"
call :check_exists "src\x007007007\er_ai" "AI 建模"
call :check_exists "src\x007007007\er_mcp" "MCP 服务器"
call :check_exists "pyproject.toml" "核心包配置"

echo.
echo 2. Django 插件结构
echo ----------------------------------------
call :check_exists "packages\er-django" "Django 插件目录"
call :check_exists "packages\er-django\pyproject.toml" "Django 插件配置"
call :check_exists "packages\er-django\README.md" "Django 插件文档"
call :check_exists "packages\er-django\INSTALL.md" "Django 安装指南"
call :check_exists "packages\er-django\src\x007007007\er_django" "Django 插件源码"
call :check_exists "packages\er-django\tests" "Django 插件测试"

echo.
echo 3. Django 插件核心文件
echo ----------------------------------------
call :check_exists "packages\er-django\src\x007007007\er_django\__init__.py" "包初始化"
call :check_exists "packages\er-django\src\x007007007\er_django\parser.py" "解析器"
call :check_exists "packages\er-django\src\x007007007\er_django\introspector.py" "内省工具"
call :check_exists "packages\er-django\src\x007007007\er_django\apps.py" "Django AppConfig"

echo.
echo 4. 示例项目
echo ----------------------------------------
call :check_exists "examples\django_blog" "Django 示例项目"
call :check_exists "examples\django_blog\manage.py" "Django 管理脚本"
call :check_exists "examples\django_blog\blog\models.py" "示例模型"
call :check_exists "examples\django_blog\README.md" "示例文档"

echo.
echo 5. 文档
echo ----------------------------------------
call :check_exists "README.md" "主文档"
call :check_exists "PROJECT_STRUCTURE.md" "项目结构说明"
call :check_exists "DJANGO_INTEGRATION_SUMMARY.md" "Django 集成总结"
call :check_exists "packages\README.md" "包管理说明"

echo.
echo 6. 验证 Python 导入
echo ----------------------------------------

python -c "import x007007007.er" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 核心包可导入
    set /a CHECKS_PASSED+=1
) else (
    echo [WARN] 核心包未安装 ^(需要: pip install -e .^)
)

python -c "import x007007007.er_django" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Django 插件可导入
    set /a CHECKS_PASSED+=1
) else (
    echo [WARN] Django 插件未安装 ^(需要: pip install -e packages/er-django/^)
)

echo.
echo ==========================================
echo 验证总结
echo ==========================================
echo 通过: %CHECKS_PASSED%
echo 失败: %CHECKS_FAILED%
set /a TOTAL=%CHECKS_PASSED%+%CHECKS_FAILED%
echo 总计: %TOTAL%
echo.

if %CHECKS_FAILED% equ 0 (
    echo [OK] 项目结构正确！
    echo.
    echo 下一步：
    echo 1. 安装核心包: pip install -e .
    echo 2. 安装 Django 插件: pip install -e packages/er-django/
    echo 3. 测试示例项目: cd examples\django_blog ^&^& test_er_django.bat
    exit /b 0
) else (
    echo [FAIL] 项目结构有问题，请检查
    exit /b 1
)

:check_exists
if exist "%~1" (
    echo [OK] %~2: %~1
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] %~2: %~1 ^(不存在^)
    set /a CHECKS_FAILED+=1
)
goto :eof
