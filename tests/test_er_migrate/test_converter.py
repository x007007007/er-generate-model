"""
测试ER模型转换器
"""
import pytest
from x007007007.er.models import Entity, Column, Relationship, ERModel
from x007007007.er_migrate.converter import ERConverter
from x007007007.er_migrate.models import (
    ColumnDefinition,
    IndexDefinition,
    ForeignKeyDefinition,
)


class TestERConverter:
    """测试ER模型转换器"""
    
    def test_convert_simple_column(self):
        """测试转换简单列"""
        # 创建原始Column
        col = Column(name="id", type="uuid", is_pk=True, nullable=False)
        
        # 转换
        converter = ERConverter()
        col_def = converter.convert_column(col)
        
        # 验证
        assert isinstance(col_def, ColumnDefinition)
        assert col_def.name == "id"
        assert col_def.type == "uuid"
        assert col_def.primary_key is True
        assert col_def.nullable is False
    
    def test_convert_column_with_max_length(self):
        """测试转换带长度的列"""
        col = Column(name="username", type="string", max_length=255)
        
        converter = ERConverter()
        col_def = converter.convert_column(col)
        
        assert col_def.max_length == 255
    
    def test_convert_column_with_unique(self):
        """测试转换唯一列"""
        col = Column(name="email", type="string", unique=True)
        
        converter = ERConverter()
        col_def = converter.convert_column(col)
        
        assert col_def.unique is True
    
    def test_convert_simple_entity(self):
        """测试转换简单实体"""
        entity = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string", max_length=255)
            ]
        )
        
        converter = ERConverter()
        table_name, columns = converter.convert_entity(entity)
        
        assert table_name == "user"  # 应该转换为小写
        assert len(columns) == 2
        assert all(isinstance(col, ColumnDefinition) for col in columns)
    
    def test_convert_entity_name_to_snake_case(self):
        """测试实体名转换为snake_case"""
        entity = Entity(name="UserProfile", columns=[])
        
        converter = ERConverter()
        table_name, _ = converter.convert_entity(entity)
        
        assert table_name == "user_profile"
    
    def test_extract_indexes_from_entity(self):
        """测试从实体提取索引"""
        entity = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", unique=True),
                Column(name="username", type="string", indexed=True)
            ]
        )
        
        converter = ERConverter()
        indexes = converter.extract_indexes(entity)
        
        # 应该有2个索引：email的唯一索引和username的普通索引
        assert len(indexes) == 2
        assert all(isinstance(idx, IndexDefinition) for idx in indexes)
        
        # 验证唯一索引
        unique_idx = next(idx for idx in indexes if idx.unique)
        assert "email" in unique_idx.columns
        
        # 验证普通索引
        normal_idx = next(idx for idx in indexes if not idx.unique)
        assert "username" in normal_idx.columns
    
    def test_convert_relationship_to_foreign_key(self):
        """测试转换关系为外键"""
        rel = Relationship(
            left_entity="Post",
            right_entity="User",
            relation_type="many-to-one",
            left_column="author_id",
            right_column="id"
        )
        
        converter = ERConverter()
        fk = converter.convert_relationship(rel)
        
        assert isinstance(fk, ForeignKeyDefinition)
        assert fk.column_name == "author_id"
        assert fk.reference_table == "user"
        assert fk.reference_column == "id"
    
    def test_convert_full_er_model(self):
        """测试转换完整的ER模型"""
        # 创建ER模型
        er_model = ERModel()
        
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string", max_length=255, unique=True)
            ]
        )
        er_model.add_entity(user)
        
        post = Entity(
            name="Post",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="author_id", type="uuid", is_fk=True),
                Column(name="title", type="string", max_length=255)
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
        
        # 转换
        converter = ERConverter()
        result = converter.convert_model(er_model)
        
        # 验证结果
        assert "tables" in result
        assert "foreign_keys" in result
        assert len(result["tables"]) == 2
        assert len(result["foreign_keys"]) == 1
        
        # 验证表
        assert "user" in result["tables"]
        assert "post" in result["tables"]
        
        # 验证外键
        fk = result["foreign_keys"][0]
        assert fk.column_name == "author_id"
        assert fk.reference_table == "user"
