# 安装指南

## 从源码安装（开发模式）

### 方法 1: 直接安装

```bash
# 进入 er-django 目录
cd packages/er-django

# 安装依赖（核心包）
pip install x007007007-er

# 安装 Django
pip install django>=4.2.0

# 安装 er-django（开发模式）
pip install -e .
```

### 方法 2: 从项目根目录安装

```bash
# 在项目根目录
pip install -e packages/er-django
```

### 方法 3: 同时安装核心包和 Django 插件

```bash
# 在项目根目录

# 1. 安装核心包
pip install -e .

# 2. 安装 Django 插件
pip install -e packages/er-django
```

## 验证安装

```bash
# 检查是否安装成功
python -c "import x007007007.er_django; print('✓ er-django installed')"

# 检查核心包
python -c "import x007007007.er; print('✓ er core installed')"

# 检查 Django
python -c "import django; print('✓ Django installed')"
```

## 在 Django 项目中使用

### 1. 添加到 INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ... 其他 apps
    'x007007007.er_django',
]
```

### 2. 验证 management commands

```bash
python manage.py help | grep er_

# 应该看到:
#   er_export
#   er_makemigrations
#   er_showmigrations
```

### 3. 测试功能

```bash
# 导出 ER 图
python manage.py er_export your_app

# 生成迁移
python manage.py er_makemigrations your_app

# 查看迁移状态
python manage.py er_showmigrations your_app
```

## 运行测试

```bash
cd packages/er-django

# 安装测试依赖
pip install pytest pytest-django

# 运行测试
pytest tests/
```

## 卸载

```bash
pip uninstall x007007007-er-django
```

## 故障排除

### 问题：找不到 er_django 模块

**解决**:
```bash
# 确保安装了核心包
pip install x007007007-er

# 重新安装 er-django
pip install -e packages/er-django
```

### 问题：找不到 management commands

**解决**:
```bash
# 确保在 settings.py 中添加了 'x007007007.er_django'
# 检查 Django 配置
python manage.py check
```

### 问题：导入错误

**解决**:
```bash
# 检查 Python 路径
python -c "import sys; print('\n'.join(sys.path))"

# 确保包目录在路径中
export PYTHONPATH="${PYTHONPATH}:$(pwd)/packages/er-django/src"
```

## 开发模式

如果你要开发 er-django：

```bash
# 1. 克隆仓库
git clone https://github.com/x007007007/er.git
cd er

# 2. 安装核心包（开发模式）
pip install -e .

# 3. 安装 er-django（开发模式）
pip install -e packages/er-django

# 4. 安装开发依赖
pip install pytest pytest-django pytest-cov

# 5. 运行测试
cd packages/er-django
pytest tests/

# 6. 测试示例项目
cd ../../examples/django_blog
python manage.py er_export blog
```

## 构建和发布

```bash
cd packages/er-django

# 1. 安装构建工具
pip install build twine

# 2. 构建包
python -m build

# 3. 检查包
twine check dist/*

# 4. 发布到 PyPI（需要账号）
twine upload dist/*

# 或发布到 Test PyPI
twine upload --repository testpypi dist/*
```

## 依赖关系

```
x007007007-er-django
├── x007007007-er (>=0.1.0)  # 核心包
├── django (>=4.2.0)          # Django 框架
├── pydantic (>=2.0.0)        # 数据验证
└── pyyaml (>=6.0.0)          # YAML 支持
```

## 版本兼容性

| er-django | er core | Django | Python |
|-----------|---------|--------|--------|
| 0.1.x     | >=0.1.0 | >=4.2  | >=3.11 |

## 更多信息

- [README.md](README.md) - 用户文档
- [../../examples/django_blog/](../../examples/django_blog/) - 示例项目
- [src/x007007007/er_django/DESIGN.md](src/x007007007/er_django/DESIGN.md) - 设计文档
