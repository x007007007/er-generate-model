# Changelog

本文档记录 ER Diagram Converter 项目的所有重要变更。

## [Unreleased]

### 修复 (Bug Fixes)

#### 测试兼容性修复
- 🐛 **修复测试文件与新Column/Entity API的兼容性**
  - 修复了 `packages/er-gen-tool/tests/test_cli_extended.py` 中的导入错误：将 `convert` 改为 `convert_cmd`
  - 批量更新了所有测试文件中的 `Column` 构造函数调用，添加必需的 `db_column` 参数
  - 批量更新了所有测试文件中的 `Entity` 构造函数调用，添加必需的 `table_name` 参数
  - 修复了自动化脚本错误添加 `table_name` 到 `Column` 的问题
  - 影响范围：
    - `packages/er-gen-tool/tests/test_er_migrate/` 下的所有测试文件
    - `packages/er-django/tests/` 下的部分测试文件
    - `packages/er-gen-core/tests/` 下的部分测试文件
  - 测试通过率从 658/790 (83%) 提升到 719/790 (91%)

## [0.3.0] - 2024-01-XX

### 重大变更 (Breaking Changes)

#### CLI 统一重构
- 🔄 **命令结构变更**：所有命令统一到 `er-gen-tool` 下
  - `er-convert` → `er-gen-tool convert`
  - `er-ai generate` → `er-gen-tool ai-assist generate`
  - `er-ai refine` → `er-gen-tool ai-assist refine`
  - `er-ai chat` → `er-gen-tool ai-assist chat`
  - `er-migrate makemigrations` → `er-gen-tool makemigration`
  - `er-migrate showmigrations` → `er-gen-tool migrate showmigrations`
  - `er-mcp` → `er-gen-mcp` (保持独立)

#### 包结构重组
- 📦 **多包架构**：项目拆分为4个独立包
  - `x007007007-er-gen-core`: 核心库（解析器、渲染器、转换器）
  - `x007007007-er-gen-tool`: 统一CLI工具
  - `x007007007-er-gen-tool-ai`: AI扩展插件（可选）
  - `x007007007-er-gen-mcp`: MCP服务器

#### 模块路径变更
- 🔄 **导入路径更新**：
  - AI模块：`x007007007.er_ai` → `x007007007.er_tool_ai`
  - 迁移模块：`x007007007.er_migrate` → `x007007007.er_tool.migrate`
  - 核心模块：`x007007007.er` (保持不变)

### 新增功能

#### 插件系统
- ✨ **Entry Points插件机制**：
  - AI功能作为可选插件，安装后自动注册
  - 插件安装后命令自动出现在CLI中
  - 支持第三方插件扩展

#### 安装选项
- 📦 **灵活的安装方式**：
  - 基础安装：`pip install x007007007-er-gen-tool`
  - 带AI功能：`pip install x007007007-er-gen-tool[ai]`
  - 独立安装AI插件：`pip install x007007007-er-gen-tool-ai`
  - MCP服务器：`pip install x007007007-er-gen-mcp`

### 改进

#### 代码组织
- 📁 **测试重组**：测试文件按包分类
  - `packages/er-gen-core/tests/`: 核心功能测试
  - `packages/er-gen-tool/tests/`: CLI和迁移测试
  - `packages/er-gen-tool-ai/tests/`: AI功能测试
  - `packages/er-gen-mcp/tests/`: MCP服务器测试

#### 文档更新
- 📚 **迁移指南**：新增 `MIGRATION.md` 详细说明迁移步骤
- 📚 **README更新**：更新所有文档中的命令示例
- 📚 **示例更新**：更新 examples/ 目录中的所有示例

### 依赖关系
- 🔗 **清晰的依赖图**：
  ```
  er-gen-core (核心库)
       ↑
       ├── er-gen-tool (CLI工具)
       ├── er-gen-tool-ai (AI插件)
       └── er-gen-mcp (MCP服务器)
  ```

### 迁移指南
详见 [MIGRATION.md](MIGRATION.md)

