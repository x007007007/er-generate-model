#!/bin/bash
# 验证项目结构的脚本

echo "=========================================="
echo "验证项目结构"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

# 检查函数
check_exists() {
    local path=$1
    local description=$2
    
    if [ -e "$path" ]; then
        echo -e "${GREEN}✓${NC} $description: $path"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description: $path (不存在)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo "1. 核心包结构"
echo "----------------------------------------"
check_exists "src/x007007007/er" "核心 ER 模块"
check_exists "src/x007007007/er_migrate" "迁移系统"
check_exists "src/x007007007/er_ai" "AI 建模"
check_exists "src/x007007007/er_mcp" "MCP 服务器"
check_exists "pyproject.toml" "核心包配置"

echo ""
echo "2. Django 插件结构"
echo "----------------------------------------"
check_exists "packages/er-django" "Django 插件目录"
check_exists "packages/er-django/pyproject.toml" "Django 插件配置"
check_exists "packages/er-django/README.md" "Django 插件文档"
check_exists "packages/er-django/INSTALL.md" "Django 安装指南"
check_exists "packages/er-django/src/x007007007/er_django" "Django 插件源码"
check_exists "packages/er-django/tests" "Django 插件测试"

echo ""
echo "3. Django 插件核心文件"
echo "----------------------------------------"
check_exists "packages/er-django/src/x007007007/er_django/__init__.py" "包初始化"
check_exists "packages/er-django/src/x007007007/er_django/parser.py" "解析器"
check_exists "packages/er-django/src/x007007007/er_django/introspector.py" "内省工具"
check_exists "packages/er-django/src/x007007007/er_django/apps.py" "Django AppConfig"
check_exists "packages/er-django/src/x007007007/er_django/management/commands/er_export.py" "导出命令"
check_exists "packages/er-django/src/x007007007/er_django/management/commands/er_makemigrations.py" "迁移命令"
check_exists "packages/er-django/src/x007007007/er_django/management/commands/er_showmigrations.py" "状态命令"

echo ""
echo "4. 示例项目"
echo "----------------------------------------"
check_exists "examples/django_blog" "Django 示例项目"
check_exists "examples/django_blog/manage.py" "Django 管理脚本"
check_exists "examples/django_blog/blog/models.py" "示例模型"
check_exists "examples/django_blog/README.md" "示例文档"
check_exists "examples/django_blog/QUICKSTART.md" "快速开始"
check_exists "examples/django_blog/test_er_django.sh" "测试脚本"

echo ""
echo "5. 文档"
echo "----------------------------------------"
check_exists "README.md" "主文档"
check_exists "PROJECT_STRUCTURE.md" "项目结构说明"
check_exists "DJANGO_INTEGRATION_SUMMARY.md" "Django 集成总结"
check_exists "packages/README.md" "包管理说明"
check_exists "docs/ER_DJANGO_GUIDE.md" "Django 集成指南"

echo ""
echo "6. 验证 Python 导入"
echo "----------------------------------------"

# 检查核心包
if python -c "import x007007007.er" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 核心包可导入"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} 核心包未安装（需要: pip install -e .）"
fi

# 检查 Django 插件
if python -c "import x007007007.er_django" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Django 插件可导入"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Django 插件未安装（需要: pip install -e packages/er-django/）"
fi

echo ""
echo "=========================================="
echo "验证总结"
echo "=========================================="
echo -e "通过: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "失败: ${RED}$CHECKS_FAILED${NC}"
echo "总计: $((CHECKS_PASSED + CHECKS_FAILED))"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 项目结构正确！${NC}"
    echo ""
    echo "下一步："
    echo "1. 安装核心包: pip install -e ."
    echo "2. 安装 Django 插件: pip install -e packages/er-django/"
    echo "3. 测试示例项目: cd examples/django_blog && ./test_er_django.sh"
    exit 0
else
    echo -e "${RED}✗ 项目结构有问题，请检查${NC}"
    exit 1
fi
