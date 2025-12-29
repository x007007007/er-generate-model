# ER AI 使用指南

ER AI 是一个基于 LangChain 和 DeepSeek 的智能 ER 建模工具，可以根据自然语言需求自动生成 TOML 格式的 ER 配置。

## 功能特性

- 🤖 **AI 驱动**：使用 DeepSeek 大语言模型进行 ER 建模
- 📝 **自然语言输入**：支持用自然语言描述需求
- 🎯 **自动生成**：自动生成符合规范的 TOML ER 配置
- ✅ **语法验证**：自动验证生成的 TOML 语法，错误时自动重试
- 🔄 **智能重试**：验证失败时，将错误信息反馈给 AI，让其重新生成
- 📊 **流式输出**：支持分段输出，实时查看生成过程
- 🔧 **易于集成**：提供 CLI 和 SDK 两种使用方式

## 安装

确保已安装项目依赖：

```bash
uv sync
```

**注意**：项目使用 `langchain-deepseek` 作为 DeepSeek 的专用集成包。如果安装失败，会自动回退到 `langchain-community` 的 `ChatOpenAI`（兼容模式），但会显示警告信息。

## 配置 API 密钥

在使用前，需要设置 DeepSeek API 密钥。推荐使用 `.env` 文件进行配置：

### 方法 1: 使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
# .env
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1  # 可选，默认使用官方API
```

项目会自动从 `.env` 文件加载配置。可以参考 `.env.example` 文件创建自己的 `.env` 文件。

**注意**：`.env` 文件包含敏感信息，不要提交到版本控制系统。

### 方法 2: 使用环境变量

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-api-key-here"

# Linux/Mac
export DEEPSEEK_API_KEY="your-api-key-here"
```

### 方法 3: 通过命令行参数传递

也可以在使用时通过 `--api-key` 参数传递（见下文）。

## 使用方法

### 1. 命令行工具 (CLI)

#### 基本用法

```bash
# 从命令行参数读取需求
er-ai generate "设计一个博客系统，包含用户、文章、标签等实体" -o output.toml

# 从文件读取需求
er-ai generate -i requirement.txt -o output.toml

# 从标准输入读取需求
echo "设计一个电商系统" | er-ai generate -o output.toml
```

#### 命令行选项

- `requirement`: 需求描述（可选，如果提供了 `--input-file` 则从文件读取）
- `--api-key`: DeepSeek API 密钥（或设置 `DEEPSEEK_API_KEY` 环境变量）
- `--base-url`: DeepSeek API 基础 URL（可选，默认使用官方 API）
- `--output, -o`: 输出文件路径（默认输出到标准输出）
- `--input-file, -i`: 从文件读取需求描述
- `--max-retries, -r`: 最大重试次数（默认 3 次），当 TOML 验证失败时自动重试
- `--stream`: 启用流式输出，实时显示生成过程

#### 示例

```bash
# 生成博客系统 ER 配置
er-ai generate "设计一个博客系统，包含以下功能：
- 用户管理：用户注册、登录、个人资料
- 文章管理：发布、编辑、删除文章
- 标签系统：文章可以打多个标签
- 评论系统：用户可以对文章进行评论" -o blog_er.toml

# 使用自定义 API 密钥
er-ai generate "设计一个电商系统" --api-key "sk-xxx" -o ecommerce.toml

# 使用流式输出（实时查看生成过程）
er-ai generate "设计一个博客系统" --stream -o blog.toml

# 设置最大重试次数
er-ai generate "设计一个复杂系统" --max-retries 5 -o complex.toml
```

### 2. 修改现有TOML配置

使用 `refine` 命令可以基于现有TOML文件进行修改和完善：

```bash
# 基本用法
er-ai refine existing.toml "添加一个评论实体，与文章建立一对多关系" -o refined.toml

# 从文件读取修改需求
er-ai refine existing.toml -m modification.txt -o refined.toml

# 使用流式输出
er-ai refine existing.toml "添加用户头像字段" --stream -o refined.toml
```

#### refine 命令选项

- `existing_toml_file`: 现有的TOML ER配置文件路径（必需）
- `modification_request`: 修改需求描述（可选，如果提供了 `--modification-file` 则从文件读取）
- `--modification-file, -m`: 从文件读取修改需求描述
- `--max-retries, -r`: 最大重试次数（默认 3 次）
- `--stream`: 启用流式输出
- 其他选项与 `generate` 命令相同

#### 修改示例

```bash
# 添加新实体
er-ai refine blog.toml "添加一个TAG实体，包含name字段，与POST建立多对多关系" -o blog_updated.toml

# 修改现有实体
er-ai refine blog.toml "给USER实体添加avatar_url和bio字段" -o blog_updated.toml

# 添加关系
er-ai refine blog.toml "在USER和POST之间添加一个收藏关系（多对多）" -o blog_updated.toml

# 添加模板
er-ai refine blog.toml "创建一个soft_delete模板，包含deleted_at字段，让POST实体继承" -o blog_updated.toml
```

### 3. SDK 接口

#### Python SDK

```python
from x007007007.er_ai import generate_er_model

# 基本用法
toml_config = generate_er_model(
    "设计一个博客系统，包含用户、文章、标签等实体"
)
print(toml_config)

# 使用自定义 API 密钥
toml_config = generate_er_model(
    "设计一个电商系统",
    api_key="sk-xxx"
)

# 使用流式输出和自定义重试次数
def on_chunk(chunk):
    print(chunk, end='', flush=True)

toml_config = generate_er_model(
    "设计一个博客系统",
    max_retries=5,
    stream=True,
    on_chunk=on_chunk
)

# 保存到文件
with open("output.toml", "w", encoding="utf-8") as f:
    f.write(toml_config)
```

