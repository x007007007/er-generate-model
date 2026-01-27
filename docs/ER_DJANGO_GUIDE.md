# ER Django 集成指南

## 📋 概述

`x007007007-er-django` 是一个 Django 插件，用于将 Django models 转换为 ER 图和 ER 迁移系统。

## 🎯 两种发布方案对比

### 方案 1: 集成在主包中（当前实现）

**优点**:
- 代码在同一仓库，便于开发和维护
- 共享依赖和工具
- 版本同步简单

**缺点**:
- Django 成为可选依赖，增加主包体积
- 用户需要安装额外依赖

**适用场景**: 
- 开发阶段
- 小型项目
- 需要紧密集成的场景

### 方案 2: 独立包发布（推荐用于生产）

**优点**:
- 独立版本管理
- 减少主包依赖
- 用户按需安装
- 更清晰的职责分离

**缺点**:
- 需要维护多个包
- 版本同步复杂
- 发布流程更复杂

**适用场景**:
- 生产环境
- 大型项目
- 需要独立演进的场景

## 🏗️ 当前实现（方案 1）

### 目录结构

```
project/
├── src/x007007007/
│   ├── er/                    # 核心包
│   ├── er_migrate/            # 迁移系统
│   └── er_django/             # Django 插件
│       ├── pyproject.toml     # 独立配置（预留）
│       ├── __init__.py
│       ├── parser.py
│       ├── introspector.py
│       └── management/
├── examples/
│   └── django_blog/           # Django 示例项目
├── pyproject.toml             # 主项目配置
└── README.md
```

### 安装方式

```bash
# 安装核心包
pip install x007007007-er

# 安装 Django 支持
pip install x007007007-er[django]

# 或安装所有可选依赖
pip install x007007007-er[all]
```

## 🚀 迁移到独立包（方案 2）

如果将来需要独立发布，可以按以下步骤操作：

### 步骤 1: 创建独立仓库

```bash
# 创建新仓库
mkdir x007007007-er-django
cd x007007007-er-django

# 复制代码
cp -r ../er/src/x007007007/er_django ./src/x007007007/
cp ../er/src/x007007007/er_django/pyproject.toml ./
```

### 步骤 2: 更新依赖

```toml
# pyproject.toml
[project]
name = "x007007007-er-django"
dependencies = [
    "x007007007-er>=0.1.0",  # 依赖核心包
    "django>=4.2.0",
]
```

### 步骤 3: 发布到 PyPI

```bash
# 构建包
python -m build

# 发布到 PyPI
python -m twine upload dist/*
```

### 步骤 4: 用户安装

```bash
# 独立安装
pip install x007007007-er-django
```

## 📦 Monorepo 方案（推荐用于开发）

如果需要在同一仓库管理多个包，可以使用 monorepo 结构：

### 目录结构

```
project/
├── packages/
│   ├── er/                    # 核心包
│   │   ├── pyproject.toml
│   │   └── src/x007007007/er/
│   ├── er-migrate/            # 迁移系统
│   │   ├── pyproject.toml
│   │   └── src/x007007007/er_migrate/
│   └── er-django/             # Django 插件
│       ├── pyproject.toml
│       └── src/x007007007/er_django/
├── examples/
│   └── django_blog/
├── pyproject.toml             # 工作区配置
└── README.md
```

### 工作区配置

```toml
# 根 pyproject.toml
[tool.uv.workspace]
members = [
    "packages/er",
    "packages/er-migrate",
    "packages/er-django",
]
```

### 开发安装

```bash
# 安装所有包（开发模式）
uv pip install -e packages/er
uv pip install -e packages/er-migrate
uv pip install -e packages/er-django
```

## 🧪 测试 Django 集成

### 快速测试

```bash
cd examples/django_blog

# 安装依赖
pip install django>=4.2.0
pip install -e ../../

# 运行测试
python manage.py er_export blog
python manage.py er_makemigrations blog
python manage.py er_showmigrations blog
```

### 自动化测试

```bash
# Linux/Mac
./test_er_django.sh

# Windows
test_er_django.bat
```

## 📝 发布清单

### 发布核心包

```bash
# 1. 更新版本号
# 2. 运行测试
pytest

# 3. 构建包
python -m build

# 4. 发布到 PyPI
python -m twine upload dist/*
```

### 发布 Django 插件（独立包）

```bash
cd src/x007007007/er_django

# 1. 更新版本号
# 2. 运行测试
pytest

# 3. 构建包
python -m build

# 4. 发布到 PyPI
python -m twine upload dist/*
```

## 🎯 推荐方案

### 当前阶段（开发）
✅ **使用方案 1**: 集成在主包中
- 便于开发和测试
- 代码在同一仓库
- 使用可选依赖 `[django]`

### 未来阶段（生产）
✅ **迁移到方案 2**: 独立包发布
- 当 Django 插件稳定后
- 当有独立版本需求时
- 当需要独立演进时

### 长期方案（大型项目）
✅ **采用 Monorepo**: 多包管理
- 使用 uv workspace
- 统一的开发环境
- 独立的发布流程

## 📚 相关文档

- [ER Django README](../src/x007007007/er_django/README.md)
- [ER Django 设计文档](../src/x007007007/er_django/DESIGN.md)
- [Django 示例项目](../examples/django_blog/README.md)
- [快速开始指南](../examples/django_blog/QUICKSTART.md)

## 🤝 贡献指南

### 添加新功能

1. 在 `src/x007007007/er_django/` 中添加代码
2. 添加测试到 `tests/test_er_django.py`
3. 更新文档
4. 提交 PR

### 报告问题

在 GitHub Issues 中报告问题，包含：
- Django 版本
- Python 版本
- 错误信息
- 重现步骤

## 📄 许可证

MIT License
