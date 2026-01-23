# ER Migrations - 设计文档

## 1. 架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (cli.py)                       │
│  er-migrate makemigrations | showmigrations | rebuild-state │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                  Core Modules                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Generator   │  │    Differ    │  │StateBuilder  │     │
│  │  (生成迁移)  │  │  (比较差异)  │  │ (重建状态)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                  Support Modules                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │FileManager   │  │  Namespace   │  │  Operations  │     │
│  │(文件管理)    │  │  (命名空间)  │  │  (操作定义)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                  Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   Models     │  │   ERModel    │                        │
│  │ (Pydantic)   │  │  (现有模型)  │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责

#### CLI Layer (cli.py)
- 解析命令行参数
- 调用核心模块的功能
- 格式化输出结果

#### Core Modules
- **Generator**: 生成迁移文件的核心逻辑
- **Differ**: 比较两个ER模型的差异
- **StateBuilder**: 从迁移历史重建ER状态

#### Support Modules
- **FileManager**: 管理迁移文件的读写
- **Namespace**: 管理命名空间和依赖关系
- **Operations**: 定义所有迁移操作类型

#### Data Layer
- **Models**: Pydantic数据模型定义
- **ERModel**: 复用现有的ER模型

## 2. 数据模型设计

### 2.1 核心数据模型


```python
# src/x007007007/er_migrate/models.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Union, Any
from enum import Enum
from datetime import datetime


class ColumnType(str, Enum):
    """数据库列类型枚举"""
    INT = "int"
    BIGINT = "bigint"
    SMALLINT = "smallint"
    STRING = "string"
    VARCHAR = "varchar"
    CHAR = "char"
    TEXT = "text"
    UUID = "uuid"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    JSON = "json"
    JSONB = "jsonb"
    DECIMAL = "decimal"
    NUMERIC = "numeric"
    FLOAT = "float"
    DOUBLE = "double"
    REAL = "real"


class OnDeleteAction(str, Enum):
    """外键删除动作"""
    CASCADE = "CASCADE"
    SET_NULL = "SET_NULL"
    SET_DEFAULT = "SET_DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO_ACTION"


class OnUpdateAction(str, Enum):
    """外键更新动作"""
    CASCADE = "CASCADE"
    SET_NULL = "SET_NULL"
    SET_DEFAULT = "SET_DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO_ACTION"


class ColumnDefinition(BaseModel):
    """列定义"""
    name: str
    type: ColumnType
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    default: Optional[Any] = None
    auto_increment: bool = False
    comment: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        assert isinstance(v, str) and len(v) > 0, "Column name must be non-empty string"
        return v


class IndexDefinition(BaseModel):
    """索引定义"""
    name: str
    columns: List[str]
    unique: bool = False
    type: Optional[str] = None  # btree, hash, gin, gist等


class ForeignKeyDefinition(BaseModel):
    """外键定义"""
    column_name: str
    reference_table: str
    reference_column: str
    on_delete: OnDeleteAction = OnDeleteAction.NO_ACTION
    on_update: OnUpdateAction = OnUpdateAction.NO_ACTION
    constraint_name: Optional[str] = None


# 操作类型定义
class Operation(BaseModel):
    """迁移操作基类"""
    type: str
    
    class Config:
        extra = "forbid"  # 禁止额外字段


class CreateTable(Operation):
    """创建表操作"""
    type: Literal["CreateTable"] = "CreateTable"
    table_name: str
    columns: List[ColumnDefinition]
    comment: Optional[str] = None


class DeleteTable(Operation):
    """删除表操作"""
    type: Literal["DeleteTable"] = "DeleteTable"
    table_name: str


class RenameTable(Operation):
    """重命名表操作"""
    type: Literal["RenameTable"] = "RenameTable"
    old_name: str
    new_name: str


class AddColumn(Operation):
    """添加列操作"""
    type: Literal["AddColumn"] = "AddColumn"
    table_name: str
    column: ColumnDefinition


class RemoveColumn(Operation):
    """删除列操作"""
    type: Literal["RemoveColumn"] = "RemoveColumn"
    table_name: str
    column_name: str


class AlterColumn(Operation):
    """修改列操作 - 只记录新值，不记录旧值"""
    type: Literal["AlterColumn"] = "AlterColumn"
    table_name: str
    column_name: str
    new_type: Optional[str] = None  # 新的数据类型
    new_max_length: Optional[int] = None  # 新的最大长度
    new_nullable: Optional[bool] = None  # 新的可空性
    new_default: Optional[Any] = None  # 新的默认值


class RenameColumn(Operation):
    """重命名列操作"""
    type: Literal["RenameColumn"] = "RenameColumn"
    table_name: str
    old_name: str
    new_name: str


class AddIndex(Operation):
    """添加索引操作"""
    type: Literal["AddIndex"] = "AddIndex"
    table_name: str
    index: IndexDefinition


class RemoveIndex(Operation):
    """删除索引操作"""
    type: Literal["RemoveIndex"] = "RemoveIndex"
    table_name: str
    index_name: str


class AddForeignKey(Operation):
    """添加外键操作"""
    type: Literal["AddForeignKey"] = "AddForeignKey"
    table_name: str
    foreign_key: ForeignKeyDefinition


class RemoveForeignKey(Operation):
    """删除外键操作"""
    type: Literal["RemoveForeignKey"] = "RemoveForeignKey"
    table_name: str
    constraint_name: str


class AlterForeignKey(Operation):
    """修改外键操作 - 只记录新值"""
    type: Literal["AlterForeignKey"] = "AlterForeignKey"
    table_name: str
    constraint_name: str
    new_on_delete: Optional[str] = None  # 新的删除行为
    new_on_update: Optional[str] = None  # 新的更新行为


# 联合类型
OperationType = Union[
    CreateTable, DeleteTable, RenameTable,
    AddColumn, RemoveColumn, AlterColumn, RenameColumn,
    AddIndex, RemoveIndex,
    AddForeignKey, RemoveForeignKey, AlterForeignKey
]


class Migration(BaseModel):
    """迁移文件模型"""
    version: str = "1.0"
    name: str
    namespace: str
    dependencies: List[str] = Field(default_factory=list)
    operations: List[OperationType]
    created_at: Optional[datetime] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        assert isinstance(v, str) and len(v) > 0, "Migration name must be non-empty"
        return v
    
    @field_validator('namespace')
    @classmethod
    def validate_namespace(cls, v: str) -> str:
        assert isinstance(v, str) and len(v) > 0, "Namespace must be non-empty"
        return v
```



