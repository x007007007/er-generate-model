# ER Migrations - 需求文档

## 概述

实现一个类似Django Migrations的数据库迁移管理系统，基于ER图来管理数据库schema的变更历史。

## 用户故事

### 1. 作为开发者，我希望能够自动生成数据库变更记录
**场景**: 当我修改ER图后，系统能够自动检测变更并生成迁移文件

**验收标准**:
- 1.1 系统能够比较当前ER图与上一个迁移状态的差异
- 1.2 系统能够识别以下变更类型：
  - 创建表（CreateTable）
  - 删除表（DeleteTable）
  - 修改表（AlterTable）
  - 添加字段（AddColumn）
  - 删除字段（RemoveColumn）
  - 修改字段（AlterColumn）
  - 添加索引（AddIndex）
  - 删除索引（RemoveIndex）
  - 添加外键（AddForeignKey）
  - 删除外键（RemoveForeignKey）
- 1.3 生成的迁移文件包含完整的操作记录和依赖信息
- 1.4 迁移文件使用YAML或TOML格式存储

### 2. 作为开发者，我希望能够管理多个独立的迁移命名空间
**场景**: 在一个项目中，可能有多个独立的数据库schema需要管理（例如：主应用数据库、日志数据库、缓存数据库等）

**验收标准**:
- 2.1 支持通过目录结构组织不同的命名空间
- 2.2 可以通过glob规则选择特定的命名空间
- 2.3 每个命名空间维护独立的迁移历史
- 2.4 支持跨命名空间的依赖关系（例如：一个表引用另一个命名空间的表）

### 3. 作为开发者，我希望迁移文件有明确的顺序和依赖关系
**场景**: 确保迁移按正确的顺序执行

**验收标准**:
- 3.1 迁移文件使用数字前缀命名（如0001_initial.yaml, 0002_add_user_table.yaml）
- 3.2 每个迁移文件记录其依赖的迁移（dependencies字段）
- 3.3 支持依赖其他命名空间的迁移
- 3.4 系统能够自动计算迁移的执行顺序

### 4. 作为开发者，我希望能够从迁移历史重建ER图状态
**场景**: 了解数据库在特定迁移点的schema状态

**验收标准**:
- 4.1 能够应用所有迁移操作重建完整的ER模型
- 4.2 能够重建到指定迁移点的ER模型
- 4.3 重建的ER模型可以与当前ER图进行比较
- 4.4 支持生成ER图的可视化表示

### 5. 作为开发者，我希望迁移系统支持常见的数据库操作
**场景**: 覆盖实际开发中的各种数据库变更需求

**验收标准**:
- 5.1 支持数据操作（插入、更新、删除数据）
- 5.2 支持索引管理（创建、删除索引）
- 5.3 支持约束管理（唯一约束、检查约束）
- 5.4 支持数据类型的跨数据库映射

### 6. 作为开发者，我希望使用类型安全的数据模型
**场景**: 确保迁移文件的正确性和可维护性

**验收标准**:
- 6.1 使用Pydantic定义迁移文件的数据模型
- 6.2 支持迁移文件的验证
- 6.3 提供清晰的错误提示
- 6.4 支持IDE的类型提示和自动完成

### 7. 作为开发者，我希望能够预览迁移变更
**场景**: 在生成迁移文件前，先查看会产生哪些变更

**验收标准**:
- 7.1 支持 `--dry-run` 选项预览变更
- 7.2 清晰显示将要执行的操作
- 7.3 显示受影响的表和字段
- 7.4 支持JSON格式输出便于程序处理

### 8. 作为开发者，我希望迁移系统能够检测冲突
**场景**: 多人协作时可能产生迁移冲突

**验收标准**:
- 8.1 检测同一命名空间下的迁移编号冲突
- 8.2 检测循环依赖
- 8.3 检测不存在的依赖
- 8.4 提供清晰的冲突解决建议

## 功能需求

### 命令行接口

#### `er-migrate makemigrations`
生成新的迁移文件

