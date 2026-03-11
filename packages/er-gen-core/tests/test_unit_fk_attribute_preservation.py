"""
Unit Tests for Foreign Key Column Attribute Preservation

These tests verify that when a column is marked as a foreign key,
all its other attributes (nullable, unique, indexed, default, comment)
are preserved and rendered correctly in the generated SQLAlchemy code.

Requirements: 2.3
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestForeignKeyAttributePreservation:
    """Test that FK columns preserve all attributes."""
    
    def test_fk_preserves_nullable_true(self):
        """
        Test that nullable=True is preserved in FK column.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="integer",
                    db_column="parent_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify nullable=True is in the FK column definition
        assert "parent_id = Column(" in generated_code
        assert "nullable=True" in generated_code
        
        # Verify it's in the context of parent_id
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                # Check this line and next few lines for nullable
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                assert 'nullable=True' in column_def, \
                    "FK column should preserve nullable=True"
                break
    
    def test_fk_preserves_nullable_false(self):
        """
        Test that nullable=False is preserved in FK column.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="integer",
                    db_column="parent_id",
                    nullable=False,  # Required FK
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify nullable=False is in the FK column definition
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                assert 'nullable=False' in column_def, \
                    "FK column should preserve nullable=False"
                break
    
    def test_fk_preserves_unique(self):
        """
        Test that unique=True is preserved in FK column.
        
        This is useful for one-to-one relationships where the FK
        should be unique.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="integer",
                    db_column="parent_id",
                    nullable=True,
                    unique=True,  # One-to-one relationship
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-one",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify unique=True is in the FK column definition
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                assert 'unique=True' in column_def, \
                    "FK column should preserve unique=True"
                break
    
    def test_fk_preserves_indexed(self):
        """
        Test that indexed=True is preserved in FK column.
        
        Foreign keys are often indexed for performance.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="integer",
                    db_column="parent_id",
                    nullable=True,
                    indexed=True,  # Index for performance
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify index=True is in the FK column definition
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                assert 'index=True' in column_def, \
                    "FK column should preserve index=True"
                break
    
    def test_fk_preserves_default(self):
        """
        Test that default value is preserved in FK column.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="integer",
                    db_column="parent_id",
                    nullable=True,
                    default="1",  # Default to parent with id=1
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify default is in the FK column definition
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                assert 'default=' in column_def, \
                    "FK column should preserve default value"
                break
    
    def test_fk_preserves_comment(self):
        """
        Test that comment is preserved in FK column.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="integer",
                    db_column="parent_id",
                    nullable=True,
                    comment="Reference to parent entity",
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify comment is in the FK column definition
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                assert 'comment=' in column_def, \
                    "FK column should preserve comment"
                assert 'Reference to parent entity' in column_def, \
                    "FK column comment should contain the correct text"
                break
    
    def test_fk_preserves_multiple_attributes(self):
        """
        Test that multiple attributes are preserved together in FK column.
        
        This is the most realistic scenario where a FK has several
        attributes that all need to be preserved.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="bigint",
                    db_column="parent_id",
                    nullable=False,  # Required
                    unique=True,     # One-to-one
                    indexed=True,    # Indexed for performance
                    comment="Parent reference with constraints",
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-one",
            left_column="id",
            right_column="parent_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify all attributes are in the FK column definition
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'parent_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                
                # Check all attributes
                assert 'nullable=False' in column_def, \
                    "FK column should preserve nullable=False"
                assert 'unique=True' in column_def, \
                    "FK column should preserve unique=True"
                assert 'index=True' in column_def, \
                    "FK column should preserve index=True"
                assert 'comment=' in column_def, \
                    "FK column should preserve comment"
                
                # Verify ForeignKey is also present
                assert 'ForeignKey' in column_def, \
                    "FK column should include ForeignKey constraint"
                break
    
    def test_fk_attributes_dont_override_foreign_key_constraint(self):
        """
        Test that column attributes don't interfere with ForeignKey constraint.
        
        This verifies that the ForeignKey constraint is correctly rendered
        alongside all the column attributes.
        
        Requirements: 2.3
        """
        parent_entity = Entity(
            name="Category",
            table_name="category",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Product",
            table_name="product",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="category",
                    type="integer",
                    db_column="category_id",
                    nullable=True,
                    indexed=True,
                    comment="Product category",
                    is_fk=True
                )
            ]
        )
        
        relationship = Relationship(
            left_entity="Category",
            right_entity="Product",
            relation_type="one-to-many",
            left_column="id",
            right_column="category_id"
        )
        
        model = ERModel(
            entities={"Category": parent_entity, "Product": child_entity},
            relationships=[relationship]
        )
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify ForeignKey constraint is present
        assert "ForeignKey('category.id')" in generated_code or \
               'ForeignKey("category.id")' in generated_code, \
            "FK constraint should be present"
        
        # Verify attributes are also present
        assert "nullable=True" in generated_code
        assert "index=True" in generated_code
        assert "comment=" in generated_code
        
        # Verify the column definition has both ForeignKey and attributes
        lines = generated_code.split('\n')
        for i, line in enumerate(lines):
            if 'category_id = Column(' in line:
                column_def = line
                j = i + 1
                while j < len(lines) and ')' not in column_def:
                    column_def += lines[j]
                    j += 1
                
                # Both ForeignKey and attributes should be in the same definition
                assert 'ForeignKey' in column_def
                assert 'nullable=True' in column_def
                assert 'index=True' in column_def
                break
