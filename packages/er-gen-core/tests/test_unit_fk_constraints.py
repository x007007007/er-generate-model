"""
Unit Tests for Foreign Key Constraints

These tests verify specific examples of FK constraint generation:
- ForeignKey format without table prefix
- ForeignKey format with table prefix
- Type matching for various column types

Requirements: 2.2, 5.3, 5.4, 7.1, 7.2, 7.3
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.parser.toml_parser import TomlERParser


class TestForeignKeyConstraintFormat:
    """Test ForeignKey constraint format with and without table prefix."""
    
    def test_foreign_key_format_without_table_prefix(self):
        """
        Test ForeignKey constraint format without table prefix.
        
        Expected format: ForeignKey('table_name.column_name')
        
        Requirements: 2.2, 5.4, 7.3
        """
        # Create entities
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
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code WITHOUT table prefix
        renderer = SQLAlchemyRenderer(table_prefix='')
        generated_code = renderer.render(model)
        
        # Verify ForeignKey format: table_name.column_name
        assert 'ForeignKey("parent.id")' in generated_code or \
               "ForeignKey('parent.id')" in generated_code, \
            "ForeignKey should use format 'parent.id' without table prefix"
        
        # Verify it does NOT include a prefix
        assert 'ForeignKey("_parent.id")' not in generated_code and \
               "ForeignKey('_parent.id')" not in generated_code, \
            "ForeignKey should NOT include prefix when table_prefix is empty"
    
    def test_foreign_key_format_with_table_prefix(self):
        """
        Test ForeignKey constraint format with table prefix.
        
        Expected format: ForeignKey('{prefix}_{table_name}.column_name')
        
        Requirements: 2.2, 5.4, 7.1, 7.2
        """
        # Create entities
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
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code WITH table prefix
        table_prefix = "myapp"
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        generated_code = renderer.render(model)
        
        # Verify ForeignKey format: {prefix}_{table_name}.column_name
        expected_fk = f"{table_prefix}_parent.id"
        assert f'ForeignKey("{expected_fk}")' in generated_code or \
               f"ForeignKey('{expected_fk}')" in generated_code, \
            f"ForeignKey should use format '{expected_fk}' with table prefix"
    
    def test_foreign_key_references_correct_target_column(self):
        """
        Test that ForeignKey references the correct target column.
        
        This verifies that the ForeignKey constraint references the actual
        primary key column, not just assuming 'id'.
        
        Requirements: 2.2, 5.4
        """
        # Create entities with non-standard PK column name
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="pk", type="bigint", db_column="pk", is_pk=True, nullable=False)
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
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship referencing the 'pk' column
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="pk",
            right_column="parent_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer(table_prefix='')
        generated_code = renderer.render(model)
        
        # Verify ForeignKey references 'pk' column, not 'id'
        assert 'ForeignKey("parent.pk")' in generated_code or \
               "ForeignKey('parent.pk')" in generated_code, \
            "ForeignKey should reference the actual PK column 'pk', not assume 'id'"
        
        # Verify it does NOT reference 'id'
        assert 'ForeignKey("parent.id")' not in generated_code and \
               "ForeignKey('parent.id')" not in generated_code, \
            "ForeignKey should NOT reference 'id' when PK column is 'pk'"


class TestForeignKeyTypeMatching:
    """Test type matching for various column types in FK constraints."""
    
    def test_bigint_foreign_key_uses_biginteger(self):
        """
        Test that bigint FK uses BigInteger type.
        
        Requirements: 5.3
        """
        # Create entities with bigint FK
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
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify FK uses BigInteger
        assert "parent_id = Column(BigInteger" in generated_code, \
            "Foreign key with bigint type should use BigInteger"
        
        # Verify it does NOT use Integer
        assert "parent_id = Column(Integer" not in generated_code, \
            "Foreign key with bigint type should NOT use Integer"
    
    def test_int_foreign_key_uses_integer(self):
        """
        Test that int FK uses Integer type.
        
        Requirements: 5.3
        """
        # Create entities with int FK
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="int",
                    db_column="parent_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify FK uses Integer
        assert "parent_id = Column(Integer" in generated_code, \
            "Foreign key with int type should use Integer"
        
        # Verify it does NOT use BigInteger
        assert "parent_id = Column(BigInteger" not in generated_code, \
            "Foreign key with int type should NOT use BigInteger"
    
    def test_uuid_foreign_key_uses_uuid_type(self):
        """
        Test that uuid FK uses UUID type.
        
        Requirements: 5.3
        """
        # Create entities with uuid FK
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="uuid", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="uuid", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="uuid",
                    db_column="parent_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify FK uses UUID
        assert "parent_id = Column(UUID" in generated_code, \
            "Foreign key with uuid type should use UUID"
    
    def test_string_foreign_key_uses_string_type(self):
        """
        Test that string FK uses String type with correct length.
        
        Requirements: 5.3
        """
        # Create entities with string FK
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="code", type="string", db_column="code", is_pk=True, nullable=False, max_length=50)
            ]
        )
        
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent_code",
                    type="string",
                    db_column="parent_code_id",
                    nullable=True,
                    max_length=50,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Parent",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="code",
            right_column="parent_code_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Parent": parent_entity, "Child": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify FK uses String with length
        assert "parent_code_id = Column(String(50)" in generated_code, \
            "Foreign key with string type should use String(50)"
    
    def test_multiple_foreign_keys_with_different_types(self):
        """
        Test multiple FKs with different types all use correct types.
        
        This verifies that type matching works correctly when an entity
        has multiple foreign keys with different types.
        
        Requirements: 5.3
        """
        # Create parent entities with different PK types
        parent1_entity = Entity(
            name="Parent1",
            table_name="parent1",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        parent2_entity = Entity(
            name="Parent2",
            table_name="parent2",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        parent3_entity = Entity(
            name="Parent3",
            table_name="parent3",
            columns=[
                Column(name="id", type="uuid", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create child entity with multiple FKs
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent1",
                    type="bigint",
                    db_column="parent1_id",
                    nullable=True,
                    is_fk=True
                ),
                Column(
                    name="parent2",
                    type="int",
                    db_column="parent2_id",
                    nullable=True,
                    is_fk=True
                ),
                Column(
                    name="parent3",
                    type="uuid",
                    db_column="parent3_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationships
        relationship1 = Relationship(
            left_entity="Parent1",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent1_id"
        )
        
        relationship2 = Relationship(
            left_entity="Parent2",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent2_id"
        )
        
        relationship3 = Relationship(
            left_entity="Parent3",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent3_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                "Parent1": parent1_entity,
                "Parent2": parent2_entity,
                "Parent3": parent3_entity,
                "Child": child_entity
            },
            relationships=[relationship1, relationship2, relationship3]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify each FK uses the correct type
        assert "parent1_id = Column(BigInteger" in generated_code, \
            "First FK should use BigInteger"
        assert "parent2_id = Column(Integer" in generated_code, \
            "Second FK should use Integer"
        assert "parent3_id = Column(UUID" in generated_code, \
            "Third FK should use UUID"


class TestForeignKeyConstraintWithTablePrefix:
    """Test FK constraints with table prefix applied consistently."""
    
    def test_table_prefix_applied_to_all_foreign_keys(self):
        """
        Test that table prefix is applied consistently to all FK constraints.
        
        Requirements: 7.1, 7.2
        """
        # Create multiple entities with relationships
        parent1_entity = Entity(
            name="Parent1",
            table_name="parent1",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        parent2_entity = Entity(
            name="Parent2",
            table_name="parent2",
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
                    name="parent1",
                    type="bigint",
                    db_column="parent1_id",
                    nullable=True,
                    is_fk=True
                ),
                Column(
                    name="parent2",
                    type="bigint",
                    db_column="parent2_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationships
        relationship1 = Relationship(
            left_entity="Parent1",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent1_id"
        )
        
        relationship2 = Relationship(
            left_entity="Parent2",
            right_entity="Child",
            relation_type="one-to-many",
            left_column="id",
            right_column="parent2_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                "Parent1": parent1_entity,
                "Parent2": parent2_entity,
                "Child": child_entity
            },
            relationships=[relationship1, relationship2]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code with table prefix
        table_prefix = "app"
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        generated_code = renderer.render(model)
        
        # Verify both FKs use the table prefix
        assert f'ForeignKey("{table_prefix}_parent1.id")' in generated_code or \
               f"ForeignKey('{table_prefix}_parent1.id')" in generated_code, \
            f"First FK should use prefix '{table_prefix}_parent1.id'"
        
        assert f'ForeignKey("{table_prefix}_parent2.id")' in generated_code or \
               f"ForeignKey('{table_prefix}_parent2.id')" in generated_code, \
            f"Second FK should use prefix '{table_prefix}_parent2.id'"
    
    def test_complex_table_name_with_prefix(self):
        """
        Test that complex table names work correctly with prefix.
        
        Requirements: 7.1, 7.2
        """
        # Create entities with complex table names
        parent_entity = Entity(
            name="I18nCode",
            table_name="kkt_i18n_translations_i18ncodemodel",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        child_entity = Entity(
            name="Translation",
            table_name="kkt_i18n_translations_translationmodel",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="code",
                    type="bigint",
                    db_column="code_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="I18nCode",
            right_entity="Translation",
            relation_type="one-to-many",
            left_column="id",
            right_column="code_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"I18nCode": parent_entity, "Translation": child_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code with table prefix
        table_prefix = "myapp"
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        generated_code = renderer.render(model)
        
        # Verify FK uses prefix with complex table name
        expected_fk = f"{table_prefix}_kkt_i18n_translations_i18ncodemodel.id"
        assert f'ForeignKey("{expected_fk}")' in generated_code or \
               f"ForeignKey('{expected_fk}')" in generated_code, \
            f"FK should use prefix with complex table name: '{expected_fk}'"
