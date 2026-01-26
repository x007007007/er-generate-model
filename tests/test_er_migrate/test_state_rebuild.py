"""
测试状态重建功能 - 确保generator._rebuild_state正确应用所有操作类型

这个测试文件专门测试MigrationGenerator._rebuild_state方法是否正确处理所有操作类型。
每个操作类型都应该有对应的测试，确保：
1. 操作被正确应用到重建的状态中
2. 重复运行相同模型不会产生重复的迁移

测试分类：
- 表操作 (Table Operations): CreateTable, DropTable, RenameTable
- 列操作 (Column Operations): AddColumn, RemoveColumn, AlterColumn, RenameColumn
- 索引操作 (Index Operations): AddIndex, RemoveIndex
- 外键操作 (Foreign Key Operations): AddForeignKey, RemoveForeignKey, AlterForeignKey
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er_migrate.generator import MigrationGenerator
from x007007007.er_migrate.file_manager import FileManager


class TestStateRebuildTableOperations:
    """测试状态重建 - 表操作"""
    
    def test_rebuild_applies_create_table(self, tmp_path):
        """测试重建状态时应用CreateTable操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表
        model = ERModel()
        model.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model)
        assert migration1 is not None
        fm.save_migration(migration1)
        
        # 重建状态
        rebuilt = generator._rebuild_state("test")
        assert "User" in rebuilt.entities
        assert len(rebuilt.entities["User"].columns) == 2
        
        # 重复运行不应该生成新迁移
        migration2 = generator.generate("test", model)
        assert migration2 is None

    
    def test_rebuild_applies_drop_table(self, tmp_path):
        """测试重建状态时应用DropTable操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建两个表
        model1 = ERModel()
        model1.add_entity(Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)]))
        model1.add_entity(Entity(name="Post", columns=[Column(name="id", type="uuid", is_pk=True)]))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 删除Post表
        model2 = ERModel()
        model2.add_entity(Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)]))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        drop_ops = [op for op in migration2.operations if op.type == "DropTable"]
        assert len(drop_ops) == 1
        fm.save_migration(migration2)
        
        # 重建状态应该只有User表
        rebuilt = generator._rebuild_state("test")
        assert "User" in rebuilt.entities
        assert "Post" not in rebuilt.entities
        
        # 重复运行不应该生成新迁移
        migration3 = generator.generate("test", model2)
        assert migration3 is None
    
    def test_rebuild_applies_drop_table_repeated_runs(self, tmp_path):
        """Bug修复: 删除表后重复运行不会产生重复的DropTable操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建3个表
        model1 = ERModel()
        for name in ["User", "Post", "Comment"]:
            model1.add_entity(Entity(name=name, columns=[Column(name="id", type="uuid", is_pk=True)]))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 只保留User表
        model2 = ERModel()
        model2.add_entity(Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)]))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重复运行10次
        for i in range(10):
            migration = generator.generate("test", model2)
            assert migration is None, f"第{i+1}次重复运行不应该生成新迁移"
        
        # 验证只有2个迁移文件
        files = fm.list_migration_files("test")
        assert len(files) == 2