## [Unreleased]

### 已完成功能

#### Django字段db_column参数和路径分离 (field-db-column-and-path-separation)
- ✅ **db_column 参数支持**：完整支持 Django 字段的 db_column 参数
  - Column 模型扩展：添加 `db_column` 必需字段和 `database_column_name` 属性
  - Entity 模型扩展：添加 `table_name` 必需字段
  - DjangoModelParser 增强：从 Django 字段提取 db_column 参数
  - TOML 渲染器更新：仅在 db_column 与 name 不同时输出
  - 代码生成器更新：正确生成带 db_column 参数的 Django 代码
  - 测试覆盖：属性测试和单元测试完整覆盖

- ✅ **路径配置系统**：灵活的路径配置和分离功能
  - PathConfiguration 类：管理扫描路径、输出路径和三方包路径
  - 配置继承规则：scan_path → output_path → third_party_output_path
  - 相对路径解析：支持相对路径和绝对路径
  - 包名前缀：自动推导或自定义三方包前缀
  - 配置验证：完整的错误检查和描述性错误消息
  - 测试覆盖：13个属性测试验证配置正确性

- ✅ **三方包自动检测和分离**：智能识别和分离三方包
  - 自动检测：基于应用物理路径判断是否为三方包
  - er_export 命令：自动将三方包 TOML 输出到 `third/` 目录
  - er_convert 命令：自动发现并转换 `third/` 目录下的 TOML
  - AppDiscoveryService 增强：支持在 `third/` 子目录中查找 TOML
  - 路径查找策略：4种策略确保找到所有 TOML 文件
  - 测试覆盖：完整的三方包检测和路径解析测试

- ✅ **命令行接口增强**：
  - er_export 新增参数：`--output-dir`, `--third-party-output-dir`, `--third-party-prefix`
  - er_convert 新增参数：`--output-dir`, `--third-party-output-dir`, `--third-party-prefix`
  - 自动配置验证：启动时验证路径配置
  - 友好的错误消息：详细的配置错误提示

- ✅ **文档更新**：
  - README 重写：面向用户的功能介绍和使用指南
  - 三方包工作流程：完整的示例和目录结构说明
  - 配置选项说明：详细的参数说明和使用场景
  - 移除开发内容：开发相关内容移至独立文档

- ✅ **测试覆盖**：所有测试通过
  - 属性测试：17个属性测试验证通用正确性
  - 单元测试：完整的边缘情况和错误处理测试
  - 集成测试：端到端功能验证
  - 三方包测试：5个测试验证三方包检测和路径解析

#### Django ER Export 增强 (django-er-export-improvements)
- ✅ **table_name 字段支持**：Entity 模型新增 table_name 字段
  - DjangoModelParser 从 model._meta.db_table 提取表名
  - TOMLRenderer 输出 table_name 字段
  - TomlERParser 验证 table_name 必需字段
- ✅ **实体名称提取器**：新增 EntityNameExtractor 类
  - 支持正则表达式模式匹配
  - 灵活的实体名称过滤
- ✅ **er_export 命令增强**：
  - 新增 --output-dir 参数指定输出目录
  - 新增 --entity-name-pattern 参数过滤实体
  - 移除 export_path 字段输出
- ✅ **er_convert 命令改进**：
  - --toml-search-dir 重命名为 --output-dir
  - 参数命名更加一致和直观
- ✅ **代码生成器更新**：
  - Django 和 SQLAlchemy 渲染器使用 entity.table_name
  - 确保生成的代码使用正确的表名
- ✅ **测试覆盖**：464 个测试通过（95.7% 覆盖率）
- ✅ **文档更新**：完整的使用文档和迁移指南

### 新增功能

#### Django模型多文件生成
- ✅ **DjangoPackageRenderer**：新增多文件Django模型渲染器
  - 每个模型生成独立的Python文件
  - 自动生成 `__init__.py` 导入所有模型
  - 更好的代码组织和可维护性