**选项**:
- `--namespace, -n`: 指定命名空间（支持glob模式）
- `--name`: 迁移文件名称
- `--empty`: 创建空迁移文件
- `--dry-run`: 预览变更但不生成文件
- `--migrations-dir`: 迁移文件目录（默认：.migrations/）

**示例**:
```bash
# 为所有命名空间生成迁移
er-migrate makemigrations

# 为特定命名空间生成迁移
er-migrate makemigrations -n main_db

# 使用glob模式（例如：所有以db_开头的命名空间）
er-migrate makemigrations -n "db_*"

# 创建空迁移
er-migrate makemigrations -n main_db --empty --name add_custom_index
```

#### `er-migrate showmigrations`
显示迁移状态

**选项**:
- `--namespace, -n`: 指定命名空间
- `--format`: 输出格式（text, json, yaml）

**示例**:
```bash
# 显示所有迁移
er-migrate showmigrations

# 显示特定命名空间的迁移
er-migrate showmigrations -n main_db
```

#### `er-migrate squashmigrations`
合并多个迁移为一个

**选项**:
- `--namespace, -n`: 指定命名空间
- `--start`: 起始迁移
- `--end`: 结束迁移

#### `er-migrate rebuild-state`
从迁移历史重建ER状态

**选项**:
- `--namespace, -n`: 指定命名空间
- `--target`: 目标迁移（默认：最新）
- `--output, -o`: 输出文件
- `--format`: 输出格式（mermaid, plantuml, toml）

**示例**:
```bash
# 重建最新状态
er-migrate rebuild-state -n main_db -o current_state.mmd

# 重建到特定迁移
er-migrate rebuild-state -n main_db --target 0005 -o state_at_0005.mmd
```

### 迁移文件格式

#### YAML格式示例

```yaml
# migrations/main_db/0001_initial.yaml
version: "1.0"
name: "initial"
namespace: "main_db"
dependencies: []
operations:
  - type: CreateTable
    table_name: users
    columns:
      - name: id
        type: uuid
        primary_key: true
        nullable: false
      - name: username
        type: string
        max_length: 150
        unique: true
        nullable: false
      - name: email
        type: string
        max_length: 255
        nullable: false
      - name: created_at
        type: datetime
        auto_now_add: true
    
  - type: AddIndex
    table_name: users
    index_name: idx_users_email
    columns: [email]
    unique: false

  - type: AddForeignKey
    table_name: posts
    column_name: user_id
    reference_table: users
    reference_column: id
    on_delete: CASCADE
    on_update: CASCADE
```

#### TOML格式示例

```toml
# migrations/main_db/0002_add_profile.toml
version = "1.0"
name = "add_profile"
namespace = "main_db"
dependencies = ["main_db.0001_initial"]

[[operations]]
type = "CreateTable"
table_name = "user_profiles"

[[operations.columns]]
name = "id"
type = "uuid"
primary_key = true
nullable = false

[[operations.columns]]
name = "user_id"
type = "uuid"
nullable = false

[[operations.columns]]
name = "bio"
type = "text"
nullable = true

[[operations]]
type = "AddForeignKey"
table_name = "user_profiles"
column_name = "user_id"
reference_table = "users"
reference_column = "id"
on_delete = "CASCADE"
```

### 数据模型（Pydantic）

#### 核心模型

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class ColumnType(str, Enum):
    """数据库列类型"""
    INT = "int"
    BIGINT = "bigint"
    STRING = "string"
    TEXT = "text"
    UUID = "uuid"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    DECIMAL = "decimal"
    FLOAT = "float"

class OnDeleteAction(str, Enum):
    """外键删除动作"""
    CASCADE = "CASCADE"
    SET_NULL = "SET_NULL"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO_ACTION"

class Column(BaseModel):
    """列定义"""
    name: str
    type: ColumnType
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    default: Optional[str] = None
    auto_increment: bool = False
    auto_now_add: bool = False
    auto_now: bool = False

class Operation(BaseModel):
    """迁移操作基类"""
    type: str

class CreateTable(Operation):
    """创建表操作"""
    type: Literal["CreateTable"] = "CreateTable"
    table_name: str
    columns: List[Column]
    comment: Optional[str] = None