## 3. 核心算法设计

### 3.1 Differ算法 - ER图差异检测

```python
class ERDiffer:
    """ER模型差异检测器"""
    
    def diff(self, old_model: ERModel, new_model: ERModel) -> List[Operation]:
        """
        比较两个ER模型，生成操作列表
        
        算法步骤：
        1. 检测表的变更（新增、删除、重命名）
        2. 对于存在的表，检测列的变更
        3. 检测索引的变更
        4. 检测外键的变更
        5. 优化操作顺序（确保依赖关系正确）
        """
        operations = []
        
        # 1. 检测表变更
        old_tables = set(old_model.entities.keys())
        new_tables = set(new_model.entities.keys())
        
        # 新增的表
        for table_name in new_tables - old_tables:
            operations.append(self._create_table_operation(new_model.entities[table_name]))
        
        # 删除的表
        for table_name in old_tables - new_tables:
            operations.append(DeleteTable(table_name=table_name))
        
        # 2. 检测列变更（对于共同存在的表）
        for table_name in old_tables & new_tables:
            table_ops = self._diff_table(
                old_model.entities[table_name],
                new_model.entities[table_name]
            )
            operations.extend(table_ops)
        
        # 3. 优化操作顺序
        operations = self._optimize_operations(operations)
        
        return operations
    
    def _diff_table(self, old_entity: Entity, new_entity: Entity) -> List[Operation]:
        """比较单个表的变更"""
        operations = []
        
        old_columns = {col.name: col for col in old_entity.columns}
        new_columns = {col.name: col for col in new_entity.columns}
        
        # 新增列
        for col_name in set(new_columns.keys()) - set(old_columns.keys()):
            operations.append(AddColumn(
                table_name=new_entity.name,
                column=self._column_to_definition(new_columns[col_name])
            ))
        
        # 删除列
        for col_name in set(old_columns.keys()) - set(new_columns.keys()):
            operations.append(RemoveColumn(
                table_name=old_entity.name,
                column_name=col_name
            ))
        
        # 修改列
        for col_name in set(old_columns.keys()) & set(new_columns.keys()):
            if self._column_changed(old_columns[col_name], new_columns[col_name]):
                operations.append(AlterColumn(
                    table_name=new_entity.name,
                    column_name=col_name,
                    changes=self._get_column_changes(old_columns[col_name], new_columns[col_name])
                ))
        
        return operations
```

