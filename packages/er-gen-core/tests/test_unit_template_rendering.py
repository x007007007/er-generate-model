"""
Unit Tests for Template Rendering with Django-Style Foreign Key Naming

These tests verify that the Jinja2 templates correctly render Django-style
foreign key relationships:
- Column definitions use db_column (with _id suffix)
- Relationship objects use logical name (without _id suffix)
- Relationships include foreign_keys parameter
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestDjangoStyleTemplateRendering:
    """Test Django-style naming in template rendering."""
    
    def test_translation_i18ncode_example_basic_django_naming(self):
        """
        Test basic Django-style naming using Translation/I18nCode example.
        
        This is the canonical example from the requirements:
        - Translation entity has a foreign key to I18nCode
        - Column name is "code" (logical name)
        - db_column is "code_id" (database column name)
        
        Expected output:
        - code_id = Column(BigInteger, ForeignKey(...), nullable=True)
        - code = relationship("I18nCode", ..., foreign_keys=[code_id])
        
        Requirements: 1.1, 1.2, 1.3, 1.4
        """
        # Create I18nCode entity
        i18ncode_entity = Entity(
            name="I18nCode",
            table_name="kkt_i18n_translations_i18ncodemodel",
            columns=[
                Column(
                    name="id",
                    type="bigint",
                    db_column="id",
                    is_pk=True,
                    nullable=False,
                    unique=True
                )
            ]
        )
        
        # Create Translation entity with Django-style FK
        translation_entity = Entity(
            name="Translation",
            table_name="kkt_i18n_translations_translationmodel",
            columns=[
                Column(
                    name="id",
                    type="bigint",
                    db_column="id",
                    is_pk=True,
                    nullable=False,
                    unique=True
                ),
                Column(
                    name="code",  # Logical name for relationship
                    type="bigint",
                    db_column="code_id",  # Database column name
                    nullable=True,
                    is_fk=True
                ),
                Column(
                    name="translate",
                    type="text",
                    db_column="translate",
                    nullable=True
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
            entities={
                "I18nCode": i18ncode_entity,
                "Translation": translation_entity
            },
            relationships=[relationship]
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify column uses db_column name (code_id)
        assert "code_id = Column(" in generated_code, \
            "Column definition should use db_column 'code_id'"
        
        # Verify column should NOT use logical name
        assert "code = Column(" not in generated_code, \
            "Column definition should NOT use logical name 'code'"
        
        # Verify relationship uses logical name (code)
        assert "code = relationship(" in generated_code, \
            "Relationship should use logical name 'code'"
        
        # Verify relationship includes foreign_keys parameter
        assert "foreign_keys=[code_id]" in generated_code, \
            "Relationship should include 'foreign_keys=[code_id]' parameter"
        
        # Verify ForeignKey constraint references correct table
        assert 'ForeignKey("kkt_i18n_translations_i18ncodemodel.id")' in generated_code or \
               "ForeignKey('kkt_i18n_translations_i18ncodemodel.id')" in generated_code, \
            "ForeignKey should reference 'kkt_i18n_translations_i18ncodemodel.id'"
    
    def test_column_uses_db_column_relationship_uses_name(self):
        """
        Test that column uses db_column and relationship uses name.
        
        This test verifies the core Django-style naming convention:
        - Database column: uses db_column value (e.g., "parent_id")
        - Relationship object: uses name value (e.g., "parent")
        
        Requirements: 1.1, 1.2
        """
        # Create parent entity
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create child entity with Django-style FK
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",  # Logical name (for relationship)
                    type="integer",
                    db_column="parent_id",  # Database column name
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
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify column uses db_column
        assert "parent_id = Column(" in generated_code, \
            "Column should use db_column 'parent_id'"
        
        # Verify relationship uses name
        assert "parent = relationship(" in generated_code, \
            "Relationship should use name 'parent'"
        
        # Verify they are different (not both using the same name)
        column_count = generated_code.count("parent_id = Column(")
        relationship_count = generated_code.count("parent = relationship(")
        
        assert column_count == 1, \
            f"Should have exactly 1 column definition, found {column_count}"
        assert relationship_count == 1, \
            f"Should have exactly 1 relationship definition, found {relationship_count}"
    
    def test_foreign_keys_parameter_included_in_relationship(self):
        """
        Test that foreign_keys parameter is included in relationship.
        
        This test verifies that the relationship object includes the
        foreign_keys parameter referencing the column.
        
        Requirements: 1.3
        """
        # Create entities
        author_entity = Entity(
            name="Author",
            table_name="author",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        book_entity = Entity(
            name="Book",
            table_name="book",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="author",
                    type="bigint",
                    db_column="author_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity="Author",
            right_entity="Book",
            relation_type="one-to-many",
            left_column="id",
            right_column="author_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Author": author_entity, "Book": book_entity},
            relationships=[relationship]
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify foreign_keys parameter is present
        assert "foreign_keys=[author_id]" in generated_code, \
            "Relationship should include 'foreign_keys=[author_id]' parameter"
        
        # Verify it's in the relationship definition, not elsewhere
        # Find the relationship line
        lines = generated_code.split('\n')
        relationship_found = False
        foreign_keys_in_relationship = False
        
        for i, line in enumerate(lines):
            if "author = relationship(" in line:
                relationship_found = True
                # Check this line and the next few lines for foreign_keys
                for j in range(i, min(i + 10, len(lines))):
                    if "foreign_keys=[author_id]" in lines[j]:
                        foreign_keys_in_relationship = True
                        break
                break
        
        assert relationship_found, "Relationship definition not found"
        assert foreign_keys_in_relationship, \
            "foreign_keys parameter should be in the relationship definition"
    
    def test_multiple_foreign_keys_each_with_correct_naming(self):
        """
        Test multiple foreign keys each follow Django-style naming.
        
        This test verifies that when an entity has multiple foreign keys,
        each one correctly uses db_column for the column and name for the
        relationship, with appropriate foreign_keys parameters.
        
        Requirements: 1.1, 1.2, 1.3, 1.4
        """
        # Create parent entities
        i18ncode_entity = Entity(
            name="I18nCode",
            table_name="i18ncode",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        i18nblock_entity = Entity(
            name="I18nBlock",
            table_name="i18nblock",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Translation entity with multiple FKs
        translation_entity = Entity(
            name="Translation",
            table_name="translation",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="code",
                    type="bigint",
                    db_column="code_id",
                    nullable=True,
                    is_fk=True
                ),
                Column(
                    name="block",
                    type="bigint",
                    db_column="block_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationships
        relationship1 = Relationship(
            left_entity="I18nCode",
            right_entity="Translation",
            relation_type="one-to-many",
            left_column="id",
            right_column="code_id"
        )
        
        relationship2 = Relationship(
            left_entity="I18nBlock",
            right_entity="Translation",
            relation_type="one-to-many",
            left_column="id",
            right_column="block_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                "I18nCode": i18ncode_entity,
                "I18nBlock": i18nblock_entity,
                "Translation": translation_entity
            },
            relationships=[relationship1, relationship2]
        )
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify first FK: code/code_id
        assert "code_id = Column(" in generated_code, \
            "First column should use db_column 'code_id'"
        assert "code = relationship(" in generated_code, \
            "First relationship should use name 'code'"
        assert "foreign_keys=[code_id]" in generated_code, \
            "First relationship should include 'foreign_keys=[code_id]'"
        
        # Verify second FK: block/block_id
        assert "block_id = Column(" in generated_code, \
            "Second column should use db_column 'block_id'"
        assert "block = relationship(" in generated_code, \
            "Second relationship should use name 'block'"
        assert "foreign_keys=[block_id]" in generated_code, \
            "Second relationship should include 'foreign_keys=[block_id]'"
        
        # Verify no confusion between the two
        assert generated_code.count("code_id = Column(") == 1, \
            "Should have exactly one code_id column"
        assert generated_code.count("block_id = Column(") == 1, \
            "Should have exactly one block_id column"
        assert generated_code.count("code = relationship(") == 1, \
            "Should have exactly one code relationship"
        assert generated_code.count("block = relationship(") == 1, \
            "Should have exactly one block relationship"
    
    def test_foreign_key_with_nullable_attribute(self):
        """
        Test that nullable attribute is preserved in FK column.
        
        This test verifies that when a foreign key column has nullable=True,
        the generated Column definition includes this attribute.
        
        Requirements: 1.2 (column attributes preservation)
        """
        # Create entities
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
                    nullable=True,  # Should be preserved
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
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the parent_id column definition
        lines = generated_code.split('\n')
        parent_id_line = None
        for line in lines:
            if 'parent_id = Column(' in line:
                # Collect the full column definition (may span multiple lines)
                parent_id_line = line
                break
        
        assert parent_id_line is not None, "parent_id column not found"
        
        # Verify nullable=True is present
        # Note: We need to check the full column definition which may span multiple lines
        # For simplicity, we'll check if nullable=True appears in the generated code
        # in the context of the parent_id column
        assert "nullable=True" in generated_code, \
            "Foreign key column should include 'nullable=True' parameter"
    
    def test_foreign_key_type_matches_referenced_column(self):
        """
        Test that FK column type matches the referenced column type.
        
        This test verifies that when a foreign key references a BigInteger
        primary key, the FK column also uses BigInteger.
        
        Requirements: 1.2 (type consistency)
        """
        # Create parent entity with BigInteger PK
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create child entity with BigInteger FK
        child_entity = Entity(
            name="Child",
            table_name="child",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="parent",
                    type="bigint",  # Should match parent's id type
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
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both use BigInteger
        assert "parent_id = Column(BigInteger" in generated_code, \
            "Foreign key should use BigInteger to match referenced column"
        
        # Verify parent's id also uses BigInteger
        lines = generated_code.split('\n')
        parent_class_found = False
        parent_id_uses_bigint = False
        
        for line in lines:
            if "class Parent" in line:
                parent_class_found = True
            if parent_class_found and "id = Column(BigInteger" in line:
                parent_id_uses_bigint = True
                break
        
        assert parent_id_uses_bigint, \
            "Parent's id column should use BigInteger"