- ✅ **CLI支持**：新增命令行选项支持多文件输出
  - `--split-models`：启用多文件模式
  - `--output-dir, -d`：指定输出目录
  - 示例：`er-convert convert input.mmd -f django --split-models -d models/`
- ✅ **模板优化**：
  - `django_model_single.j2`：单个模型文件模板
  - `django_init.j2`：包初始化文件模板
  - 改进的代码格式和文档字符串
  - 添加 `__str__` 方法

#### 版本管理系统
- ✅ **setuptools-scm 集成**：使用 setuptools-scm 从 git tag 自动管理版本
  - 无需手动维护版本号
  - 支持开发版本号（如 `0.1.0.dev10`）
  - 支持从 git tag 生成正式版本号
- ✅ **版本查看命令**：所有 CLI 工具支持 `--version` 参数
  - `er-convert --version`：查看 ER 转换工具版本
  - `er-ai --version`：查看 AI 建模工具版本
  - `er-mcp --version`：查看 MCP 服务器版本
- ✅ **公共版本模块**：新增 `src/x007007007/er/version.py`
  - 提供 `get_version()` 函数供所有模块使用
  - 导出 `__version__` 变量
  - 避免代码重复

### 改进

#### 构建系统
- ✅ **pyproject.toml 配置**：
  - 添加 `setuptools-scm[toml]>=6.2` 到构建依赖
  - 配置 `[tool.setuptools_scm]` 部分
  - 设置 fallback 版本为 `0.1.0.dev0`
- ✅ **动态版本**：版本号从 git 仓库自动获取
  - 有 tag 时使用 tag 版本
  - 无 tag 时生成开发版本号（基于提交数）

#### CLI 改进
- ✅ **统一版本显示**：所有 CLI 工具使用统一的版本获取方式
- ✅ **代码复用**：通过公共 `version.py` 模块避免重复代码

### 技术细节

#### 依赖更新
- `setuptools>=45`：现代 setuptools 版本
- `setuptools-scm[toml]>=6.2`：版本管理插件

#### 版本号规则
- **正式版本**：`v0.1.0` tag → `0.1.0`
- **开发版本**：无 tag 或有新提交 → `0.1.0.dev10`（数字为距离最近 tag 的提交数）
- **未安装**：显示 `unknown`

---

## [0.1.0] - 2024年12月

### 新增功能

#### MCP 服务器支持
- ✅ **MCP 服务器实现**：新增 `er_mcp` 模块，提供 Model Context Protocol 服务器
- ✅ **Cursor 集成**：支持在 Cursor 编辑器中直接使用 ER 转换工具
- ✅ **工具接口**：提供 4 个 MCP 工具：
  - `convert_er_diagram`: ER 图格式转换
  - `parse_er_diagram`: 解析 ER 图并返回模型结构
  - `render_er_model`: 从 JSON 模型渲染代码
  - `validate_er_model`: 验证 ER 模型
- ✅ **配置文档**：新增 `docs/MCP_SETUP.md` 配置指南
- ✅ **调试支持**：新增 `docs/MCP_DEBUGGING.md` 调试指南
  - 支持环境变量启用调试日志
  - 详细的错误处理和日志记录
  - 手动测试和故障排除指南
- ✅ **单元测试**：新增 `tests/test_er_mcp.py`，包含 18 个测试用例
  - 测试所有工具功能
  - 测试错误处理
  - 测试边界情况
  - 测试覆盖率：100%

#### ANTLR4 解析器
- ✅ **完全迁移到 ANTLR4**：Mermaid 和 PlantUML 都使用 ANTLR4 解析器
- ✅ **Mermaid ANTLR 解析器** (`mermaid_antlr_parser.py`)
  - 使用 ANTLR 语法文件 (`MermaidER.g4`) 定义完整语法
  - 支持注释、外键、关系类型等完整语法
  - 更好的错误报告和恢复机制
  - 覆盖率：89%
