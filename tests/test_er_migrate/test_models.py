"""
测试迁移数据模型
"""
import pytest
from pydantic import ValidationError
from x007007007.er_migrate.models import (
    ColumnDefinition,
    IndexDefinition,
    ForeignKeyDefinition,
    CreateTable,
    DropTable,
    AddColumn,
    RemoveColumn,
    AlterColumn,
    AddIndex,
    RemoveIndex,
    AddForeignKey,
    RemoveForeignKey,
    Migration,
)


class TestColumnDefinition:
    """测试列定义模型"""
    
    def test_create_simple_column(self):
        """测试创建简单列"""
        col = ColumnDefinition(name="id", type="uuid", primary_key=True, nullable=False)
        assert col.name == "id"
        assert col.type == "uuid"
        assert col.primary_key is True
        assert col.nullable is False
    
    def test_create_string_column_with_length(self):
        """测试创建带长度的字符串列"""
        col = ColumnDefinition(name="username", type="string", max_length=255)
        assert col.name == "username"
        assert col.max_length == 255
    
    def test_create_decimal_column(self):
        """测试创建decimal列"""
        col = ColumnDefinition(name="price", type="decimal", precision=10, scale=2)
        assert col.precision == 10
        assert col.scale == 2
    
    def test_column_with_default(self):
        """测试带默认值的列"""
        col = ColumnDefinition(name="status", type="string", default="active")
        assert col.default == "active"


class TestIndexDefinition:
    """测试索引定义模型"""
    
    def test_create_simple_index(self):
        """测试创建简单索引"""
        idx = IndexDefinition(name="idx_email", columns=["email"], unique=False)
        assert idx.name == "idx_email"
        assert idx.columns == ["email"]
        assert idx.unique is False
    
    def test_create_composite_index(self):
        """测试创建复合索引"""
        idx = IndexDefinition(
            name="idx_user_created",
            columns=["user_id", "created_at"],
            unique=False
        )
        assert len(idx.columns) == 2
    
    def test_create_unique_index(self):
        """测试创建唯一索引"""
        idx = IndexDefinition(name="idx_username_unique", columns=["username"], unique=True)
        assert idx.unique is True


class TestForeignKeyDefinition:
    """测试外键定义模型"""
    
    def test_create_foreign_key(self):
        """测试创建外键"""
        fk = ForeignKeyDefinition(
            column_name="author_id",
            reference_table="user",
            reference_column="id",
            on_delete="CASCADE"
        )
        assert fk.column_name == "author_id"
        assert fk.reference_table == "user"
        assert fk.on_delete == "CASCADE"
    
    def test_foreign_key_default_behavior(self):
        """测试外键默认行为"""
        fk = ForeignKeyDefinition(
            column_name="user_id",
            reference_table="user",
            reference_column="id"
        )
        assert fk.on_delete == "CASCADE"
        assert fk.on_update == "CASCADE"


