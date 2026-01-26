# 项目结构说明

## 📁 目录结构

```
ER/
├── src/x007007007/          # 核心包源代码
│   ├── er/                  # ER 图解析和渲染
│   ├── er_ai/               # AI 建模工具
│   ├── er_mcp/              # MCP 服务器
│   └── er_migrate/          # ER 迁移系统
│
├── packages/                # 独立包（可单独发布）
│   ├── README.md            # 包管理说明
│   └── er-django/           # Django 集成插件
│       ├── pyproject.toml
│       ├── README.md
│       ├── INSTALL.md
│       ├── src/x007007007/
│       │   └── er_django/
│       └── tests/
│
├── examples/                # 示例项目
│   ├── *.mmd                # Mermaid 示例
│   ├── *.py                 # Python 示例
│   └── django_blog/         # Django 示例项目
│       ├── manage.py
│       ├── blog/            # Django app
│       ├── README.md
│       ├── QUICKSTART.md
│       └── test_er_django.sh
│
├── tests/                   # 核心包测试
│   ├── test_er.py
│   ├── test_er_migrate.py
│   └── ...
│
├── docs/                    # 文档
│   └── ER_DJANGO_GUIDE.md
│
├── tools/                   # 开发工具
│   ├── generate_antlr.sh
│   └── generate_antlr.bat
│
├── pyproject.toml           # 核心包配置
├── README.md                # 主文档
├── CHANGELOG.md
└── PROJECT_STRUCTURE.md     # 本文件
```

## 📦 包说明

### 核心包 (x007007007-er)

**位置**: `src/x007007007/`

**功能**:
- ER 图解析（Mermaid, PlantUML, TOML）
- 代码生成（Django, SQLAlchemy）
- 数据库反向工程
- ER 迁移系统
- AI 建模工具
- MCP 服务器

**安装**:
```bash
pip install -e .
```

**模块**:
- `x007007007.er` - 核心 ER 功能
- `x007007007.er_ai` - AI 建模
- `x007007007.er_mcp` - MCP 服务器
- `x007007007.er_migrate` - 迁移系统

### Django 插件 (x007007007-er-django)

**位置**: `packages/er-django/`

**功能**:
- Django models → ER 图
- Django models → ER 迁移
- Django management commands

**安装**:
```bash
pip install -e packages/er-django/
```

**模块**:
- `x007007007.er_django` - Django 集成

**文档**:
- [README.md](packages/er-django/README.md)
- [INSTALL.md](packages/er-django/INSTALL.md)
- [DESIGN.md](packages/er-django/src/x007007007/er_django/DESIGN.md)

## 🔗 依赖关系

```
核心包 (x007007007-er)
    ↓ 依赖
Django 插件 (x007007007-er-django)
```

Django 插件依赖核心包，但核心包不依赖 Django。

## 🚀 开发工作流

### 1. 开发核心功能

```bash
# 在项目根目录
cd .

# 修改核心代码
vim src/x007007007/er/...

# 运行测试
pytest tests/

# 安装（开发模式）
pip install -e .
```

### 2. 开发 Django 插件

```bash
# 进入插件目录
cd packages/er-django

# 修改代码
vim src/x007007007/er_django/...

# 运行测试
pytest tests/

# 安装（开发模式）
pip install -e .
```

### 3. 测试集成

```bash
# 使用示例项目测试
cd examples/django_blog

# 安装依赖
pip install -e ../../                    # 核心包
pip install -e ../../packages/er-django/ # Django 插件
pip install django>=4.2.0

# 测试功能
python manage.py er_export blog
python manage.py er_makemigrations blog
```

## 📝 添加新功能

### 添加到核心包

1. 在 `src/x007007007/er/` 中添加代码
2. 在 `tests/` 中添加测试
3. 更新 `README.md`
4. 提交 PR

### 添加新的独立包

1. 创建目录结构：
   ```bash
   mkdir -p packages/new-package/src/x007007007
   mkdir -p packages/new-package/tests
   ```

2. 创建 `pyproject.toml`
3. 实现功能
4. 添加测试
5. 编写文档
6. 更新 `packages/README.md`

## 🧪 测试策略

### 核心包测试

```bash
# 运行所有测试
pytest tests/

# 运行特定模块测试
pytest tests/test_er.py
pytest tests/test_er_migrate/

# 测试覆盖率
pytest --cov=src/x007007007
```

### Django 插件测试

```bash
cd packages/er-django

# 运行测试
pytest tests/

# 测试覆盖率
pytest --cov=src/x007007007/er_django
```

### 集成测试

```bash
cd examples/django_blog

# 自动化测试
./test_er_django.sh  # Linux/Mac
test_er_django.bat   # Windows
```

## 📦 发布流程

### 发布核心包

```bash
# 1. 更新版本号（自动通过 git tag）
git tag v0.2.0
git push origin v0.2.0

# 2. 构建
python -m build

# 3. 发布
twine upload dist/*
```

### 发布 Django 插件

```bash
cd packages/er-django

# 1. 更新版本号
# 编辑 pyproject.toml

# 2. 构建
python -m build

# 3. 发布
twine upload dist/*
```

## 🔄 版本管理

### 核心包版本

使用 `setuptools-scm` 自动从 git tag 生成版本号：
- Tag: `v0.1.0` → Version: `0.1.0`
- 开发版本: `0.1.0.dev5+g1234567`

### Django 插件版本

在 `packages/er-django/pyproject.toml` 中手动管理：
```toml
version = "0.1.0"
```

### 版本兼容性

Django 插件指定核心包的兼容版本：
```toml
dependencies = [
    "x007007007-er>=0.1.0,<0.3.0",
]
```

## 📚 文档位置

### 核心包文档
- [README.md](README.md) - 主文档
- [CHANGELOG.md](CHANGELOG.md) - 变更日志
- [examples/README.md](examples/README.md) - 示例说明

### Django 插件文档
- [packages/er-django/README.md](packages/er-django/README.md) - 用户文档
- [packages/er-django/INSTALL.md](packages/er-django/INSTALL.md) - 安装指南
- [packages/er-django/src/x007007007/er_django/DESIGN.md](packages/er-django/src/x007007007/er_django/DESIGN.md) - 设计文档

### 示例项目文档
- [examples/django_blog/README.md](examples/django_blog/README.md) - 完整文档
- [examples/django_blog/QUICKSTART.md](examples/django_blog/QUICKSTART.md) - 快速开始

### 其他文档
- [docs/ER_DJANGO_GUIDE.md](docs/ER_DJANGO_GUIDE.md) - Django 集成指南
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 本文件

## 🎯 设计原则

### 1. 模块化
- 核心功能在主包
- 框架特定功能在独立包
- 清晰的依赖关系

### 2. 独立性
- 每个包可以独立发布
- 独立的版本管理
- 独立的测试

### 3. 可扩展性
- 易于添加新的独立包
- 统一的包结构
- 清晰的接口

### 4. 文档完整
- 每个包都有完整文档
- 示例项目演示用法
- 设计文档说明架构

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码（遵循代码规范）
4. 添加测试（覆盖率 > 80%）
5. 更新文档
6. 提交 PR

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者！

---

**最后更新**: 2026-01-26
**维护者**: xxc <x007007007@hotmail.com>
