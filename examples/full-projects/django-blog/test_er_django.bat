@echo off
REM 测试 ER Django 功能的自动化脚本 (Windows)

setlocal enabledelayedexpansion

echo ==========================================
echo ER Django 功能测试
echo ==========================================
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

echo 1. 环境检查
echo ----------------------------------------

REM 检查 Django
python -c "import django" >nul 2>&1
if %errorlevel% equ 0 (
    echo 测试: Django 已安装 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: Django 已安装 ... [FAIL]
    set /a TESTS_FAILED+=1
)

REM 检查 er_django
python -c "import x007007007.er_django" >nul 2>&1
if %errorlevel% equ 0 (
    echo 测试: er_django 已安装 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: er_django 已安装 ... [FAIL]
    set /a TESTS_FAILED+=1
)

REM 检查核心包
python -c "import x007007007.er" >nul 2>&1
if %errorlevel% equ 0 (
    echo 测试: er 核心包已安装 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: er 核心包已安装 ... [FAIL]
    set /a TESTS_FAILED+=1
)

echo.
echo 2. Django 项目检查
echo ----------------------------------------

REM 检查 Django 配置
python manage.py check >nul 2>&1
if %errorlevel% equ 0 (
    echo 测试: Django 配置正确 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: Django 配置正确 ... [FAIL]
    set /a TESTS_FAILED+=1
)

REM 检查 models
python manage.py check blog >nul 2>&1
if %errorlevel% equ 0 (
    echo 测试: Models 定义正确 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: Models 定义正确 ... [FAIL]
    set /a TESTS_FAILED+=1
)

echo.
echo 3. ER 导出功能测试
echo ----------------------------------------

REM 导出 Mermaid 格式
python manage.py er_export blog --format mermaid --output blog_er.mmd >nul 2>&1
if exist blog_er.mmd (
    echo 测试: 导出 Mermaid ER 图 ... [OK]
    set /a TESTS_PASSED+=1
    
    REM 检查文件内容
    findstr /C:"erDiagram" blog_er.mmd >nul 2>&1
    if %errorlevel% equ 0 (
        echo 测试: Mermaid 文件格式正确 ... [OK]
        set /a TESTS_PASSED+=1
    ) else (
        echo 测试: Mermaid 文件格式正确 ... [FAIL]
        set /a TESTS_FAILED+=1
    )
) else (
    echo 测试: 导出 Mermaid ER 图 ... [FAIL]
    set /a TESTS_FAILED+=1
)

REM 导出 PlantUML 格式
python manage.py er_export blog --format plantuml --output blog_er.puml >nul 2>&1
if exist blog_er.puml (
    echo 测试: 导出 PlantUML ER 图 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: 导出 PlantUML ER 图 ... [FAIL]
    set /a TESTS_FAILED+=1
)

echo.
echo 4. ER 迁移功能测试
echo ----------------------------------------

REM 生成初始迁移
python manage.py er_makemigrations blog >nul 2>&1
if exist .migrations\blog\0001_initial.yaml (
    echo 测试: 生成初始迁移 ... [OK]
    set /a TESTS_PASSED+=1
    
    REM 检查迁移文件内容
    findstr /C:"CreateTable" .migrations\blog\0001_initial.yaml >nul 2>&1
    if %errorlevel% equ 0 (
        echo 测试: 迁移包含 CreateTable 操作 ... [OK]
        set /a TESTS_PASSED+=1
    ) else (
        echo 测试: 迁移包含 CreateTable 操作 ... [FAIL]
        set /a TESTS_FAILED+=1
    )
    
    findstr /C:"AddForeignKey" .migrations\blog\0001_initial.yaml >nul 2>&1
    if %errorlevel% equ 0 (
        echo 测试: 迁移包含 AddForeignKey 操作 ... [OK]
        set /a TESTS_PASSED+=1
    ) else (
        echo 测试: 迁移包含 AddForeignKey 操作 ... [FAIL]
        set /a TESTS_FAILED+=1
    )
) else (
    echo 测试: 生成初始迁移 ... [FAIL]
    set /a TESTS_FAILED+=1
)

REM 查看迁移状态
python manage.py er_showmigrations blog 2>&1 | findstr /C:"0001_initial" >nul 2>&1
if %errorlevel% equ 0 (
    echo 测试: 显示迁移状态 ... [OK]
    set /a TESTS_PASSED+=1
) else (
    echo 测试: 显示迁移状态 ... [FAIL]
    set /a TESTS_FAILED+=1
)

echo.
echo ==========================================
echo 测试总结
echo ==========================================
echo 通过: %TESTS_PASSED%
echo 失败: %TESTS_FAILED%
set /a TOTAL=%TESTS_PASSED%+%TESTS_FAILED%
echo 总计: %TOTAL%
echo.

if %TESTS_FAILED% equ 0 (
    echo 所有测试通过！
    exit /b 0
) else (
    echo 有 %TESTS_FAILED% 个测试失败
    exit /b 1
)