### 3.2 StateBuilder算法 - 状态重建

```python
class StateBuilder:
    """从迁移历史重建ER状态"""
    
    def build_state(self, migrations: List[Migration]) -> ERModel:
        """
        应用所有迁移操作，重建ER模型
        
        算法步骤：
        1. 创建空的ER模型
        2. 按依赖顺序排序迁移
        3. 依次应用每个迁移的操作
        4. 返回最终状态
        """
        model = ERModel()
        
        # 按依赖顺序排序
        sorted_migrations = self._topological_sort(migrations)
        
        # 应用每个迁移
        for migration in sorted_migrations:
            for operation in migration.operations:
                self._apply_operation(model, operation)
        
        return model
    
    def _apply_operation(self, model: ERModel, operation: Operation):
        """应用单个操作到模型"""
        if isinstance(operation, CreateTable):
            entity = Entity(name=operation.table_name, comment=operation.comment)
            for col_def in operation.columns:
                entity.columns.append(self._definition_to_column(col_def))
            model.add_entity(entity)
        
        elif isinstance(operation, DeleteTable):
            if operation.table_name in model.entities:
                del model.entities[operation.table_name]
        
        elif isinstance(operation, AddColumn):
            if operation.table_name in model.entities:
                entity = model.entities[operation.table_name]
                entity.columns.append(self._definition_to_column(operation.column))
        
        # ... 其他操作类型
    
    def _topological_sort(self, migrations: List[Migration]) -> List[Migration]:
        """拓扑排序迁移列表"""
        # 实现拓扑排序算法
        pass
```

### 3.3 Generator算法 - 迁移生成

```python
class MigrationGenerator:
    """迁移文件生成器"""
    
    def generate(
        self,
        namespace: str,
        current_er: ERModel,
        migrations_dir: str,
        name: Optional[str] = None
    ) -> Migration:
        """
        生成新的迁移文件
        
        算法步骤：
        1. 加载命名空间的所有现有迁移
        2. 重建当前数据库状态
        3. 比较当前状态与新ER图
        4. 生成操作列表
        5. 确定依赖关系
        6. 生成迁移文件
        """
        # 1. 加载现有迁移
        file_manager = FileManager(migrations_dir)
        existing_migrations = file_manager.load_namespace_migrations(namespace)
        
        # 2. 重建当前状态
        state_builder = StateBuilder()
        current_state = state_builder.build_state(existing_migrations)
        
        # 3. 比较差异
        differ = ERDiffer()
        operations = differ.diff(current_state, current_er)
        
        if not operations:
            return None  # 没有变更
        
        # 4. 生成迁移
        migration_number = self._get_next_number(existing_migrations)
        migration_name = name or self._auto_generate_name(operations)
        
        # 5. 确定依赖
        dependencies = self._determine_dependencies(namespace, existing_migrations)
        
        migration = Migration(
            name=migration_name,
            namespace=namespace,
            dependencies=dependencies,
            operations=operations,
            created_at=datetime.now()
        )
        
        return migration
```



## 4. 文件管理设计

### 4.1 文件命名规则

```
迁移文件命名格式: {number}_{name}.{format}
示例:
  - 0001_initial.yaml
  - 0002_add_user_table.yaml
  - 0003_add_email_index.toml

目录结构:
.migrations/
├── main_db/              # 主数据库
│   ├── 0001_initial.yaml
│   ├── 0002_add_profile.yaml
│   └── 0003_add_index.yaml
├── log_db/               # 日志数据库
│   ├── 0001_initial.yaml
│   └── 0002_add_status.yaml
└── cache_db/             # 缓存数据库
    └── 0001_initial.yaml
```

### 4.2 FileManager实现

