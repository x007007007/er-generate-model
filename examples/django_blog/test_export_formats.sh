#!/bin/bash
# 测试 ER Django 导出功能

echo "=== ER Django 导出测试 ==="
echo ""

echo "1. 导出所有 app 为 Mermaid 格式"
uv run python manage.py er_export --format mermaid
echo ""

echo "2. 导出所有 app 为 PlantUML 格式"
uv run python manage.py er_export --format plantuml
echo ""

echo "3. 导出所有 app 为 TOML 格式"
uv run python manage.py er_export --format toml
echo ""

echo "4. 导出单个 app (blog)"
uv run python manage.py er_export blog --format mermaid
echo ""

echo "5. 导出多个指定 app (users, products)"
uv run python manage.py er_export users products --format toml
echo ""

echo "=== 测试完成 ==="
echo ""
echo "生成的文件位于: er_export/"
ls -lh er_export/