class TestStateRebuildColumnOperations:
    """测试状态重建 - 列操作"""
    
    def test_rebuild_applies_add_column(self, tmp_path):
        """测试重建状态时应用AddColumn操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[Column(name="id", type="uuid", is_pk=True)]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 添加列
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重建状态应该包含email列
        rebuilt = generator._rebuild_state("test")
        user_columns = [col.name for col in rebuilt.entities["User"].columns]
        assert "email" in user_columns
        
        # 重复运行不应该生成新迁移
        migration3 = generator.generate("test", model2)
        assert migration3 is None
    
    def test_rebuild_applies_remove_column(self, tmp_path):
        """测试重建状态时应用RemoveColumn操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表（3列）
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string"),
                Column(name="email", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 删除email列
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重建状态不应该包含email列
        rebuilt = generator._rebuild_state("test")
        user_columns = [col.name for col in rebuilt.entities["User"].columns]
        assert "email" not in user_columns
        assert len(user_columns) == 2
        
        # 重复运行不应该生成新迁移
        migration3 = generator.generate("test", model2)
        assert migration3 is None

    
    def test_rebuild_applies_remove_multiple_columns(self, tmp_path):
        """测试重建状态时应用多个RemoveColumn操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表（4列）
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string"),
                Column(name="email", type="string"),
                Column(name="phone", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 删除email和phone列
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重建状态应该只有2列
        rebuilt = generator._rebuild_state("test")
        user_columns = [col.name for col in rebuilt.entities["User"].columns]
        assert len(user_columns) == 2
        assert "email" not in user_columns
        assert "phone" not in user_columns
        
        # 重复运行5次不应该生成新迁移
        for i in range(5):
            migration = generator.generate("test", model2)
            assert migration is None, f"第{i+1}次重复运行不应该生成新迁移"
    
    def test_rebuild_applies_alter_column_type(self, tmp_path):
        """测试重建状态时应用AlterColumn的类型修改"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表（price是int）
        model1 = ERModel()
        model1.add_entity(Entity(
            name="Product",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="price", type="int")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 修改price为decimal
        model2 = ERModel()
        model2.add_entity(Entity(
            name="Product",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="price", type="decimal")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        alter_ops = [op for op in migration2.operations if op.type == "AlterColumn"]
        assert len(alter_ops) == 1
        fm.save_migration(migration2)
        
        # 重建状态应该有decimal类型
        rebuilt = generator._rebuild_state("test")
        price_col = next(col for col in rebuilt.entities["Product"].columns if col.name == "price")
        assert price_col.type == "decimal"
        
        # 重复运行不应该生成新迁移
        migration3 = generator.generate("test", model2)
        assert migration3 is None
    
    def test_rebuild_applies_alter_column_max_length(self, tmp_path):
        """测试重建状态时应用AlterColumn的max_length修改"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表（username没有max_length）
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 添加max_length=100
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=100)
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重建状态应该有max_length=100
        rebuilt = generator._rebuild_state("test")
        username_col = next(col for col in rebuilt.entities["User"].columns if col.name == "username")
        assert username_col.max_length == 100
        
        # 重复运行5次不应该生成新迁移
        for i in range(5):
            migration = generator.generate("test", model2)
            assert migration is None, f"第{i+1}次重复运行不应该生成新迁移"

    
    def test_rebuild_applies_alter_column_nullable(self, tmp_path):
        """测试重建状态时应用AlterColumn的nullable修改"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表（email可空）
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", nullable=True)
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 修改为不可空
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", nullable=False)
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重建状态应该是不可空
        rebuilt = generator._rebuild_state("test")
        email_col = next(col for col in rebuilt.entities["User"].columns if col.name == "email")
        assert email_col.nullable == False
        
        # 重复运行不应该生成新迁移
        migration3 = generator.generate("test", model2)
        assert migration3 is None
    
    def test_rebuild_applies_alter_column_precision_scale(self, tmp_path):
        """测试重建状态时应用AlterColumn的precision和scale修改"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建表（price没有precision/scale）
        model1 = ERModel()
        model1.add_entity(Entity(
            name="Product",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="price", type="decimal")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 添加precision=10, scale=2
        model2 = ERModel()
        model2.add_entity(Entity(
            name="Product",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="price", type="decimal", precision=10, scale=2)
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        fm.save_migration(migration2)
        
        # 重建状态应该有precision和scale
        rebuilt = generator._rebuild_state("test")
        price_col = next(col for col in rebuilt.entities["Product"].columns if col.name == "price")
        assert price_col.precision == 10
        assert price_col.scale == 2
        
        # 重复运行不应该生成新迁移
        migration3 = generator.generate("test", model2)
        assert migration3 is None
    
    def test_rebuild_applies_multiple_alter_columns(self, tmp_path):
        """测试重建状态时应用多个AlterColumn操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 版本1: 初始状态
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string"),
                Column(name="age", type="int")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 版本2: 修改username的max_length
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=50),
                Column(name="age", type="int")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        fm.save_migration(migration2)
        
        # 版本3: 修改age的类型
        model3 = ERModel()
        model3.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=50),
                Column(name="age", type="smallint")
            ]
        ))
        
        migration3 = generator.generate("test", model3)
        assert migration3 is not None
        fm.save_migration(migration3)
        
        # 重建状态应该包含所有修改
        rebuilt = generator._rebuild_state("test")
        username_col = next(col for col in rebuilt.entities["User"].columns if col.name == "username")
        age_col = next(col for col in rebuilt.entities["User"].columns if col.name == "age")
        assert username_col.max_length == 50
        assert age_col.type == "smallint"
        
        # 重复运行不应该生成新迁移
        migration4 = generator.generate("test", model3)
        assert migration4 is None