class AddColumn(Operation):
    """添加列操作"""
    type: Literal["AddColumn"] = "AddColumn"
    table_name: str
    column: Column

class Migration(BaseModel):
    """迁移文件模型"""
    version: str = "1.0"
    name: str
    namespace: str
    dependencies: List[str] = Field(default_factory=list)
    operations: List[Operation]
```

## 项目结构

```
ER/
├── src/x007007007/
│   ├── er/                          # 现有ER转换模块
│   ├── er_ai/                       # 现有AI建模模块
│   ├── er_mcp/                      # 现有MCP服务器模块
│   └── er_migrate/                  # 新增：迁移管理模块
│       ├── __init__.py
│       ├── cli.py                   # 命令行接口
│       ├── models.py                # Pydantic数据模型
│       ├── operations.py            # 迁移操作定义
│       ├── generator.py             # 迁移生成器
│       ├── differ.py                # ER图差异比较
│       ├── state_builder.py         # 状态重建器
│       ├── file_manager.py          # 迁移文件管理
│       └── namespace.py             # 命名空间管理
├── tests/
│   └── test_er_migrate/             # 迁移模块测试
│       ├── test_models.py
│       ├── test_operations.py
│       ├── test_generator.py
│       ├── test_differ.py
│       └── test_cli.py
├── .migrations/                     # 默认迁移文件目录
│   ├── namespace1/
│   │   ├── 0001_initial.yaml
│   │   └── 0002_add_users.yaml
│   └── namespace2/
│       └── 0001_initial.yaml
└── pyproject.toml                   # 添加er-migrate命令入口
```

## 开发流程

### 使用uv进行开发

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
uv run pytest tests/test_er_migrate/

# 运行特定测试
uv run pytest tests/test_er_migrate/test_models.py -v

# 运行测试并查看覆盖率
uv run pytest tests/test_er_migrate/ --cov=src/x007007007/er_migrate --cov-report=term-missing

# 使用命令行工具
uv run er-migrate --help
uv run er-migrate makemigrations
```

## 技术约束

1. **Python版本**: >= 3.11
2. **项目管理**: 使用uv进行依赖管理
3. **依赖库**:
   - pydantic >= 2.0.0
   - pyyaml >= 6.0
   - toml >= 0.10.2
   - click >= 8.1.0 (已有)
4. **测试覆盖率**: >= 90%
5. **代码规范**: 遵循项目现有规范
   - 使用assert进行参数验证
   - 禁止滥用try-except
   - 使用类型提示（type hints）
6. **命令行工具**: 新增 `er-migrate` 命令入口点

## 非功能需求

1. **性能**: 
   - 生成迁移文件应在1秒内完成（对于<100个表的schema）
   - 重建ER状态应在2秒内完成

2. **可扩展性**:
   - 支持自定义操作类型
   - 支持插件机制扩展数据库适配器

3. **可维护性**:
   - 清晰的代码结构
   - 完整的文档和示例
   - 使用TDD开发

## 实现优先级

### P0 (必须实现)
- 基本的迁移文件生成（CreateTable, AddColumn, RemoveColumn）
- 迁移文件的读写和验证
- 简单的diff算法
- 命令行接口基础功能

### P1 (重要)
- 完整的操作类型支持
- 依赖关系管理
- 从迁移重建ER状态
- 多命名空间支持

### P2 (可选)
- 迁移合并（squash）
- 数据操作支持
- 可视化工具
- 数据库适配器

## 风险和挑战

1. **复杂的diff算法**: 准确识别schema变更可能很复杂
2. **依赖关系管理**: 跨命名空间的依赖可能导致循环依赖
3. **数据类型映射**: 不同数据库的类型映射需要仔细设计
4. **向后兼容性**: 迁移文件格式的变更需要考虑兼容性

## 成功标准

1. 能够成功生成和应用迁移文件
2. 测试覆盖率达到90%以上
3. 文档完整，包含使用示例
4. 性能满足非功能需求
5. 代码通过所有lint检查
