#!/bin/bash
# 测试 ER Django 功能的自动化脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "ER Django 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_command() {
    local test_name=$1
    local command=$2
    
    echo -n "测试: $test_name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 清理函数
cleanup() {
    echo ""
    echo "清理测试文件..."
    rm -rf .migrations/
    rm -f blog_er.mmd blog_er.puml
    rm -f db.sqlite3
}

# 设置清理陷阱
trap cleanup EXIT

echo "1. 环境检查"
echo "----------------------------------------"

# 检查 Django
test_command "Django 已安装" "python -c 'import django'"

# 检查 er_django
test_command "er_django 已安装" "python -c 'import x007007007.er_django'"

# 检查核心包
test_command "er 核心包已安装" "python -c 'import x007007007.er'"

echo ""
echo "2. Django 项目检查"
echo "----------------------------------------"

# 检查 Django 配置
test_command "Django 配置正确" "python manage.py check"

# 检查 models
test_command "Models 定义正确" "python manage.py check blog"

echo ""
echo "3. ER 导出功能测试"
echo "----------------------------------------"

# 导出 Mermaid 格式
if python manage.py er_export blog --format mermaid --output blog_er.mmd 2>&1; then
    if [ -f "blog_er.mmd" ]; then
        echo -e "测试: 导出 Mermaid ER 图 ... ${GREEN}✓ 通过${NC}"
        ((TESTS_PASSED++))
        
        # 检查文件内容
        if grep -q "erDiagram" blog_er.mmd; then
            echo -e "测试: Mermaid 文件格式正确 ... ${GREEN}✓ 通过${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "测试: Mermaid 文件格式正确 ... ${RED}✗ 失败${NC}"
            ((TESTS_FAILED++))
        fi
        
        # 检查是否包含模型
        if grep -q "Post" blog_er.mmd && grep -q "Comment" blog_er.mmd; then
            echo -e "测试: ER 图包含所有模型 ... ${GREEN}✓ 通过${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "测试: ER 图包含所有模型 ... ${RED}✗ 失败${NC}"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "测试: 导出 Mermaid ER 图 ... ${RED}✗ 失败${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "测试: 导出 Mermaid ER 图 ... ${RED}✗ 失败${NC}"
    ((TESTS_FAILED++))
fi

# 导出 PlantUML 格式
if python manage.py er_export blog --format plantuml --output blog_er.puml 2>&1; then
    if [ -f "blog_er.puml" ]; then
        echo -e "测试: 导出 PlantUML ER 图 ... ${GREEN}✓ 通过${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "测试: 导出 PlantUML ER 图 ... ${RED}✗ 失败${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "测试: 导出 PlantUML ER 图 ... ${RED}✗ 失败${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "4. ER 迁移功能测试"
echo "----------------------------------------"

# 生成初始迁移
if python manage.py er_makemigrations blog 2>&1; then
    if [ -f ".migrations/blog/0001_initial.yaml" ]; then
        echo -e "测试: 生成初始迁移 ... ${GREEN}✓ 通过${NC}"
        ((TESTS_PASSED++))
        
        # 检查迁移文件内容
        if grep -q "CreateTable" .migrations/blog/0001_initial.yaml; then
            echo -e "测试: 迁移包含 CreateTable 操作 ... ${GREEN}✓ 通过${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "测试: 迁移包含 CreateTable 操作 ... ${RED}✗ 失败${NC}"
            ((TESTS_FAILED++))
        fi
        
        if grep -q "AddForeignKey" .migrations/blog/0001_initial.yaml; then
            echo -e "测试: 迁移包含 AddForeignKey 操作 ... ${GREEN}✓ 通过${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "测试: 迁移包含 AddForeignKey 操作 ... ${RED}✗ 失败${NC}"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "测试: 生成初始迁移 ... ${RED}✗ 失败${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "测试: 生成初始迁移 ... ${RED}✗ 失败${NC}"
    ((TESTS_FAILED++))
fi

# 查看迁移状态
if python manage.py er_showmigrations blog 2>&1 | grep -q "0001_initial"; then
    echo -e "测试: 显示迁移状态 ... ${GREEN}✓ 通过${NC}"
    ((TESTS_PASSED++))
else
    echo -e "测试: 显示迁移状态 ... ${RED}✗ 失败${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC}"
echo "总计: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}有 $TESTS_FAILED 个测试失败${NC}"
    exit 1
fi
