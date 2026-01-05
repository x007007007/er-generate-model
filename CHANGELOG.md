# Changelog

本文档记录 ER Diagram Converter 项目的所有重要变更。

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