#### 高级用法

```python
from x007007007.er_ai import ERModeler

# 创建建模器实例
modeler = ERModeler(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1"  # 可选
)

# 生成 TOML 配置
toml_config = modeler.generate_toml(
    "设计一个内容管理系统，包含用户、文章、分类、评论等实体"
)

# 验证生成的配置（可选）
from x007007007.er.parser.toml_parser import TomlERParser
parser = TomlERParser()
model = parser.parse(toml_config)
print(f"生成了 {len(model.entities)} 个实体")
```

### 3. 生成代码

生成的 TOML 配置可以直接用于生成 Django 或 SQLAlchemy 代码：

```bash
# 生成 Django 代码
er-convert output.toml -t toml -f django -o models.py

# 生成 SQLAlchemy 代码
er-convert output.toml -t toml -f sqlalchemy -o models.py
```

## 修改需求描述建议

当使用 `refine` 命令修改现有TOML时，建议在修改需求中：

1. **明确操作类型**：说明是"添加"、"修改"还是"删除"
2. **指定目标**：明确指出要修改的实体、字段或关系
3. **描述关系**：如果要添加关系，说明关系的类型和方向
4. **保持一致性**：参考现有结构的命名和格式风格

### 好的修改需求示例

```
# 添加实体
"添加一个COMMENT实体，包含content和created_at字段，与POST建立多对多关系"

# 修改实体
"给USER实体添加email和phone字段，email字段设置为唯一"

# 添加关系
"在USER和POST之间添加一个收藏关系（多对多），创建FAVORITE中间表"

# 添加模板
"创建一个audit_fields模板，包含created_at和updated_at字段，让所有实体继承"

# 修改字段
"将POST实体的content字段类型从string改为text"
```

## 需求描述建议

为了获得更好的 ER 建模结果，建议在需求描述中包含：

1. **核心实体**：明确列出需要的主要实体（如用户、文章、订单等）
2. **实体关系**：描述实体之间的关系（如用户发布文章、文章有标签等）
3. **字段要求**：重要的字段或业务规则（如用户名唯一、文章有状态等）
4. **业务场景**：简要描述业务场景，帮助 AI 理解上下文

### 好的需求描述示例

```
设计一个博客系统，包含以下功能：
- 用户管理：用户注册、登录，包含用户名、邮箱、密码、头像等字段
- 文章管理：用户可以发布、编辑、删除文章，文章包含标题、内容、状态（草稿/已发布）
- 标签系统：文章可以打多个标签，标签有名称和描述
- 评论系统：用户可以对文章进行评论，评论包含内容和时间戳
- 关系：用户和文章是一对多关系，文章和标签是多对多关系，用户和评论是一对多关系
```

## 输出格式

生成的 TOML 配置遵循项目的 TOML ER 图格式规范，包括：

- **模板定义**：可复用的字段模板（如 `create_update_time`、`enable` 等）
- **实体定义**：包含字段、继承关系、注释等
- **关系定义**：实体之间的关系和基数

生成的配置可以直接用于：
- 生成 Django 模型代码
- 生成 SQLAlchemy 模型代码
- 转换为 Mermaid 或 PlantUML 图表

## 语法验证和重试机制

ER AI 工具内置了 TOML 语法验证功能：

1. **自动验证**：每次生成后自动验证 TOML 语法和 ER 模型结构
2. **智能重试**：如果验证失败，会将错误信息反馈给 AI，让其重新生成
3. **重试上限**：默认最多重试 3 次，可通过 `--max-retries` 参数调整
4. **错误反馈**：AI 会根据具体的错误信息（如语法错误、缺少主键等）进行修正

### 验证内容

- TOML 语法正确性
- ER 模型结构完整性
- 实体关系有效性
- 字段定义规范性

## 流式输出

使用 `--stream` 参数可以启用流式输出：

```bash
er-ai generate "设计一个博客系统" --stream
```

流式输出的优势：
- 实时查看生成过程
- 更快的响应体验
- 适合长时间生成任务

## 注意事项

1. **API 密钥安全**：不要将 API 密钥提交到版本控制系统
2. **生成质量**：AI 生成的结果可能需要人工审核和调整
3. **成本考虑**：每次调用（包括重试）都会消耗 API 配额，注意使用频率
4. **网络连接**：需要能够访问 DeepSeek API 服务
5. **重试次数**：如果多次重试仍失败，可能需要调整需求描述或检查 API 配置

## 故障排除

### API 密钥错误

```
ValueError: DeepSeek API key is required.
```

**解决方案**：确保设置了 `DEEPSEEK_API_KEY` 环境变量或通过 `--api-key` 参数传递。

### 网络连接错误

如果无法连接到 DeepSeek API，检查：
- 网络连接是否正常
- API 基础 URL 是否正确
- 防火墙设置是否阻止了连接

### 生成结果不符合预期

- 尝试更详细的需求描述
- 明确指定实体关系和字段要求
- 可以多次尝试，AI 生成结果可能有变化

## 示例项目

完整的使用示例可以参考项目中的测试用例：

```bash
# 查看测试用例
cat tests/test_er_ai.py
```

## 相关文档

- [TOML ER 图格式规范](../README.md#toml-格式)
- [ER 转换工具使用指南](../README.md)
- [Django 代码生成](../README.md#django-模型生成)
- [SQLAlchemy 代码生成](../README.md#sqlalchemy-模型生成)