class TestStateRebuildForeignKeyOperations:
    """测试状态重建 - 外键操作"""
    
    def test_rebuild_applies_add_foreign_key(self, tmp_path):
        """测试重建状态时应用AddForeignKey操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建带关系的模型
        model = ERModel()
        model.add_entity(Entity(
            name="User",
            columns=[Column(name="id", type="uuid", is_pk=True)]
        ))
        model.add_entity(Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="author_id", type="uuid", is_fk=True)
            ]
        ))
        model.add_relationship(Relationship(
            left_entity="Post",
            right_entity="User",
            relation_type="many-to-one",
            left_column="author_id",
            right_column="id"
        ))
        
        migration1 = generator.generate("test", model)
        assert migration1 is not None
        fm.save_migration(migration1)
        
        # 重建状态应该包含关系
        rebuilt = generator._rebuild_state("test")
        assert len(rebuilt.relationships) > 0
        
        # 重复运行不应该生成新迁移（特别是不应该重复生成外键）
        migration2 = generator.generate("test", model)
        assert migration2 is None, "不应该重复生成外键"
    
    def test_rebuild_applies_add_foreign_key_repeated_runs(self, tmp_path):
        """Bug修复: 添加外键后重复运行不会产生重复的AddForeignKey操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建带关系的模型
        model = ERModel()
        model.add_entity(Entity(
            name="User",
            columns=[Column(name="id", type="uuid", is_pk=True)]
        ))
        model.add_entity(Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="author_id", type="uuid", is_fk=True)
            ]
        ))
        model.add_relationship(Relationship(
            left_entity="Post",
            right_entity="User",
            relation_type="many-to-one",
            left_column="author_id",
            right_column="id"
        ))
        
        migration1 = generator.generate("test", model)
        fm.save_migration(migration1)
        
        # 重复运行10次
        for i in range(10):
            migration = generator.generate("test", model)
            assert migration is None, f"第{i+1}次重复运行不应该生成新迁移"
        
        # 验证只有1个迁移文件
        files = fm.list_migration_files("test")
        assert len(files) == 1