```python
class FileManager:
    """迁移文件管理器"""
    
    def __init__(self, base_dir: str = ".migrations"):
        self.base_dir = Path(base_dir)
    
    def load_migration(self, namespace: str, filename: str) -> Migration:
        """加载单个迁移文件"""
        file_path = self.base_dir / namespace / filename
        
        if file_path.suffix == '.yaml':
            return self._load_yaml(file_path)
        elif file_path.suffix == '.toml':
            return self._load_toml(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def save_migration(self, migration: Migration, format: str = 'yaml'):
        """保存迁移文件"""
        namespace_dir = self.base_dir / migration.namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取下一个编号
        number = self._get_next_number(namespace_dir)
        filename = f"{number:04d}_{migration.name}.{format}"
        file_path = namespace_dir / filename
        
        if format == 'yaml':
            self._save_yaml(file_path, migration)
        elif format == 'toml':
            self._save_toml(file_path, migration)
    
    def list_namespaces(self, pattern: Optional[str] = None) -> List[str]:
        """列出所有命名空间"""
        if not self.base_dir.exists():
            return []
        
        namespaces = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        if pattern:
            import fnmatch
            namespaces = [ns for ns in namespaces if fnmatch.fnmatch(ns, pattern)]
        
        return sorted(namespaces)
    
    def load_namespace_migrations(self, namespace: str) -> List[Migration]:
        """加载命名空间的所有迁移"""
        namespace_dir = self.base_dir / namespace
        if not namespace_dir.exists():
            return []
        
        migrations = []
        for file_path in sorted(namespace_dir.glob('*.*')):
            if file_path.suffix in ['.yaml', '.yml', '.toml']:
                migration = self.load_migration(namespace, file_path.name)
                migrations.append(migration)
        
        return migrations
```

## 5. CLI设计

### 5.1 命令结构

```python
# src/x007007007/er_migrate/cli.py

import click
from x007007007.er.version import get_version

@click.group()
@click.version_option(version=get_version(), prog_name="er-migrate")
def main():
    """ER Migrations - Database schema migration tool"""
    pass

@main.command()
@click.option('--namespace', '-n', help='Namespace (supports glob pattern)')
@click.option('--name', help='Migration name')
@click.option('--empty', is_flag=True, help='Create empty migration')
@click.option('--dry-run', is_flag=True, help='Preview changes without creating files')
@click.option('--migrations-dir', default='.migrations', help='Migrations directory')
@click.option('--er-file', '-e', required=True, help='ER diagram file (mermaid/plantuml/toml)')
@click.option('--format', '-f', type=click.Choice(['yaml', 'toml']), default='yaml')
def makemigrations(namespace, name, empty, dry_run, migrations_dir, er_file, format):
    """Generate new migration files"""
    # 实现逻辑
    pass

@main.command()
@click.option('--namespace', '-n', help='Namespace filter')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'yaml']), default='text')
@click.option('--migrations-dir', default='.migrations')
def showmigrations(namespace, format, migrations_dir):
    """Show migration status"""
    # 实现逻辑
    pass

@main.command()
@click.option('--namespace', '-n', required=True, help='Namespace')
@click.option('--target', help='Target migration (default: latest)')
@click.option('--output', '-o', help='Output file')
@click.option('--format', '-f', type=click.Choice(['mermaid', 'plantuml', 'toml']), default='mermaid')
@click.option('--migrations-dir', default='.migrations')
def rebuild_state(namespace, target, output, format, migrations_dir):
    """Rebuild ER state from migrations"""
    # 实现逻辑
    pass
```

### 5.2 输出格式设计

#### showmigrations 文本输出
```
main_db
  [X] 0001_initial
  [X] 0002_add_profile
  [ ] 0003_add_index (pending)

log_db
  [X] 0001_initial
  [X] 0002_add_status
```

#### makemigrations --dry-run 输出
```
Migrations for 'main_db':
  0003_add_email_index.yaml
    - Add index 'idx_users_email' on users(email)
    - Add column 'last_login' to users
    
No changes detected in 'log_db'
```

## 6. 测试策略

### 6.1 单元测试

