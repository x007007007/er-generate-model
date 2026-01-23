"""
测试迁移生成器
"""
import pytest
from pathlib import Path
from x007007007.er.models import Entity, Column, Relationship, ERModel
from x007007007.er_migrate.generator import MigrationGenerator
from x007007007.er_migrate.file_manager import FileManager
from x007007007.er_migrate.models import (
    CreateTable,
    AddColumn,
    AddForeignKey,
    AddIndex,
)


class TestMigrationGenerator:
    """测试迁移生成器"""
    
    def test_generate_initial_migration(self, tmp_path):
        """测试生成初始迁移"""
        # 创建ER模型
        er_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string", max_length=255)
            ]
        )
        er_model.add_entity(user)
        
        # 生成迁移
        generator = MigrationGenerator(str(tmp_path))
        migration = generator.generate("blog", er_model)
        
        # 验证迁移
        assert migration is not None
        assert migration.name == "initial"
        assert migration.namespace == "blog"
        assert len(migration.dependencies) == 0
        
        # 验证操作
        assert len(migration.operations) == 1
        assert isinstance(migration.operations[0], CreateTable)
        assert migration.operations[0].table_name == "user"
    
    def test_generate_migration_with_changes(self, tmp_path):
        """测试生成带变更的迁移"""
        # 创建初始ER模型
        initial_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string")
            ]
        )
        initial_model.add_entity(user)
        
        # 生成初始迁移
        generator = MigrationGenerator(str(tmp_path))
        migration1 = generator.generate("blog", initial_model)
        
        # 保存迁移
        fm = FileManager(str(tmp_path))
        fm.save_migration(migration1)
        
        # 创建更新后的ER模型（添加email列）
        updated_model = ERModel()
        user_updated = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string"),
                Column(name="email", type="string", nullable=True)
            ]
        )
        updated_model.add_entity(user_updated)
        
        # 生成新迁移
        migration2 = generator.generate("blog", updated_model)
        
        # 验证迁移
        assert migration2 is not None
        assert migration2.name == "add_email"
        assert migration2.namespace == "blog"
        assert "blog.0001_initial" in migration2.dependencies
        
        # 验证操作
        add_col_ops = [op for op in migration2.operations if isinstance(op, AddColumn)]
        assert len(add_col_ops) == 1
        assert add_col_ops[0].column.name == "email"
    
    def test_no_changes_returns_none(self, tmp_path):
        """测试无变更时返回None"""
        # 创建ER模型
        er_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False)
            ]
        )
        er_model.add_entity(user)
        
        # 生成初始迁移
        generator = MigrationGenerator(str(tmp_path))
        migration1 = generator.generate("blog", er_model)
        
        # 保存迁移
        fm = FileManager(str(tmp_path))
        fm.save_migration(migration1)
        
        # 使用相同的ER模型再次生成
        migration2 = generator.generate("blog", er_model)
        
        # 应该返回None（没有变更）
        assert migration2 is None
    
    def test_generate_migration_with_relationship(self, tmp_path):
        """测试生成带关系的迁移"""
        # 创建ER模型
        er_model = ERModel()
        
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string")
            ]
        )
        er_model.add_entity(user)
        
        post = Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="author_id", type="uuid", is_fk=True),
                Column(name="title", type="string")
            ]
        )
        er_model.add_entity(post)
        
        rel = Relationship(
            left_entity="Post",
            right_entity="User",
            relation_type="many-to-one",
            left_column="author_id",
            right_column="id"
        )
        er_model.add_relationship(rel)
        
        # 生成迁移
        generator = MigrationGenerator(str(tmp_path))
        migration = generator.generate("blog", er_model)
        
        # 验证迁移
        assert migration is not None
        
        # 应该有2个CreateTable和1个AddForeignKey
        create_table_ops = [op for op in migration.operations if isinstance(op, CreateTable)]
        add_fk_ops = [op for op in migration.operations if isinstance(op, AddForeignKey)]
        
        assert len(create_table_ops) == 2
        assert len(add_fk_ops) == 1
        assert add_fk_ops[0].foreign_key.column_name == "author_id"
    
    def test_generate_migration_with_indexes(self, tmp_path):
        """测试生成带索引的迁移"""
        # 创建ER模型
        er_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="email", type="string", unique=True),
                Column(name="username", type="string", indexed=True)
            ]
        )
        er_model.add_entity(user)
        
        # 生成迁移
        generator = MigrationGenerator(str(tmp_path))
        migration = generator.generate("blog", er_model)
        
        # 验证迁移
        assert migration is not None
        
        # 应该有1个CreateTable和2个AddIndex
        create_table_ops = [op for op in migration.operations if isinstance(op, CreateTable)]
        add_idx_ops = [op for op in migration.operations if isinstance(op, AddIndex)]
        
        assert len(create_table_ops) == 1
        assert len(add_idx_ops) == 2
        
        # 验证唯一索引
        unique_idx = next(op for op in add_idx_ops if op.index.unique)
        assert "email" in unique_idx.index.columns
        
        # 验证普通索引
        normal_idx = next(op for op in add_idx_ops if not op.index.unique)
        assert "username" in normal_idx.index.columns
    
    def test_auto_generate_migration_name(self, tmp_path):
        """测试自动生成迁移名称"""
        # 创建ER模型（添加email列）
        er_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string")
            ]
        )
        er_model.add_entity(user)
        
        # 生成迁移
        generator = MigrationGenerator(str(tmp_path))
        migration = generator.generate("blog", er_model)
        
        # 验证名称（应该根据操作自动生成）
        assert migration.name in ["initial", "create_user", "add_user"]
    
    def test_calculate_dependencies(self, tmp_path):
        """测试计算依赖关系"""
        # 创建初始迁移
        initial_model = ERModel()
        user = Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)])
        initial_model.add_entity(user)
        
        generator = MigrationGenerator(str(tmp_path))
        migration1 = generator.generate("blog", initial_model)
        
        fm = FileManager(str(tmp_path))
        fm.save_migration(migration1)
        
        # 创建第二个迁移
        updated_model = ERModel()
        user_updated = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        )
        updated_model.add_entity(user_updated)
        
        migration2 = generator.generate("blog", updated_model)
        
        # 验证依赖
        assert len(migration2.dependencies) == 1
        assert migration2.dependencies[0] == "blog.0001_initial"
    
    def test_multiple_namespaces(self, tmp_path):
        """测试多个命名空间"""
        # 创建auth命名空间的迁移
        auth_model = ERModel()
        user = Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)])
        auth_model.add_entity(user)
        
        generator = MigrationGenerator(str(tmp_path))
        auth_migration = generator.generate("auth", auth_model)
        
        fm = FileManager(str(tmp_path))
        fm.save_migration(auth_migration)
        
        # 创建blog命名空间的迁移
        blog_model = ERModel()
        post = Entity(name="Post", columns=[Column(name="id", type="uuid", is_pk=True)])
        blog_model.add_entity(post)
        
        blog_migration = generator.generate("blog", blog_model)
        
        # 验证两个命名空间独立
        assert auth_migration.namespace == "auth"
        assert blog_migration.namespace == "blog"
        assert len(blog_migration.dependencies) == 0  # blog不依赖auth