class TestStateRebuildComplexScenarios:
    """测试状态重建 - 复杂场景"""
    
    def test_rebuild_applies_mixed_operations(self, tmp_path):
        """测试重建状态时应用混合操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 版本1: 创建User表
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 版本2: 添加email列
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string"),
                Column(name="email", type="string")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        fm.save_migration(migration2)
        
        # 版本3: 修改username的max_length，删除email，添加Post表
        model3 = ERModel()
        model3.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=100)
            ]
        ))
        model3.add_entity(Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="title", type="string")
            ]
        ))
        
        migration3 = generator.generate("test", model3)
        assert migration3 is not None
        fm.save_migration(migration3)
        
        # 重建状态应该正确
        rebuilt = generator._rebuild_state("test")
        assert "User" in rebuilt.entities
        assert "Post" in rebuilt.entities
        user_columns = [col.name for col in rebuilt.entities["User"].columns]
        assert "email" not in user_columns
        username_col = next(col for col in rebuilt.entities["User"].columns if col.name == "username")
        assert username_col.max_length == 100
        
        # 重复运行不应该生成新迁移
        migration4 = generator.generate("test", model3)
        assert migration4 is None

    
    def test_rebuild_drop_and_recreate_table(self, tmp_path):
        """测试删除表后重新创建同名表"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 版本1: 创建Post表
        model1 = ERModel()
        model1.add_entity(Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="title", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 版本2: 删除Post表
        model2 = ERModel()
        migration2 = generator.generate("test", model2)
        assert migration2 is not None
        drop_ops = [op for op in migration2.operations if op.type == "DropTable"]
        assert len(drop_ops) == 1
        fm.save_migration(migration2)
        
        # 版本3: 重新创建Post表（但结构不同）
        model3 = ERModel()
        model3.add_entity(Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="content", type="text")  # 不同的列
            ]
        ))
        
        migration3 = generator.generate("test", model3)
        assert migration3 is not None
        create_ops = [op for op in migration3.operations if op.type == "CreateTable"]
        assert len(create_ops) == 1
        fm.save_migration(migration3)
        
        # 重建状态应该有新的Post表
        rebuilt = generator._rebuild_state("test")
        assert "Post" in rebuilt.entities
        post_columns = [col.name for col in rebuilt.entities["Post"].columns]
        assert "content" in post_columns
        assert "title" not in post_columns
        
        # 重复运行不应该生成新迁移
        migration4 = generator.generate("test", model3)
        assert migration4 is None
    
    def test_rebuild_add_remove_add_column(self, tmp_path):
        """测试添加列、删除列、再添加列的场景"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 版本1: 只有id
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[Column(name="id", type="uuid", is_pk=True)]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 版本2: 添加email
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string")
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        fm.save_migration(migration2)
        
        # 版本3: 删除email
        model3 = ERModel()
        model3.add_entity(Entity(
            name="User",
            columns=[Column(name="id", type="uuid", is_pk=True)]
        ))
        
        migration3 = generator.generate("test", model3)
        fm.save_migration(migration3)
        
        # 版本4: 再次添加email（可能类型不同）
        model4 = ERModel()
        model4.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="text")  # 不同类型
            ]
        ))
        
        migration4 = generator.generate("test", model4)
        assert migration4 is not None
        add_ops = [op for op in migration4.operations if op.type == "AddColumn"]
        assert len(add_ops) == 1
        fm.save_migration(migration4)
        
        # 重建状态应该有email列（text类型）
        rebuilt = generator._rebuild_state("test")
        email_col = next(col for col in rebuilt.entities["User"].columns if col.name == "email")
        assert email_col.type == "text"
        
        # 重复运行不应该生成新迁移
        migration5 = generator.generate("test", model4)
        assert migration5 is None
    
    def test_rebuild_sequential_alter_columns(self, tmp_path):
        """测试连续多次修改同一列"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 版本1: username是string
        model1 = ERModel()
        model1.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 版本2: 添加max_length=50
        model2 = ERModel()
        model2.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=50)
            ]
        ))
        
        migration2 = generator.generate("test", model2)
        fm.save_migration(migration2)
        
        # 版本3: 修改max_length=100
        model3 = ERModel()
        model3.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=100)
            ]
        ))
        
        migration3 = generator.generate("test", model3)
        fm.save_migration(migration3)
        
        # 版本4: 修改为不可空
        model4 = ERModel()
        model4.add_entity(Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=100, nullable=False)
            ]
        ))
        
        migration4 = generator.generate("test", model4)
        fm.save_migration(migration4)
        
        # 重建状态应该有最终的属性
        rebuilt = generator._rebuild_state("test")
        username_col = next(col for col in rebuilt.entities["User"].columns if col.name == "username")
        assert username_col.max_length == 100
        assert username_col.nullable == False
        
        # 重复运行不应该生成新迁移
        migration5 = generator.generate("test", model4)
        assert migration5 is None

    
    def test_rebuild_applies_rename_table(self, tmp_path):
        """测试重建状态时应用RenameTable操作"""
        generator = MigrationGenerator(str(tmp_path))
        fm = FileManager(str(tmp_path))
        
        # 创建Post表
        model1 = ERModel()
        model1.add_entity(Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="title", type="string")
            ]
        ))
        
        migration1 = generator.generate("test", model1)
        fm.save_migration(migration1)
        
        # 重命名为Article（需要手动创建RenameTable操作，因为differ可能检测为Drop+Create）
        from x007007007.er_migrate.models import Migration, RenameTable
        migration2 = Migration(
            version="1.0",
            name="rename_post_to_article",
            namespace="test",
            dependencies=["test.0001_initial"],
            operations=[
                RenameTable(old_name="post", new_name="article")
            ]
        )
        fm.save_migration(migration2)
        
        # 重建状态应该有Article表，没有Post表
        rebuilt = generator._rebuild_state("test")
        assert "Article" in rebuilt.entities
        assert "Post" not in rebuilt.entities
        
        # 验证Article表的列
        article_columns = [col.name for col in rebuilt.entities["Article"].columns]
        assert "id" in article_columns
        assert "title" in article_columns