```python
# tests/test_er_migrate/test_models.py
def test_column_definition_validation():
    """测试列定义验证"""
    # 正常情况
    col = ColumnDefinition(name="id", type=ColumnType.INT, primary_key=True)
    assert col.name == "id"
    
    # 异常情况
    with pytest.raises(AssertionError):
        ColumnDefinition(name="", type=ColumnType.INT)

# tests/test_er_migrate/test_differ.py
def test_diff_detect_new_table():
    """测试检测新增表"""
    old_model = ERModel()
    new_model = ERModel()
    
    # 添加新表
    user_entity = Entity(name="users")
    user_entity.columns.append(Column(name="id", type="int", is_pk=True))
    new_model.add_entity(user_entity)
    
    differ = ERDiffer()
    operations = differ.diff(old_model, new_model)
    
    assert len(operations) == 1
    assert isinstance(operations[0], CreateTable)
    assert operations[0].table_name == "users"

# tests/test_er_migrate/test_state_builder.py
def test_build_state_from_migrations():
    """测试从迁移重建状态"""
    migrations = [
        Migration(
            name="initial",
            namespace="test",
            operations=[
                CreateTable(
                    table_name="users",
                    columns=[
                        ColumnDefinition(name="id", type=ColumnType.INT, primary_key=True)
                    ]
                )
            ]
        )
    ]
    
    builder = StateBuilder()
    model = builder.build_state(migrations)
    
    assert "users" in model.entities
    assert len(model.entities["users"].columns) == 1
```

### 6.2 集成测试

```python
# tests/test_er_migrate/test_integration.py
def test_full_migration_workflow(tmp_path):
    """测试完整的迁移工作流"""
    # 1. 创建初始ER图
    initial_er = create_test_er_model()
    
    # 2. 生成初始迁移
    generator = MigrationGenerator()
    migration1 = generator.generate("test", initial_er, str(tmp_path))
    
    # 3. 保存迁移
    file_manager = FileManager(str(tmp_path))
    file_manager.save_migration(migration1)
    
    # 4. 修改ER图
    modified_er = modify_test_er_model(initial_er)
    
    # 5. 生成新迁移
    migration2 = generator.generate("test", modified_er, str(tmp_path))
    
    # 6. 验证迁移内容
    assert len(migration2.operations) > 0
    
    # 7. 重建状态
    builder = StateBuilder()
    migrations = file_manager.load_namespace_migrations("test")
    final_state = builder.build_state(migrations + [migration2])
    
    # 8. 验证最终状态与修改后的ER图一致
    assert_er_models_equal(final_state, modified_er)
```

## 7. 性能考虑

### 7.1 优化策略

1. **缓存机制**: 缓存已加载的迁移文件
2. **增量比较**: 只比较变更的部分
3. **并行处理**: 对于多个命名空间，可以并行生成迁移
4. **延迟加载**: 只在需要时加载迁移文件

### 7.2 性能目标

- 生成迁移: < 1秒 (100个表以内)
- 重建状态: < 2秒 (100个迁移以内)
- 文件加载: < 100ms (单个迁移文件)

## 8. 错误处理

### 8.1 错误类型

```python
class MigrationError(Exception):
    """迁移错误基类"""
    pass

class DependencyError(MigrationError):
    """依赖错误"""
    pass

class ConflictError(MigrationError):
    """冲突错误"""
    pass

class ValidationError(MigrationError):
    """验证错误"""
    pass
```

### 8.2 错误处理策略

1. **验证错误**: 在加载迁移文件时立即检测
2. **依赖错误**: 在排序迁移时检测循环依赖
3. **冲突错误**: 在生成迁移时检测编号冲突
4. **提供清晰的错误消息和解决建议**

## 9. 扩展性设计

### 9.1 插件机制

```python
class MigrationPlugin:
    """迁移插件基类"""
    
    def pre_generate(self, context):
        """生成前钩子"""
        pass
    
    def post_generate(self, migration):
        """生成后钩子"""
        pass
    
    def custom_operation(self, operation):
        """自定义操作处理"""
        pass
```

### 9.2 数据库适配器

```python
class DatabaseAdapter:
    """数据库适配器基类"""
    
    def generate_sql(self, operation: Operation) -> str:
        """生成SQL语句"""
        raise NotImplementedError
    
    def map_type(self, column_type: ColumnType) -> str:
        """映射数据类型"""
        raise NotImplementedError

class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL适配器"""
    pass

class MySQLAdapter(DatabaseAdapter):
    """MySQL适配器"""
    pass
```

## 10. 实现计划

### Phase 1: 核心功能 (P0)
1. 数据模型定义 (models.py)
2. 文件管理器 (file_manager.py)
3. 基本的Differ算法
4. 基本的StateBuilder
5. CLI基础框架

### Phase 2: 完整功能 (P1)
1. 完整的操作类型支持
2. 依赖关系管理
3. 命名空间管理
4. 完整的CLI命令

### Phase 3: 高级功能 (P2)
1. 迁移合并 (squash)
2. 数据库适配器
3. 插件机制
4. 性能优化
