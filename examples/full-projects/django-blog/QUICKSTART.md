# 快速开始指南

## 5 分钟快速测试 ER Django

### 步骤 1: 安装依赖

```bash
# 进入示例项目目录
cd examples/django_blog

# 安装核心包和 Django 插件
pip install django>=4.2.0
pip install -e ../../
pip install -e ../../packages/er-django/
```

### 步骤 2: 初始化数据库

```bash
# 运行 Django 迁移（创建基础表）
python manage.py migrate
```

### 步骤 3: 测试 ER 导出

```bash
# 导出 ER 图到控制台
python manage.py er_export blog

# 或保存到文件
python manage.py er_export blog --output blog_er.mmd
```

**预期输出**: 看到完整的 Mermaid ER 图，包含 Category, Tag, Post, Comment, UserProfile 等模型。

### 步骤 4: 生成 ER 迁移

```bash
# 生成初始迁移
python manage.py er_makemigrations blog

# 查看生成的文件
cat .migrations/blog/0001_initial.yaml  # Linux/Mac
type .migrations\blog\0001_initial.yaml  # Windows
```

**预期输出**: 
```
Parsing Django models from app 'blog'...
Found 5 models
Detected XX operations:
  - CreateTable
  - CreateTable
  ...

Migrations for 'blog':
  0001_initial.yaml

Migration saved to: .migrations/blog/0001_initial.yaml
```

### 步骤 5: 查看迁移状态

```bash
python manage.py er_showmigrations blog
```

**预期输出**:
```
blog:
  [X] 0001_initial
```

## 自动化测试

### Linux/Mac

```bash
chmod +x test_er_django.sh
./test_er_django.sh
```

### Windows

```cmd
test_er_django.bat
```

## 成功标志

如果看到以下内容，说明一切正常：

✅ 可以导出 ER 图
✅ 生成了 `.migrations/blog/0001_initial.yaml` 文件
✅ 迁移文件包含 CreateTable 和 AddForeignKey 操作
✅ `er_showmigrations` 显示迁移列表

## 下一步

1. 查看生成的 ER 图：`blog_er.mmd`
2. 查看生成的迁移文件：`.migrations/blog/0001_initial.yaml`
3. 尝试修改 models.py 并生成新迁移
4. 阅读完整文档：`README.md`

## 故障排除

### 问题：找不到命令

```bash
# 确保安装了 er-django
pip list | grep er-django

# 重新安装
pip install -e ../../
```

### 问题：导入错误

```bash
# 检查 Python 路径
python -c "import x007007007.er_django; print('OK')"

# 如果失败，检查安装
pip install -e ../../ --force-reinstall
```

### 问题：Django 配置错误

```bash
# 检查 Django 配置
python manage.py check

# 确保在 settings.py 中添加了 'x007007007.er_django'
```

## 需要帮助？

查看详细文档：
- [README.md](README.md) - 完整文档
- [../../src/x007007007/er_django/README.md](../../src/x007007007/er_django/README.md) - ER Django 文档
- [../../src/x007007007/er_django/DESIGN.md](../../src/x007007007/er_django/DESIGN.md) - 设计文档
