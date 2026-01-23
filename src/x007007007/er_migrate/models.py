"""
Migration data models using Pydantic for validation
"""
from typing import List, Optional, Any, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ColumnDefinition(BaseModel):
    """列定义"""
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    default: Optional[Any] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    unique: bool = False
    comment: Optional[str] = None


class IndexDefinition(BaseModel):
    """索引定义"""
    name: str
    columns: List[str]
    unique: bool = False


class ForeignKeyDefinition(BaseModel):
    """外键定义"""
    column_name: str
    reference_table: str
    reference_column: str
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"


# ============ 操作类型定义 ============

class Operation(BaseModel):
    """操作基类"""
    type: str


class CreateTable(Operation):
    """创建表操作"""
    type: Literal["CreateTable"] = "CreateTable"
    table_name: str
    columns: List[ColumnDefinition]


class DropTable(Operation):
    """删除表操作"""
    type: Literal["DropTable"] = "DropTable"
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
    """修改列操作 - 只记录新值"""
    type: Literal["AlterColumn"] = "AlterColumn"
    table_name: str
    column_name: str
    new_type: Optional[str] = None
    new_max_length: Optional[int] = None
    new_nullable: Optional[bool] = None
    new_default: Optional[Any] = None
    new_precision: Optional[int] = None
    new_scale: Optional[int] = None


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
    new_on_delete: Optional[str] = None
    new_on_update: Optional[str] = None


# 联合类型
OperationType = Union[
    CreateTable, DropTable, RenameTable,
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