class TestOperations:
    """测试操作类型"""
    
    def test_create_table_operation(self):
        """测试创建表操作"""
        op = CreateTable(
            table_name="user",
            columns=[
                ColumnDefinition(name="id", type="uuid", primary_key=True, nullable=False),
                ColumnDefinition(name="username", type="string", max_length=255)
            ]
        )
        assert op.type == "CreateTable"
        assert op.table_name == "user"
        assert len(op.columns) == 2
    
    def test_drop_table_operation(self):
        """测试删除表操作"""
        op = DropTable(table_name="temp_data")
        assert op.type == "DropTable"
        assert op.table_name == "temp_data"
    
    def test_add_column_operation(self):
        """测试添加列操作"""
        op = AddColumn(
            table_name="user",
            column=ColumnDefinition(name="email", type="string", max_length=255)
        )
        assert op.type == "AddColumn"
        assert op.table_name == "user"
        assert op.column.name == "email"
    
    def test_remove_column_operation(self):
        """测试删除列操作"""
        op = RemoveColumn(table_name="user", column_name="deprecated_field")
        assert op.type == "RemoveColumn"
        assert op.column_name == "deprecated_field"
    
    def test_alter_column_operation(self):
        """测试修改列操作 - 只记录新值"""
        op = AlterColumn(
            table_name="user",
            column_name="username",
            new_max_length=200
        )
        assert op.type == "AlterColumn"
        assert op.new_max_length == 200
        assert op.new_type is None  # 未修改的属性为None
    
    def test_alter_column_multiple_changes(self):
        """测试修改列的多个属性"""
        op = AlterColumn(
            table_name="user",
            column_name="email",
            new_max_length=320,
            new_nullable=False
        )
        assert op.new_max_length == 320
        assert op.new_nullable is False
    
    def test_add_index_operation(self):
        """测试添加索引操作"""
        op = AddIndex(
            table_name="user",
            index=IndexDefinition(name="idx_email", columns=["email"], unique=True)
        )
        assert op.type == "AddIndex"
        assert op.index.unique is True
    
    def test_remove_index_operation(self):
        """测试删除索引操作"""
        op = RemoveIndex(table_name="user", index_name="idx_old_index")
        assert op.type == "RemoveIndex"
    
    def test_add_foreign_key_operation(self):
        """测试添加外键操作"""
        op = AddForeignKey(
            table_name="post",
            foreign_key=ForeignKeyDefinition(
                column_name="author_id",
                reference_table="user",
                reference_column="id"
            )
        )
        assert op.type == "AddForeignKey"
        assert op.foreign_key.column_name == "author_id"
    
    def test_remove_foreign_key_operation(self):
        """测试删除外键操作"""
        op = RemoveForeignKey(table_name="post", constraint_name="fk_post_author")
        assert op.type == "RemoveForeignKey"


class TestMigration:
    """测试迁移模型"""
    
    def test_create_migration(self):
        """测试创建迁移"""
        migration = Migration(
            name="initial",
            namespace="blog",
            dependencies=[],
            operations=[
                CreateTable(
                    table_name="user",
                    columns=[
                        ColumnDefinition(name="id", type="uuid", primary_key=True, nullable=False)
                    ]
                )
            ]
        )
        assert migration.name == "initial"
        assert migration.namespace == "blog"
        assert migration.version == "1.0"
        assert len(migration.operations) == 1
    
    def test_migration_with_dependencies(self):
        """测试带依赖的迁移"""
        migration = Migration(
            name="add_posts",
            namespace="blog",
            dependencies=["blog.0001_initial"],
            operations=[]
        )
        assert len(migration.dependencies) == 1
        assert migration.dependencies[0] == "blog.0001_initial"
    
    def test_migration_validation_empty_name(self):
        """测试迁移名称验证 - 空名称"""
        with pytest.raises((ValidationError, AssertionError)):
            Migration(
                name="",
                namespace="blog",
                operations=[]
            )
    
    def test_migration_validation_empty_namespace(self):
        """测试命名空间验证 - 空命名空间"""
        with pytest.raises((ValidationError, AssertionError)):
            Migration(
                name="initial",
                namespace="",
                operations=[]
            )
    
    def test_migration_serialization(self):
        """测试迁移序列化"""
        migration = Migration(
            name="initial",
            namespace="test",
            operations=[
                CreateTable(
                    table_name="user",
                    columns=[
                        ColumnDefinition(name="id", type="uuid", primary_key=True, nullable=False)
                    ]
                )
            ]
        )
        # 转换为字典
        data = migration.model_dump()
        assert data["name"] == "initial"
        assert data["namespace"] == "test"
        assert len(data["operations"]) == 1
    
    def test_migration_deserialization(self):
        """测试迁移反序列化"""
        data = {
            "version": "1.0",
            "name": "initial",
            "namespace": "test",
            "dependencies": [],
            "operations": [
                {
                    "type": "CreateTable",
                    "table_name": "user",
                    "columns": [
                        {
                            "name": "id",
                            "type": "uuid",
                            "primary_key": True,
                            "nullable": False
                        }
                    ]
                }
            ]
        }
        migration = Migration(**data)
        assert migration.name == "initial"
        assert len(migration.operations) == 1
        assert isinstance(migration.operations[0], CreateTable)
