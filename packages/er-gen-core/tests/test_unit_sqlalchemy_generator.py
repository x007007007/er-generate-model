"""
Unit Tests for SQLAlchemy Generator Fixes

These tests verify specific scenarios for the SQLAlchemy generator fixes:
- Primary key column generation
- Foreign key field naming
- Foreign key type mapping
- Nullable foreign key generation
- Reverse relationship foreign_keys parameter
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestPrimaryKeyColumnGeneration:
    """Test primary key column generation with primary_key=True parameter."""
    
    def test_primary_key_column_includes_primary_key_parameter(self):
        """
        Test that a column with primary_key=True generates correct SQLAlchemy code.
        
        Verifies:
        - Generated code includes `primary_key=True`
        - Generated code includes `autoincrement=True`
        """
        # Create entity with primary key column
        entity = Entity(
            name="TestEntity",
            columns=[
                Column(
                    name="id",
                    type="integer",
                    db_column="id",
                    is_pk=True,
                    nullable=False,
                    unique=True
                )
            ],
            table_name="test_entity"
        )
        model = ERModel(entities={"TestEntity": entity}, relationships=[], templates={})
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify primary_key=True is present
        assert "primary_key=True" in result, \
            "Primary key column should include 'primary_key=True' parameter"
        
        # Verify autoincrement=True is present
        assert "autoincrement=True" in result, \
            "Primary key column should include 'autoincrement=True' parameter"
    
    def test_primary_key_foreign_key_column(self):
        """
        Test edge case: column that is both primary key and foreign key.
        
        Verifies:
        - Generated code includes both `primary_key=True` and ForeignKey
        """
        # Create two entities with a relationship where FK is also PK
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent_id",
                    type="integer",
                    is_pk=True,  # Both PK and FK
                    is_fk=True,
                    nullable=False,
                    db_column="parent_id"
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify both primary_key=True and ForeignKey are present
        assert "primary_key=True" in result, \
            "Primary key foreign key should include 'primary_key=True'"
        assert "ForeignKey" in result, \
            "Primary key foreign key should include ForeignKey"


class TestForeignKeyFieldNaming:
    """Test foreign key field naming with db_column attribute."""
    
    def test_foreign_key_uses_db_column_name(self):
        """
        Test that FK column with db_column uses db_column value instead of name.
        
        Verifies:
        - Generated code uses db_column value (e.g., 'code_id')
        - Generated code does NOT use relationship name (e.g., 'code')
        """
        # Create entities with FK relationship
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent",  # Relationship name
                    type="bigint",
                    is_fk=True,
                    nullable=True,
                    db_column="parent_id"  # Actual column name
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify db_column name is used
        assert "parent_id = Column(" in result, \
            "Foreign key should use db_column value 'parent_id'"
        
        # Verify relationship name is NOT used as column name
        assert "parent = Column(" not in result, \
            "Foreign key should NOT use relationship name 'parent' as column name"
    
    def test_foreign_key_without_db_column_uses_name(self):
        """
        Test edge case: FK without db_column should use name.
        
        Verifies:
        - Generated code uses column name when db_column is not specified
        """
        # Create entities with FK relationship (no db_column)
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent_id",
                    type="integer",
                    db_column="parent_id",
                    is_fk=True,
                    nullable=True
                    # No db_column specified
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify name is used when db_column is not specified
        assert "parent_id = Column(" in result, \
            "Foreign key without db_column should use name 'parent_id'"


class TestForeignKeyTypeMapping:
    """Test foreign key type mapping from TOML to SQLAlchemy types."""
    
    def test_foreign_key_bigint_type(self):
        """
        Test that FK column with bigint type generates BigInteger.
        
        Verifies:
        - Generated code uses BigInteger for bigint type
        - Generated code does NOT use Integer
        """
        # Create entities with bigint FK
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent_id",
                    type="bigint",  # Should map to BigInteger
                    is_fk=True,
                    nullable=True,
                    db_column="parent_id"
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify BigInteger is used
        assert "parent_id = Column(BigInteger" in result, \
            "Foreign key with bigint type should use BigInteger"
    
    def test_foreign_key_string_type(self):
        """
        Test that FK column with string type generates String.
        
        Verifies:
        - Generated code uses String for string type
        """
        # Create entities with string FK
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="code", type="string", db_column="code", is_pk=True, nullable=False, max_length=50)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent_code",
                    type="string",  # Should map to String
                    is_fk=True,
                    nullable=True,
                    max_length=50,
                    db_column="parent_code"
                )
            ],
            table_name="child"
        )
        
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="code",
            right_column="parent_code"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify String is used
        assert "parent_code = Column(String" in result, \
            "Foreign key with string type should use String"


class TestNullableForeignKeyGeneration:
    """Test nullable foreign key generation with nullable=True parameter."""
    
    def test_nullable_foreign_key_includes_nullable_parameter(self):
        """
        Test that FK column with nullable=true includes nullable=True.
        
        Verifies:
        - Generated code includes `nullable=True` parameter
        """
        # Create entities with nullable FK
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent_id",
                    type="integer",
                    is_fk=True,
                    nullable=True,  # Should include nullable=True
                    db_column="parent_id"
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Find the parent_id column line
        for line in result.split('\n'):
            if 'parent_id = Column(' in line:
                # Verify nullable=True is present
                assert 'nullable=True' in line, \
                    "Nullable foreign key should include 'nullable=True' parameter"
                break
        else:
            pytest.fail("Could not find parent_id column in generated code")
    
    def test_non_nullable_foreign_key_includes_nullable_false(self):
        """
        Test edge case: non-nullable FK should include nullable=False.
        
        Verifies:
        - Generated code includes `nullable=False` parameter
        """
        # Create entities with non-nullable FK
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(
                    name="parent_id",
                    type="integer",
                    is_fk=True,
                    nullable=False,  # Should include nullable=False
                    db_column="parent_id"
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Find the parent_id column line
        for line in result.split('\n'):
            if 'parent_id = Column(' in line:
                # Verify nullable=False is present
                assert 'nullable=False' in line, \
                    "Non-nullable foreign key should include 'nullable=False' parameter"
                break
        else:
            pytest.fail("Could not find parent_id column in generated code")


class TestReverseRelationshipForeignKeys:
    """Test reverse relationship foreign_keys parameter."""
    
    def test_reverse_relationship_includes_foreign_keys_parameter(self):
        """
        Test that reverse relationship includes foreign_keys parameter.
        
        Verifies:
        - Generated relationship() includes `foreign_keys=[column_name]`
        """
        # Create entities with relationship
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent_id",
                    type="integer",
                    is_fk=True,
                    nullable=True,
                    db_column="parent_id"
                )
            ],
            table_name="child"
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
            relationships=[relationship],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify foreign_keys parameter is present in reverse relationship
        assert "foreign_keys=[parent_id]" in result, \
            "Reverse relationship should include 'foreign_keys=[parent_id]' parameter"
    
    def test_multiple_foreign_keys_to_same_table(self):
        """
        Test edge case: multiple FKs to same table.
        
        Verifies:
        - Each reverse relationship includes correct foreign_keys parameter
        """
        # Create entities with multiple FKs to same table
        parent_entity = Entity(
            name="Parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ],
            table_name="parent"
        )
        
        child_entity = Entity(
            name="Child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent1_id",
                    type="integer",
                    is_fk=True,
                    nullable=True,
                    db_column="parent1_id"
                ),
                Column(
                    name="parent2_id",
                    type="integer",
                    is_fk=True,
                    nullable=True,
                    db_column="parent2_id"
                )
            ],
            table_name="child"
        )
        
        relationship1 = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent1_id"
        )
        
        relationship2 = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent2_id"
        )
        
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship1, relationship2],
            templates={}
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify both foreign_keys parameters are present
        assert "foreign_keys=[parent1_id]" in result, \
            "First reverse relationship should include 'foreign_keys=[parent1_id]'"
        assert "foreign_keys=[parent2_id]" in result, \
            "Second reverse relationship should include 'foreign_keys=[parent2_id]'"
