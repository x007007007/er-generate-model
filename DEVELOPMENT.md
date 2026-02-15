# 开发指南

本文档提供 ER Diagram Converter monorepo 的详细开发指南，包括工作区设置、常见开发工作流程、包管理和故障排除。

## 目录

- [工作区设置](#工作区设置)
- [常见开发工作流程](#常见开发工作流程)
- [添加新包](#添加新包)
- [内部依赖管理](#内部依赖管理)
- [故障排除](#故障排除)

## 工作区设置

### 前提条件

- Python 3.8+
- uv 包管理器
- Java 11+（用于 ANTLR 解析器生成）

### 初始设置

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd ER
   ```

2. **安装 uv**（如果尚未安装）：
   ```bash
   pip install uv
   ```

3. **安装所有包和依赖**：
   ```bash
   uv sync
   ```
   
   这个命令会：
   - 安装所有 workspace 包（editable 模式）
   - 解析并安装所有外部依赖
   - 正确处理内部包依赖关系
   - 安装开发工具（pytest、pytest-cov、hypothesis）
   - 使所有 CLI 命令可用

4. **生成 ANTLR 解析器**：
   
   **Windows**：
   ```bash
   tools\generate_antlr.bat
   ```
   
   **Linux/Mac**：
   ```bash
   chmod +x tools/generate_antlr.sh
   ./tools/generate_antlr.sh
   ```

5. **验证安装**：
   ```bash
   # 检查 CLI 命令是否可用
   er-gen-tool --help
   
   # 运行测试
   uv run pytest
   ```

### 工作区结构说明

```
ER/
├── pyproject.toml              # 工作区根配置（无 [project] 表）
├── uv.lock                     # 统一的依赖锁文件
├── .venv/                      # 共享虚拟环境
├── packages/                   # 所有包的目录
│   ├── er-gen-core/           # 核心库
│   │   ├── pyproject.toml     # 包配置（有 [project] 表）
│   │   ├── src/               # 源代码
│   │   └── tests/             # 测试
│   ├── er-gen-tool/           # CLI 工具（依赖 er-gen-core）
│   ├── er-gen-mcp/            # MCP 服务器
│   ├── er-gen-tool-ai/        # AI 工具（依赖 er-gen-core）
│   └── er-django/             # Django 集成
├── examples/                   # 示例文件
└── tools/                      # 开发工具脚本
```

**关键点**：
- 根 `pyproject.toml` 只包含工作区配置，没有 `[project]` 表
- 每个包都有自己的 `pyproject.toml`，包含完整的包元数据
- 所有包共享一个虚拟环境（`.venv/`）
- 单一锁文件（`uv.lock`）确保依赖版本一致

## 常见开发工作流程

### 日常开发

1. **激活虚拟环境**（可选，uv 会自动处理）：
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **进行代码更改**：
   - 所有包都以 editable 模式安装
   - 代码更改立即生效，无需重新安装
   - 依赖包的更改也会立即反映到依赖它的包中

3. **运行测试**：
   ```bash
   # 运行所有测试
   uv run pytest
   
   # 运行特定包的测试
   uv run pytest packages/er-gen-core/tests/
   
   # 运行特定测试文件
   uv run pytest packages/er-gen-core/tests/test_models.py
   
   # 运行特定测试函数
   uv run pytest packages/er-gen-core/tests/test_models.py::test_entity_creation
   ```

4. **检查代码覆盖率**：
   ```bash
   # 生成覆盖率报告
   uv run pytest --cov
   
   # 生成 HTML 覆盖率报告
   uv run pytest --cov --cov-report=html
   # 在浏览器中打开 htmlcov/index.html
   ```

### 添加或更新依赖

#### 添加外部依赖到特定包

```bash
# 添加依赖到特定包
uv add --package er-gen-tool click>=8.1.0

# 添加开发依赖到特定包
uv add --package er-gen-tool --dev black
```

#### 添加工作区级别的开发依赖

编辑根 `pyproject.toml` 的 `[dependency-groups]` 部分：

```toml
[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "hypothesis>=6.0.0",
    "black>=23.0.0",  # 新增
]
```

然后运行：
```bash
uv sync
```

#### 更新依赖

```bash
# 更新所有依赖
uv lock --upgrade

# 更新特定依赖
uv lock --upgrade-package click

# 同步更新后的依赖
uv sync
```

### 构建和发布包

#### 构建单个包

```bash
# 进入包目录
cd packages/er-gen-core

# 构建包
python -m build

# 生成的文件在 dist/ 目录
# - dist/x007007007_er_gen_core-0.3.0-py3-none-any.whl
# - dist/x007007007_er_gen_core-0.3.0.tar.gz
```

#### 发布到 PyPI

```bash
# 安装 twine（如果尚未安装）
pip install twine

# 上传到 PyPI
twine upload dist/*

# 上传到 TestPyPI（测试）
twine upload --repository testpypi dist/*
```

### 测试 CLI 命令

```bash
# 测试 er-gen-tool 命令
er-gen-tool convert convert examples/input-to-toml/mermaid-to-toml/01-simple-blog/input.mmd

# 测试 AI 工具
er-gen-tool ai-assist generate "设计一个博客系统" -o test-output.toml

# 测试 MCP 服务器
er-mcp
```

## 添加新包

### 步骤 1：创建包目录结构

```bash
# 创建包目录
mkdir -p packages/my-new-package/src/x007007007/my_new_package
mkdir -p packages/my-new-package/tests

# 创建 __init__.py 文件
touch packages/my-new-package/src/x007007007/__init__.py
touch packages/my-new-package/src/x007007007/my_new_package/__init__.py
touch packages/my-new-package/tests/__init__.py
```

### 步骤 2：创建 pyproject.toml

在 `packages/my-new-package/pyproject.toml` 中：

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "x007007007-my-new-package"
version = "0.1.0"
description = "My new package description"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    # 外部依赖
    "click>=8.1.0",
    
    # 内部依赖（如果需要）
    "x007007007-er-gen-core>=0.3.0",
]

[project.scripts]
# CLI 命令（如果需要）
my-command = "x007007007.my_new_package.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

### 步骤 3：验证工作区识别新包

```bash
# uv 会自动识别新包（因为使用了 packages/* 模式）
uv sync

# 验证包已安装
uv pip list | grep my-new-package
```

### 步骤 4：添加测试

在 `packages/my-new-package/tests/test_basic.py` 中：

```python
def test_import():
    """Test that the package can be imported."""
    import x007007007.my_new_package
    assert x007007007.my_new_package is not None
```

运行测试：
```bash
uv run pytest packages/my-new-package/tests/
```

### 步骤 5：创建 README.md

在 `packages/my-new-package/README.md` 中：

```markdown
# My New Package

Package description here.

## Installation

### From PyPI
\`\`\`bash
pip install x007007007-my-new-package
\`\`\`

### From Source (Development)
\`\`\`bash
# From workspace root
uv sync
\`\`\`

## Usage

\`\`\`python
from x007007007.my_new_package import something
\`\`\`
```

## 内部依赖管理

### 理解内部依赖

内部依赖是指 monorepo 中一个包依赖另一个包的情况。例如：
- `er-gen-tool` 依赖 `er-gen-core`
- `er-gen-tool-ai` 依赖 `er-gen-core`

### 声明内部依赖

在包的 `pyproject.toml` 中，使用发布的包名称：

```toml
[project]
name = "x007007007-er-gen-tool"
dependencies = [
    "x007007007-er-gen-core>=0.3.0",  # 内部依赖
    "click>=8.1.0",                    # 外部依赖
]
```

### 内部依赖的工作原理

1. **开发模式**（在工作区中）：
   - `uv sync` 识别 `x007007007-er-gen-core` 是工作区成员
   - 以 editable 模式从本地安装（`packages/er-gen-core/`）
   - 对 `er-gen-core` 的更改立即反映到 `er-gen-tool` 中

2. **生产模式**（从 PyPI 安装）：
   - `pip install x007007007-er-gen-tool` 从 PyPI 获取依赖
   - 安装发布的 `x007007007-er-gen-core` 版本
   - 包独立工作，不需要工作区

### 版本约束最佳实践

```toml
# ✅ 推荐：使用 >= 允许补丁更新
"x007007007-er-gen-core>=0.3.0"

# ✅ 可以：锁定主版本
"x007007007-er-gen-core>=0.3.0,<0.4.0"

# ⚠️ 谨慎：精确版本可能过于严格
"x007007007-er-gen-core==0.3.0"

# ❌ 避免：过于宽松的约束
"x007007007-er-gen-core"
```

### 验证内部依赖

```bash
# 检查包是否以 editable 模式安装
uv pip list | grep x007007007

# 应该看到类似：
# x007007007-er-gen-core    0.3.0  /path/to/ER/packages/er-gen-core/src
# x007007007-er-gen-tool    0.3.0  /path/to/ER/packages/er-gen-tool/src
```

### 测试内部依赖

创建测试验证依赖正确解析：

```python
# packages/er-gen-tool/tests/test_dependencies.py
def test_can_import_core():
    """Test that er-gen-tool can import er-gen-core."""
    from x007007007.er_core.models import ERModel
    assert ERModel is not None

def test_core_is_editable():
    """Test that er-gen-core is installed in editable mode."""
    import x007007007.er_core
    import os
    
    # 在开发模式下，模块路径应该指向工作区
    module_path = x007007007.er_core.__file__
    assert "packages/er-gen-core" in module_path
```

## 故障排除

### 配置错误详解

本节详细说明 uv 工作区配置中最常见的三种配置错误，这些错误会导致工作区无法正常工作。

#### 错误 1：缺少工作区声明

**错误描述**：
这是最常见的配置错误。当根 `pyproject.toml` 文件缺少 `[tool.uv.workspace]` 部分时，uv 无法识别这是一个工作区项目，也无法发现和管理包成员。

**症状**：
```
error: No workspace members found
```
或
```
error: No `project` table found in workspace root
```

**原因**：
- 根 `pyproject.toml` 完全缺少 `[tool.uv.workspace]` 部分
- `[tool.uv.workspace]` 部分存在但 `members` 字段为空或未定义
- 工作区成员路径模式不正确（例如使用了错误的 glob 模式）

**正确的配置示例**：
```toml
# 根 pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]  # 使用 glob 模式包含所有包

# 或者显式列出每个包
[tool.uv.workspace]
members = [
    "packages/er-gen-core",
    "packages/er-gen-tool",
    "packages/er-gen-mcp",
    "packages/er-gen-tool-ai",
    "packages/er-django",
]
```

**错误的配置示例**：
```toml
# ❌ 错误：完全缺少工作区声明
[tool.uv]
index-url = "https://mirrors.aliyun.com/pypi/simple/"
# 缺少 [tool.uv.workspace] 部分

# ❌ 错误：members 为空
[tool.uv.workspace]
members = []

# ❌ 错误：错误的 glob 模式（缺少递归通配符）
[tool.uv.workspace]
members = ["packages"]  # 应该是 "packages/*"
```

**解决方案**：
1. 在根 `pyproject.toml` 中添加 `[tool.uv.workspace]` 部分
2. 使用 `members` 字段声明所有包的位置
3. 推荐使用 glob 模式 `packages/*` 以自动包含新包
4. 验证配置：
   ```bash
   uv sync  # 应该成功识别所有包
   ```

**验证工作区配置**：
```bash
# 检查 uv 是否识别工作区成员
uv tree

# 应该看到所有包列出
# 如果只看到根项目或错误，说明配置有问题
```

#### 错误 2：包结构无效

**错误描述**：
当工作区成员路径指向的目录不包含有效的 Python 包配置时，uv 无法将其作为包进行管理。每个包必须有自己的 `pyproject.toml` 文件，并且必须包含 `[project]` 表。

**症状**：
```
error: Package 'packages/my-package' does not have a pyproject.toml
```
或
```
error: Package 'packages/my-package' is missing [project] table
```
或
```
error: Invalid package structure in 'packages/my-package'
```

**原因**：
- 包目录缺少 `pyproject.toml` 文件
- 包的 `pyproject.toml` 缺少必需的 `[project]` 表
- 包的 `[project]` 表缺少必需字段（如 `name` 或 `version`）
- 包目录结构不符合 Python 包标准

**正确的包结构**：
```
packages/my-package/
├── pyproject.toml          # 必需：包配置文件
├── README.md               # 推荐：包文档
├── src/                    # 推荐：源代码目录
│   └── x007007007/
│       └── my_package/
│           ├── __init__.py
│           └── module.py
└── tests/                  # 推荐：测试目录
    ├── __init__.py
    └── test_module.py
```

**正确的 pyproject.toml 配置**：
```toml
# packages/my-package/pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "x007007007-my-package"      # 必需：包名称
version = "0.1.0"                    # 必需：版本号
description = "Package description"  # 推荐：描述
requires-python = ">=3.8"           # 推荐：Python 版本要求
dependencies = []                    # 可选：依赖列表

[tool.setuptools.packages.find]
where = ["src"]
```

**错误的包结构示例**：
```
# ❌ 错误 1：缺少 pyproject.toml
packages/my-package/
├── src/
│   └── my_package/
│       └── __init__.py
└── tests/
    └── test_module.py

# ❌ 错误 2：pyproject.toml 缺少 [project] 表
packages/my-package/
├── pyproject.toml  # 只有 [build-system]，没有 [project]
└── src/

# ❌ 错误 3：[project] 表缺少必需字段
packages/my-package/
├── pyproject.toml
    [project]
    # 缺少 name 和 version
    description = "My package"
└── src/
```

**解决方案**：
1. 确保每个包目录都有 `pyproject.toml` 文件
2. 确保每个包的 `pyproject.toml` 包含完整的 `[project]` 表
3. 验证 `[project]` 表包含所有必需字段：
   - `name`：包的唯一名称
   - `version`：包的版本号
4. 使用标准的包目录结构（推荐使用 `src` 布局）
5. 验证包配置：
   ```bash
   # 尝试同步工作区
   uv sync
   
   # 检查包是否被识别
   uv pip list | grep my-package
   ```

**创建新包的模板**：
```bash
# 创建包目录结构
mkdir -p packages/my-package/src/x007007007/my_package
mkdir -p packages/my-package/tests

# 创建必需的文件
touch packages/my-package/pyproject.toml
touch packages/my-package/README.md
touch packages/my-package/src/x007007007/__init__.py
touch packages/my-package/src/x007007007/my_package/__init__.py
touch packages/my-package/tests/__init__.py

# 编辑 pyproject.toml 添加必需的配置
```

#### 错误 3：根项目表冲突

**错误描述**：
在 uv 工作区中，根 `pyproject.toml` 不应该包含 `[project]` 表。根配置文件的作用是声明工作区成员和共享配置，而不是定义一个可安装的包。如果根文件包含 `[project]` 表，会与工作区配置产生冲突。

**症状**：
```
error: Workspace root cannot have [project] table
```
或
```
error: Found both [tool.uv.workspace] and [project] in root pyproject.toml
```
或工作区行为异常，例如：
- 包依赖解析错误
- 内部依赖无法正确识别
- `uv sync` 尝试将根目录作为包安装

**原因**：
- 根 `pyproject.toml` 同时包含 `[tool.uv.workspace]` 和 `[project]` 表
- 将单包项目转换为工作区时未删除根 `[project]` 表
- 误解了工作区配置的结构

**正确的根配置**：
```toml
# 根 pyproject.toml - 仅包含工作区配置
[tool.uv.workspace]
members = ["packages/*"]

[tool.uv]
index-url = "https://mirrors.aliyun.com/pypi/simple/"

[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "hypothesis>=6.0.0",
]

[tool.pytest.ini_options]
testpaths = ["packages/*/tests"]

[tool.coverage.run]
source = ["packages/*/src"]

# ✅ 注意：没有 [project] 表
```

**错误的根配置**：
```toml
# ❌ 错误：根文件包含 [project] 表
[tool.uv.workspace]
members = ["packages/*"]

[project]  # ❌ 这不应该在根文件中
name = "my-monorepo"
version = "1.0.0"
dependencies = []

[tool.uv]
index-url = "https://mirrors.aliyun.com/pypi/simple/"
```

**解决方案**：
1. 从根 `pyproject.toml` 中删除整个 `[project]` 部分
2. 如果需要根级别的可安装包，将其移到 `packages/` 目录下作为独立包
3. 保留工作区配置部分：
   - `[tool.uv.workspace]`：工作区成员声明
   - `[tool.uv]`：uv 设置（如索引 URL）
   - `[dependency-groups]`：共享开发依赖
   - `[tool.pytest.ini_options]`：测试配置
   - `[tool.coverage.run]`：覆盖率配置
4. 验证配置：
   ```bash
   uv sync  # 应该成功且不会尝试安装根项目
   ```

**配置层次说明**：
```
工作区配置层次：
├── 根 pyproject.toml
│   ├── [tool.uv.workspace]      # 工作区声明
│   ├── [tool.uv]                # uv 设置
│   ├── [dependency-groups]      # 共享开发依赖
│   └── [tool.*]                 # 工具配置（pytest、coverage 等）
│   └── ❌ 不应有 [project]
│
└── packages/*/pyproject.toml
    ├── [build-system]           # 构建配置
    ├── [project]                # ✅ 包元数据（必需）
    │   ├── name                 # 包名称
    │   ├── version              # 版本号
    │   └── dependencies         # 包依赖
    └── [tool.*]                 # 包特定的工具配置
```

**迁移指南**：
如果你有一个包含 `[project]` 表的根文件，需要迁移到工作区结构：

```bash
# 1. 备份当前配置
cp pyproject.toml pyproject.toml.backup

# 2. 创建新的包目录（如果根项目需要保留为包）
mkdir -p packages/root-package
cp pyproject.toml packages/root-package/
cp -r src packages/root-package/
cp -r tests packages/root-package/

# 3. 更新根 pyproject.toml，删除 [project] 表，添加工作区配置
# 编辑 pyproject.toml，删除 [project] 部分，添加：
# [tool.uv.workspace]
# members = ["packages/*"]

# 4. 验证配置
uv sync
```

**验证工作区配置正确性**：
```bash
# 检查根文件不包含 [project] 表
grep -A 5 "\[project\]" pyproject.toml
# 应该没有输出（或只在注释中出现）

# 检查工作区成员
uv tree

# 验证所有包都被识别
uv pip list | grep x007007007

# 运行测试确保一切正常
uv run pytest
```

### 依赖解析错误详解

本节详细说明在 uv 工作区中进行依赖解析时可能遇到的三种主要错误类型。这些错误通常发生在包之间存在内部依赖关系时。

#### 错误 1：版本不匹配

**错误描述**：
当一个包声明的内部依赖版本约束与工作区中实际包的版本不匹配时，uv 会拒绝安装并报告版本冲突。这是一种保护机制，确保依赖关系的一致性。

**症状**：
```
error: Package 'x007007007-er-gen-tool' requires 'x007007007-er-gen-core>=0.4.0' but workspace has version 0.3.0
```
或
```
error: Version constraint not satisfied: x007007007-er-gen-core 0.3.0 does not match >=0.4.0
```
或在运行时出现兼容性问题：
```
AttributeError: module 'x007007007.er_core' has no attribute 'new_feature'
```

**原因**：
- 依赖包（如 `er-gen-tool`）的 `pyproject.toml` 中声明的版本约束过于严格
- 被依赖包（如 `er-gen-core`）的版本号未及时更新
- 在不同分支或提交之间版本号不同步
- 包的 API 发生了破坏性更改但版本号未正确递增

**示例场景**：
```toml
# packages/er-gen-core/pyproject.toml
[project]
name = "x007007007-er-gen-core"
version = "0.3.0"  # 当前版本

# packages/er-gen-tool/pyproject.toml
[project]
name = "x007007007-er-gen-tool"
dependencies = [
    "x007007007-er-gen-core>=0.4.0",  # ❌ 要求 0.4.0 但工作区只有 0.3.0
]
```

**解决方案**：

**方案 1：更新被依赖包的版本**（推荐用于新功能）
```toml
# packages/er-gen-core/pyproject.toml
[project]
name = "x007007007-er-gen-core"
version = "0.4.0"  # ✅ 更新版本以满足约束
```

然后重新同步：
```bash
uv lock
uv sync
```

**方案 2：放宽版本约束**（推荐用于开发阶段）
```toml
# packages/er-gen-tool/pyproject.toml
[project]
dependencies = [
    "x007007007-er-gen-core>=0.3.0",  # ✅ 放宽约束以匹配当前版本
]
```

**方案 3：使用兼容版本约束**（推荐用于生产）
```toml
# packages/er-gen-tool/pyproject.toml
[project]
dependencies = [
    "x007007007-er-gen-core>=0.3.0,<0.4.0",  # ✅ 允许补丁版本更新
]
```

**版本约束最佳实践**：
```toml
# ✅ 推荐：允许补丁和次要版本更新
"x007007007-er-gen-core>=0.3.0,<1.0.0"

# ✅ 适用于稳定 API：允许补丁更新
"x007007007-er-gen-core>=0.3.0,<0.4.0"

# ⚠️ 谨慎使用：精确版本（过于严格）
"x007007007-er-gen-core==0.3.0"

# ⚠️ 开发阶段：宽松约束（允许任何版本）
"x007007007-er-gen-core>=0.3.0"

# ❌ 避免：无版本约束（可能导致不兼容）
"x007007007-er-gen-core"
```

**验证版本兼容性**：
```bash
# 检查所有包的版本
uv pip list | grep x007007007

# 查看依赖树和版本约束
uv tree

# 验证特定包的依赖
uv pip show x007007007-er-gen-tool
```

**预防措施**：
1. 使用语义化版本控制（SemVer）
2. 在 API 发生破坏性更改时递增主版本号
3. 在添加新功能时递增次要版本号
4. 在修复 bug 时递增补丁版本号
5. 在 CHANGELOG.md 中记录版本更改和兼容性说明

#### 错误 2：循环依赖

**错误描述**：
循环依赖是指两个或多个包相互依赖，形成一个依赖环。例如，包 A 依赖包 B，而包 B 又依赖包 A。这种情况会导致依赖解析失败，因为无法确定安装顺序。

**症状**：
```
error: Circular dependency detected: x007007007-er-gen-tool → x007007007-er-gen-core → x007007007-er-gen-tool
```
或
```
error: Dependency cycle found: A → B → C → A
```
或在导入时出现错误：
```
ImportError: cannot import name 'X' from partially initialized module 'Y' (most likely due to a circular import)
```

**原因**：
- 包 A 的 `pyproject.toml` 中声明依赖包 B
- 包 B 的 `pyproject.toml` 中声明依赖包 A
- 更复杂的情况：A → B → C → A（多包循环）
- 代码层面的循环导入（即使依赖声明正确）

**示例场景**：
```toml
# packages/er-gen-tool/pyproject.toml
[project]
name = "x007007007-er-gen-tool"
dependencies = [
    "x007007007-er-gen-core>=0.3.0",  # er-gen-tool 依赖 er-gen-core
]

# packages/er-gen-core/pyproject.toml
[project]
name = "x007007007-er-gen-core"
dependencies = [
    "x007007007-er-gen-tool>=0.3.0",  # ❌ er-gen-core 也依赖 er-gen-tool！
]
```

**诊断循环依赖**：
```bash
# 查看完整的依赖树
uv tree

# 检查特定包的依赖
uv pip show x007007007-er-gen-tool
uv pip show x007007007-er-gen-core

# 使用 Python 检测导入循环
python -c "import x007007007.er_tool; import x007007007.er_core"
```

**解决方案**：

**方案 1：提取共享代码到新包**（最佳实践）

将 A 和 B 都需要的代码提取到新的包 C 中：
```
原始结构：
A ⟷ B（循环依赖）

重构后：
A → C
B → C
（C 不依赖 A 或 B）
```

实施步骤：
```bash
# 1. 创建新的共享包
mkdir -p packages/er-gen-common/src/x007007007/er_common
touch packages/er-gen-common/pyproject.toml

# 2. 将共享代码移到新包
# 将 A 和 B 共同使用的代码移到 er-gen-common

# 3. 更新依赖关系
```

```toml
# packages/er-gen-common/pyproject.toml
[project]
name = "x007007007-er-gen-common"
version = "0.1.0"
dependencies = []  # 不依赖其他内部包

# packages/er-gen-tool/pyproject.toml
[project]
dependencies = [
    "x007007007-er-gen-common>=0.1.0",  # ✅ 依赖共享包
]

# packages/er-gen-core/pyproject.toml
[project]
dependencies = [
    "x007007007-er-gen-common>=0.1.0",  # ✅ 依赖共享包
]
```

**方案 2：重新设计包边界**

重新思考包的职责，确保依赖关系是单向的：
```
原始设计：
er-gen-tool（CLI 工具）⟷ er-gen-core（核心库）

重构后：
er-gen-tool（CLI 工具）→ er-gen-core（核心库）
（CLI 工具依赖核心库，但核心库不依赖 CLI 工具）
```

**方案 3：使用依赖注入**

通过依赖注入打破循环依赖：
```python
# 在 er-gen-core 中，不直接导入 er-gen-tool
# 而是接受一个可调用对象作为参数

# packages/er-gen-core/src/x007007007/er_core/processor.py
from typing import Callable, Any

class Processor:
    def __init__(self, tool_callback: Callable[[Any], Any] = None):
        self.tool_callback = tool_callback
    
    def process(self, data: Any) -> Any:
        # 使用注入的回调而不是直接导入
        if self.tool_callback:
            return self.tool_callback(data)
        return data

# packages/er-gen-tool/src/x007007007/er_tool/cli.py
from x007007007.er_core.processor import Processor

def my_tool_function(data):
    return f"Processed: {data}"

# 注入依赖
processor = Processor(tool_callback=my_tool_function)
```

**方案 4：使用可选依赖**

如果依赖不是必需的，可以将其设为可选：
```toml
# packages/er-gen-core/pyproject.toml
[project]
name = "x007007007-er-gen-core"
dependencies = []  # 核心依赖不包含 er-gen-tool

[project.optional-dependencies]
cli = ["x007007007-er-gen-tool>=0.3.0"]  # 可选的 CLI 功能
```

**预防循环依赖的最佳实践**：
1. **分层架构**：建立清晰的依赖层次
   ```
   表示层（CLI、Web）
        ↓
   应用层（业务逻辑）
        ↓
   领域层（核心模型）
        ↓
   基础设施层（工具、数据库）
   ```

2. **依赖方向规则**：
   - 高层模块可以依赖低层模块
   - 低层模块不应依赖高层模块
   - 同层模块之间避免相互依赖

3. **定期检查依赖树**：
   ```bash
   uv tree | grep -A 5 "x007007007"
   ```

4. **代码审查**：在添加新依赖时检查是否会引入循环

#### 错误 3：缺少内部依赖

**错误描述**：
当一个包声明依赖另一个内部包，但该包未在工作区中声明为成员时，uv 会尝试从外部包索引（如 PyPI）安装该依赖。如果外部索引中不存在该包或版本不匹配，安装将失败。

**症状**：
```
error: Package 'x007007007-er-gen-helper' not found in workspace or package index
```
或
```
error: Could not find a version that satisfies the requirement x007007007-er-gen-helper>=0.1.0
```
或
```
warning: Package 'x007007007-er-gen-helper' is not a workspace member, attempting to install from index
```
或在运行时：
```
ModuleNotFoundError: No module named 'x007007007.er_helper'
```

**原因**：
- 包 A 的 `dependencies` 中声明了包 B，但包 B 不在工作区的 `members` 列表中
- 包 B 的目录存在但未被工作区配置识别
- 包 B 的名称在 `pyproject.toml` 中拼写错误
- 包 B 尚未创建但已在依赖中声明

**示例场景**：
```toml
# 根 pyproject.toml
[tool.uv.workspace]
members = [
    "packages/er-gen-core",
    "packages/er-gen-tool",
    # ❌ 缺少 packages/er-gen-helper
]

# packages/er-gen-tool/pyproject.toml
[project]
name = "x007007007-er-gen-tool"
dependencies = [
    "x007007007-er-gen-core>=0.3.0",
    "x007007007-er-gen-helper>=0.1.0",  # ❌ 依赖未在工作区中声明的包
]
```

**诊断缺少的依赖**：
```bash
# 检查工作区成员
uv tree

# 列出所有包目录
ls -la packages/

# 检查特定包是否存在
ls -la packages/er-gen-helper/

# 验证包的 pyproject.toml
cat packages/er-gen-helper/pyproject.toml | grep "name ="
```

**解决方案**：

**方案 1：将包添加到工作区成员**（最常见）

如果包已存在但未在工作区中声明：
```toml
# 根 pyproject.toml
[tool.uv.workspace]
members = [
    "packages/er-gen-core",
    "packages/er-gen-tool",
    "packages/er-gen-helper",  # ✅ 添加缺少的包
]

# 或使用 glob 模式自动包含所有包
[tool.uv.workspace]
members = ["packages/*"]  # ✅ 推荐：自动包含所有包
```

然后重新同步：
```bash
uv sync
```

**方案 2：创建缺少的包**

如果包尚不存在，需要创建它：
```bash
# 创建包目录结构
mkdir -p packages/er-gen-helper/src/x007007007/er_helper
mkdir -p packages/er-gen-helper/tests

# 创建 __init__.py 文件
touch packages/er-gen-helper/src/x007007007/__init__.py
touch packages/er-gen-helper/src/x007007007/er_helper/__init__.py
touch packages/er-gen-helper/tests/__init__.py

# 创建 pyproject.toml
cat > packages/er-gen-helper/pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "x007007007-er-gen-helper"
version = "0.1.0"
description = "Helper utilities for ER Diagram Converter"
requires-python = ">=3.8"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

# 创建 README.md
cat > packages/er-gen-helper/README.md << 'EOF'
# ER Gen Helper

Helper utilities for ER Diagram Converter.
EOF

# 同步工作区
uv sync
```

**方案 3：修正包名称拼写错误**

如果是名称拼写错误：
```bash
# 检查实际的包名称
cat packages/er-gen-helper/pyproject.toml | grep "name ="

# 输出：name = "x007007007-er-gen-helper"

# 确保依赖声明中的名称完全匹配
```

```toml
# packages/er-gen-tool/pyproject.toml
[project]
dependencies = [
    "x007007007-er-gen-helper>=0.1.0",  # ✅ 确保名称完全匹配
]
```

**方案 4：改为外部依赖**

如果该包实际上应该是外部依赖（从 PyPI 安装）：
```toml
# packages/er-gen-tool/pyproject.toml
[project]
dependencies = [
    "some-external-package>=1.0.0",  # ✅ 外部依赖
]
```

**验证内部依赖正确配置**：
```bash
# 1. 检查工作区成员
uv tree

# 2. 验证所有内部依赖都已安装
uv pip list | grep x007007007

# 3. 检查包是否以 editable 模式安装
uv pip show x007007007-er-gen-helper
# 应该显示：Location: /path/to/ER/packages/er-gen-helper/src

# 4. 测试导入
python -c "import x007007007.er_helper; print('Success')"

# 5. 运行测试确保依赖正常工作
uv run pytest packages/er-gen-tool/tests/
```

**预防缺少依赖的最佳实践**：

1. **使用 glob 模式**：
   ```toml
   [tool.uv.workspace]
   members = ["packages/*"]  # 自动包含所有包
   ```

2. **在添加依赖前创建包**：
   - 先创建包的基本结构
   - 然后在其他包中声明依赖
   - 最后实现包的功能

3. **使用一致的命名约定**：
   ```
   目录名：packages/er-gen-helper/
   包名：x007007007-er-gen-helper
   模块名：x007007007.er_helper
   ```

4. **定期验证工作区配置**：
   ```bash
   # 创建验证脚本
   cat > verify_workspace.sh << 'EOF'
   #!/bin/bash
   echo "Checking workspace members..."
   uv tree
   
   echo -e "\nChecking installed packages..."
   uv pip list | grep x007007007
   
   echo -e "\nChecking for missing dependencies..."
   for pkg in packages/*/pyproject.toml; do
       echo "Checking $pkg"
       grep "x007007007-" "$pkg" || true
   done
   EOF
   
   chmod +x verify_workspace.sh
   ./verify_workspace.sh
   ```

5. **文档化包依赖关系**：
   在 README.md 或 DEVELOPMENT.md 中维护依赖关系图：
   ```
   依赖关系：
   er-gen-tool → er-gen-core
   er-gen-tool-ai → er-gen-core
   er-gen-helper → er-gen-core
   ```

### 常见问题

#### 1. `uv sync` 失败：找不到工作区成员

**症状**：
```
error: No workspace members found
```

**原因**：根 `pyproject.toml` 缺少 `[tool.uv.workspace]` 部分。

**解决方案**：
参见上面的"错误 1：缺少工作区声明"部分。

#### 2. 包结构无效

**症状**：
```
error: Package 'packages/my-package' does not have a pyproject.toml
```

**原因**：包目录缺少 `pyproject.toml` 或 `[project]` 表。

**解决方案**：
参见上面的"错误 2：包结构无效"部分。

#### 3. 根项目表冲突

**症状**：
```
error: Workspace root cannot have [project] table
```

**原因**：根 `pyproject.toml` 包含 `[project]` 表。

**解决方案**：
参见上面的"错误 3：根项目表冲突"部分。

#### 4. 包未以 editable 模式安装

**症状**：代码更改不生效，需要重新安装。

**诊断**：
```bash
uv pip list | grep x007007007
# 如果没有显示路径，说明不是 editable 模式
```

**解决方案**：
```bash
# 重新同步工作区
uv sync

# 或手动以 editable 模式安装
uv pip install -e packages/package-name
```

#### 5. 内部依赖版本不匹配

**症状**：
```
error: Package A requires B>=0.4.0 but workspace has B==0.3.0
```

**解决方案**：
- 选项 1：更新工作区包版本以满足约束
- 选项 2：放宽依赖包中的版本约束

```toml
# 在依赖包的 pyproject.toml 中
dependencies = [
    "x007007007-er-gen-core>=0.3.0",  # 放宽约束
]
```

#### 6. 测试未被发现

**症状**：`pytest` 找不到某些包的测试。

**诊断**：
```bash
# 检查 pytest 配置
uv run pytest --collect-only
```

**解决方案**：
确保根 `pyproject.toml` 中的 testpaths 正确：
```toml
[tool.pytest.ini_options]
testpaths = ["packages/*/tests"]
```

#### 7. 覆盖率报告不包含所有包

**症状**：覆盖率报告缺少某些包的代码。

**解决方案**：
检查根 `pyproject.toml` 中的覆盖率配置：
```toml
[tool.coverage.run]
source = [
    "packages/er-gen-core/src",
    "packages/er-gen-tool/src",
    "packages/er-gen-mcp/src",
    "packages/er-gen-tool-ai/src",
    "packages/er-django/src",
    "packages/my-new-package/src",  # 添加新包
]
```

#### 8. CLI 命令不可用

**症状**：
```
command not found: er-gen-tool
```

**解决方案**：
```bash
# 确保包已安装
uv sync

# 使用 uv run 运行命令
uv run er-gen-tool --help

# 或激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
er-gen-tool --help
```

#### 9. ANTLR 解析器错误

**症状**：
```
ModuleNotFoundError: No module named 'x007007007.er_core.parsers.generated'
```

**原因**：ANTLR 解析器代码未生成。

**解决方案**：
```bash
# Windows
tools\generate_antlr.bat

# Linux/Mac
./tools/generate_antlr.sh
```

#### 10. 锁文件冲突

**症状**：
```
error: uv.lock is out of sync with pyproject.toml
```

**解决方案**：
```bash
# 重新生成锁文件
uv lock

# 同步依赖
uv sync
```

#### 11. 包索引不可达

**症状**：
```
error: Cannot reach package index at https://mirrors.aliyun.com/pypi/simple/
```

**解决方案**：
```bash
# 临时使用官方 PyPI
uv sync --index-url https://pypi.org/simple/

# 或更新根 pyproject.toml
[tool.uv]
index-url = "https://pypi.org/simple/"
```

#### 12. 循环依赖

**症状**：
```
error: Circular dependency detected: A → B → A
```

**解决方案**：
重构代码以打破循环依赖：
- 将共享代码提取到新包中
- 使用依赖注入
- 重新设计包边界

### 调试技巧

#### 查看已安装的包

```bash
# 列出所有已安装的包
uv pip list

# 查看特定包的信息
uv pip show x007007007-er-gen-core

# 检查包的依赖树
uv pip tree
```

#### 验证工作区配置

```bash
# 检查 uv 识别的工作区成员
uv tree

# 查看锁文件内容
cat uv.lock
```

#### 清理和重建

```bash
# 删除虚拟环境
rm -rf .venv

# 删除锁文件
rm uv.lock

# 重新安装
uv sync
```

#### 运行特定测试进行调试

```bash
# 运行单个测试并显示详细输出
uv run pytest packages/er-gen-core/tests/test_models.py::test_entity_creation -v

# 运行测试并在失败时进入调试器
uv run pytest --pdb

# 运行测试并显示打印输出
uv run pytest -s
```

### 获取帮助

如果遇到本指南未涵盖的问题：

1. 检查 [uv 文档](https://docs.astral.sh/uv/)
2. 查看项目的 GitHub Issues
3. 查看根目录的 README.md
4. 检查各个包的 README.md

## 最佳实践

### 代码质量

1. **运行测试**：提交前始终运行测试
   ```bash
   uv run pytest
   ```

2. **检查覆盖率**：保持高测试覆盖率
   ```bash
   uv run pytest --cov
   ```

3. **使用类型提示**：所有新代码应包含类型提示
   ```python
   def process_entity(entity: Entity) -> Dict[str, Any]:
       ...
   ```

4. **参数验证**：使用 assert 验证函数参数
   ```python
   def create_entity(name: str) -> Entity:
       assert isinstance(name, str), "name must be a string"
       assert len(name) > 0, "name cannot be empty"
       ...
   ```

### 依赖管理

1. **最小化依赖**：只添加真正需要的依赖
2. **固定主版本**：使用版本约束避免破坏性更改
3. **定期更新**：定期更新依赖以获取安全修复
4. **文档化依赖**：在 README 中说明为什么需要特定依赖

### 测试策略

1. **单元测试**：测试单个函数和类
2. **集成测试**：测试包之间的交互
3. **端到端测试**：测试完整的用户工作流程
4. **属性测试**：使用 hypothesis 进行基于属性的测试

### 文档

1. **代码注释**：为复杂逻辑添加注释
2. **文档字符串**：所有公共函数和类都应有文档字符串
3. **README**：每个包都应有清晰的 README
4. **更新日志**：在 CHANGELOG.md 中记录重要更改

## 相关资源

- [README.md](README.md) - 项目概述和快速开始
- [uv 文档](https://docs.astral.sh/uv/) - uv 包管理器文档
- [pytest 文档](https://docs.pytest.org/) - pytest 测试框架
- [hypothesis 文档](https://hypothesis.readthedocs.io/) - 基于属性的测试