- ✅ **PlantUML ANTLR 解析器** (`plantuml_antlr_parser.py`)
  - 使用 ANTLR 语法文件 (`PlantUMLER.g4`) 定义完整语法
  - 支持所有 PlantUML 关系语法（`||--||`, `}o--||` 等）
  - 完整支持基数（cardinality）解析
  - 支持实体别名、列标记（PK, FK, enum）
  - 覆盖率：84%
- ✅ **生成脚本**：Windows (`generate_antlr.bat`) 和 Linux/Mac (`generate_antlr.sh`)
- ✅ **移除正则表达式解析器**：完全移除 `parsers.py` 和 `plantuml_parser.py`

#### 数据模型扩展
- ✅ **Relationship 模型扩展**：
  - `left_column`: 外键列名
  - `right_column`: 外键列名
  - `left_cardinality`: 基数信息（"1", "0..1", "*"）
  - `right_cardinality`: 基数信息
- ✅ **Column 模型扩展**：
  - `max_length`: 字段长度（如 VARCHAR(255)）
  - `precision`: 精度（如 DECIMAL(10,2)）
  - `scale`: 小数位数
  - `unique`: 唯一性约束
  - `indexed`: 索引信息
- ✅ **ERModel 验证方法**：新增 `validate()` 方法
  - 验证实体名称冲突
  - 验证关系的实体是否存在
  - 验证关系引用的列是否存在

#### 类型映射系统
- ✅ **TypeMapper 类** (`type_mapper.py`)：统一的类型映射系统
- ✅ **支持的数据类型**：
  - 整数类型：int, integer, bigint, smallint
  - 浮点类型：float, real, double
  - 小数类型：decimal, numeric
  - 布尔类型：boolean, bool
  - 日期时间：date, time, datetime, timestamp
  - 文本类型：string, varchar, char, text, longtext
  - JSON 类型：json, jsonb
- ✅ **Django 和 SQLAlchemy 类型映射**：完整的类型转换支持

#### ORM 代码生成
- ✅ **Django 模板**：
  - `ForeignKey`, `OneToOneField`, `ManyToManyField` 支持
  - 关系命名规范：使用 `_set` 后缀和 `_rel` 后缀
- ✅ **SQLAlchemy 模板**：
  - `ForeignKey` 和 `relationship` 支持
  - Many-to-many 中间表自动生成
- ✅ **外键关系处理**：完整的外键关系生成

#### 数据库解析器改进
- ✅ **外键关系解析**：已实现（之前是 `pass`）
- ✅ **资源管理**：使用上下文管理器确保连接关闭
- ✅ **错误处理**：添加 NotImplementedError 处理
- ✅ **类型映射改进**：使用 TypeMapper
- ✅ **表注释处理**：已添加

#### TOML 格式支持
- ✅ **TOML ER 图解析器** (`toml_parser.py`)
- ✅ **模板和继承**：支持实体继承多个模板
- ✅ **字段覆盖**：支持模板字段覆盖
- ✅ **导出路径**：支持实体导出路径配置

### 改进

#### 代码质量
- ✅ **测试覆盖**：115 个测试全部通过
  - 总体覆盖率：88%（已排除 ANTLR 生成代码）
  - `type_mapper.py`: 100%
  - `converters.py`: 100%
  - `renderers.py`: 100%
  - `base.py`: 100%
  - `er_mcp/cli.py`: 100%
  - `models.py`: 94%
  - `mermaid_antlr_parser.py`: 92%
  - `plantuml_antlr_parser.py`: 88%
  - `er_mcp/server.py`: 85%
  - `cli.py`: 82%
- ✅ **代码规范**：
  - 使用 `assert` 进行函数参数验证（符合项目规范）
  - 禁止滥用 try-except
  - 使用类型提示（type hints）
- ✅ **错误处理**：
  - CLI 文件存在性验证
  - 文件读取错误处理（FileNotFoundError, IOError）
  - 自定义 ErrorListener 记录语法错误
- ✅ **代码重复消除**：移除正则表达式解析器，使用 ANTLR4 统一架构

