"""
测试ER差异检测器
"""
import pytest
from x007007007.er.models import Entity, Column, ERModel
from x007007007.er_migrate.differ import ERDiffer
from x007007007.er_migrate.models import (
    CreateTable,
    DropTable,
    AddColumn,
    RemoveColumn,
    AlterColumn,
    AddIndex,
    RemoveIndex,
)


class TestTableOperations:
    """测试表操作检测"""
    
    def test_detect_new_table(self):
        """T-001: 检测新增表"""
        old_model = ERModel()
        
        new_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True, nullable=False),
                Column(name="username", type="string")
            ]
        )
        new_model.add_entity(user)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到CreateTable操作
        assert len(operations) == 1
        assert isinstance(operations[0], CreateTable)
        assert operations[0].table_name == "user"
        assert len(operations[0].columns) == 2
    
    def test_detect_dropped_table(self):
        """T-002: 检测删除表"""
        old_model = ERModel()
        user = Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)])
        temp = Entity(name="TempData", columns=[Column(name="id", type="uuid", is_pk=True)])
        old_model.add_entity(user)
        old_model.add_entity(temp)
        
        new_model = ERModel()
        user_new = Entity(name="User", columns=[Column(name="id", type="uuid", is_pk=True)])
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到DropTable操作
        drop_ops = [op for op in operations if isinstance(op, DropTable)]
        assert len(drop_ops) == 1
        assert drop_ops[0].table_name == "temp_data"
    
    def test_no_changes(self):
        """S-004: 检测无变更"""
        model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        )
        model.add_entity(user)
        
        # 创建相同的模型
        model2 = ERModel()
        user2 = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        )
        model2.add_entity(user2)
        
        differ = ERDiffer()
        operations = differ.diff(model, model2)
        
        # 应该没有变更
        assert len(operations) == 0


class TestColumnOperations:
    """测试列操作检测"""
    
    def test_detect_added_column(self):
        """C-001: 检测新增列"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string"),
                Column(name="email", type="string", nullable=True)
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到AddColumn操作
        add_col_ops = [op for op in operations if isinstance(op, AddColumn)]
        assert len(add_col_ops) == 1
        assert add_col_ops[0].table_name == "user"
        assert add_col_ops[0].column.name == "email"
        assert add_col_ops[0].column.nullable is True
    
    def test_detect_removed_column(self):
        """C-003: 检测删除列"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string"),
                Column(name="deprecated_field", type="string")
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到RemoveColumn操作
        remove_col_ops = [op for op in operations if isinstance(op, RemoveColumn)]
        assert len(remove_col_ops) == 1
        assert remove_col_ops[0].table_name == "user"
        assert remove_col_ops[0].column_name == "deprecated_field"
    
    def test_detect_column_type_change(self):
        """C-005: 检测列类型变更"""
        old_model = ERModel()
        product = Entity(
            name="Product",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="price", type="int")
            ]
        )
        old_model.add_entity(product)
        
        new_model = ERModel()
        product_new = Entity(
            name="Product",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="price", type="decimal")
            ]
        )
        new_model.add_entity(product_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到AlterColumn操作
        alter_col_ops = [op for op in operations if isinstance(op, AlterColumn)]
        assert len(alter_col_ops) == 1
        assert alter_col_ops[0].table_name == "product"
        assert alter_col_ops[0].column_name == "price"
        assert alter_col_ops[0].new_type == "decimal"
    
    def test_detect_column_length_change(self):
        """C-006: 检测字符串长度变更"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=100)
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", max_length=200)
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到AlterColumn操作
        alter_col_ops = [op for op in operations if isinstance(op, AlterColumn)]
        assert len(alter_col_ops) == 1
        assert alter_col_ops[0].column_name == "username"
        assert alter_col_ops[0].new_max_length == 200
    
    def test_detect_nullable_change(self):
        """C-007: 检测可空性变更"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", nullable=True)
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", nullable=False)
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到AlterColumn操作
        alter_col_ops = [op for op in operations if isinstance(op, AlterColumn)]
        assert len(alter_col_ops) == 1
        assert alter_col_ops[0].new_nullable is False


class TestIndexOperations:
    """测试索引操作检测"""
    
    def test_detect_added_index(self):
        """I-001: 检测新增索引"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string")
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", indexed=True)
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到AddIndex操作
        add_idx_ops = [op for op in operations if isinstance(op, AddIndex)]
        assert len(add_idx_ops) == 1
        assert add_idx_ops[0].table_name == "user"
        assert "email" in add_idx_ops[0].index.columns
    
    def test_detect_removed_index(self):
        """I-003: 检测删除索引"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string", indexed=True)
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="email", type="string")
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到RemoveIndex操作
        remove_idx_ops = [op for op in operations if isinstance(op, RemoveIndex)]
        assert len(remove_idx_ops) == 1
        assert remove_idx_ops[0].table_name == "user"
    
    def test_detect_unique_index(self):
        """I-004: 检测唯一索引"""
        old_model = ERModel()
        user = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string")
            ]
        )
        old_model.add_entity(user)
        
        new_model = ERModel()
        user_new = Entity(
            name="User",
            columns=[
                Column(name="id", type="uuid", is_pk=True),
                Column(name="username", type="string", unique=True)
            ]
        )
        new_model.add_entity(user_new)
        
        differ = ERDiffer()
        operations = differ.diff(old_model, new_model)
        
        # 应该检测到AddIndex操作，且为唯一索引
        add_idx_ops = [op for op in operations if isinstance(op, AddIndex)]
        assert len(add_idx_ops) == 1
        assert add_idx_ops[0].index.unique is True
