# Packages 目录

这个目录包含独立的包，可以单独发布到 PyPI。

## 📦 包列表

### er-django

Django 集成插件，用于将 Django models 转换为 ER 图和 ER 迁移。

**目录**: `packages/er-django/`

**安装**:
```bash
# 开发模式
uv pip install -e packages/er-django/

# 从 PyPI（未来）
uv pip install x007007007-er-django
```

**文档**:
- [README.md](er-django/README.md) - 用户文档
- [INSTALL.md](er-django/INSTALL.md) - 安装指南
- [DESIGN.md](er-django/src/x007007007/er_django/DESIGN.md) - 设计文档

**依赖**:
- x007007007-er (核心包)
- django>=4.2.0

## 🏗️ 包结构

每个包都遵循标准的 Python 包结构：

```
packages/
└── er-django/
    ├── pyproject.toml      # 包配置
    ├── README.md           # 用户文档
    ├── INSTALL.md          # 安装指南
    ├── .gitignore
    ├── src/
    │   └── x007007007/
    │       └── er_django/  # 源代码
    └── tests/              # 测试
```

## 🚀 开发工作流

### 1. 开发新包

```bash
# 1. 创建包目录
mkdir -p packages/new-package/src/x007007007

# 2. 创建 pyproject.toml
# 3. 实现功能
# 4. 添加测试
# 5. 编写文档
```

### 2. 本地测试

```bash
# 安装包（开发模式）
uv pip install -e packages/er-django/

# 运行测试
cd packages/er-django
pytest tests/
```

### 3. 构建和发布

```bash
cd packages/er-django

# 构建
^uv run python -m build

# 发布到 Test PyPI
twine upload --repository testpypi dist/*

# 发布到 PyPI
twine upload dist/*
```

## 📋 添加新包的步骤

1. **创建目录结构**
   ```bash
   mkdir -p packages/new-package/src/x007007007
   mkdir -p packages/new-package/tests
   ```

2. **创建 pyproject.toml**
   ```toml
   [project]
   name = "x007007007-new-package"
   version = "0.1.0"
   dependencies = [
       "x007007007-er>=0.1.0",
   ]
   ```

3. **实现功能**
   - 在 `src/x007007007/new_package/` 中编写代码
   - 遵循项目的代码规范

4. **添加测试**
   - 在 `tests/` 中添加测试
   - 确保测试覆盖率 > 80%

5. **编写文档**
   - README.md - 用户文档
   - INSTALL.md - 安装指南
   - DESIGN.md - 设计文档（可选）

6. **更新此文档**
   - 在上面的"包列表"中添加新包

## 🔗 包之间的依赖

```
x007007007-er (核心包)
    ↑
    └── x007007007-er-django (Django 插件)
    └── x007007007-er-xxx (未来的其他插件)
```

## 📝 命名规范

- **包名**: `x007007007-er-{feature}`
- **模块名**: `x007007007.er_{feature}`
- **PyPI 名**: `x007007007-er-{feature}`

例如:
- 包名: `er-django`
- 模块名: `x007007007.er_django`
- PyPI 名: `x007007007-er-django`

## 🧪 测试策略

每个包都应该有自己的测试：

```bash
# 运行单个包的测试
cd packages/er-django
pytest tests/

# 运行所有包的测试
pytest packages/*/tests/
```

## 📦 发布策略

### 独立版本

每个包可以有自己的版本号：
- 核心包: `x007007007-er==0.2.0`
- Django 插件: `x007007007-er-django==0.1.5`

### 版本兼容性

在 `pyproject.toml` 中指定依赖版本：
```toml
dependencies = [
    "x007007007-er>=0.1.0,<0.3.0",  # 兼容 0.1.x 和 0.2.x
]
```

## 🔄 更新流程

1. **更新核心包**
   ```bash
   cd .  # 项目根目录
   # 更新代码
   # 更新版本号
   # 发布
   ```

2. **更新插件包**
   ```bash
   cd packages/er-django
   # 更新代码
   # 更新版本号
   # 测试兼容性
   # 发布
   ```

## 📚 相关文档

- [主项目 README](../README.md)
- [ER Django 文档](er-django/README.md)
- [示例项目](../examples/django_blog/README.md)

## 🤝 贡献

欢迎贡献新的包！请遵循：
1. 创建新的包目录
2. 遵循命名规范
3. 添加完整的测试
4. 编写清晰的文档
5. 提交 PR

## 📄 许可证

所有包都使用 MIT License