#### CLI 改进
- ✅ **参数验证**：使用 assert 进行参数验证
- ✅ **默认值**：自动从文件名生成 `app_label` 和 `table_prefix`
- ✅ **错误处理**：改进的错误处理和用户友好的错误消息

#### 文档
- ✅ **README.md**：完善项目介绍、安装说明、使用示例、MCP配置、AI工具使用
- ✅ **CHANGELOG.md**：完整的变更历史记录

### 修复

#### 解析器修复
- ✅ **MermaidParser**：完全替换为 ANTLR4 解析器，解决正则表达式解析问题
- ✅ **PlantUMLParser**：完全替换为 ANTLR4 解析器，解决关系类型判断问题
- ✅ **关系类型判断**：修复关系类型判断逻辑
- ✅ **基数标记**：修复基数标记解析问题
- ✅ **错误恢复**：改进格式错误的恢复机制

#### DBParser 修复
- ✅ **外键关系解析**：实现外键关系解析（之前未实现）
- ✅ **数据库连接**：使用上下文管理器确保连接关闭
- ✅ **错误处理**：添加错误处理逻辑
- ✅ **类型转换**：改进类型转换逻辑（使用 TypeMapper）
- ✅ **表注释**：添加表注释处理

#### 渲染器修复
- ✅ **外键关系生成**：修复 Django 和 SQLAlchemy 模板中外键关系未生成的问题
- ✅ **Many-to-many 关系**：修复中间表未生成的问题
- ✅ **类型映射**：修复类型映射过于简单的问题

### 已知问题

#### 待改进
- ⚠️ **DBParser 测试覆盖率**：当前 59%，需要更多测试（数据库相关测试较复杂）
- ⚠️ **CLI 功能**：验证命令、查看命令、格式化选项尚未实现
- ⚠️ **解析统计信息**：解析统计信息日志尚未实现
- ⚠️ **性能测试**：需要添加性能测试

### 技术细节

#### 依赖更新
- `antlr4-python3-runtime>=4.13.1`：ANTLR4 解析器运行时
- `jinja2>=3.1.2`：模板引擎
- `sqlalchemy>=2.0.0`：数据库连接
- `click>=8.1.0`：命令行接口
- `toml>=0.10.2`：TOML 解析
- `pydantic>=2.0.0`：数据验证
- `langchain>=0.1.0`：AI 集成（用于 er_ai）
- `langchain-deepseek>=0.1.0`：DeepSeek 集成

#### 项目结构
```
ER/
├── src/x007007007/
│   ├── er/                    # ER 转换核心模块
│   │   ├── parser/antlr/      # ANTLR 解析器
│   │   ├── templates/         # Jinja2 模板
│   │   └── ...
│   ├── er_ai/                 # AI 建模工具
│   └── er_mcp/                # MCP 服务器（新增）
├── tests/                     # 测试文件
├── docs/                      # 文档
└── tools/                     # 工具脚本
```

### 迁移指南

#### 从正则表达式解析器迁移
- ✅ **已自动迁移**：项目已完全移除正则表达式解析器
- ✅ **无需更改代码**：API 接口保持不变
- ⚠️ **必须生成 ANTLR 代码**：使用前需要运行 `tools/generate_antlr.bat` 或 `tools/generate_antlr.sh`

#### 使用 MCP 服务器
1. 安装依赖：`uv sync` 或 `pip install -e .`
2. 配置 Cursor：参考 `docs/MCP_SETUP.md`
3. 重启 Cursor 并开始使用

### 贡献者

- xxc (x007007007@hotmail.com)

---

## 版本历史

- **0.1.0** (2024-12): 初始版本
  - ANTLR4 解析器实现（完全替换正则表达式解析器）
  - MCP 服务器支持（Cursor 集成）
  - 完整的数据模型和类型映射
  - ORM 代码生成（Django 和 SQLAlchemy）
  - TOML 格式支持（模板和继承）
  - AI 建模工具（自然语言生成 ER 图）
  - 115 个测试全部通过，覆盖率 88%

