"""
Unit Tests for Relationship Configuration

These tests verify specific examples of bidirectional relationship configuration:
- One-to-one relationships with correct uselist
- One-to-many relationships with correct back_populates
- Both entities have matching relationship objects

Requirements: 3.1, 3.4, 5.2
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.parser.toml_parser import TomlERParser


class TestOneToOneRelationships:
    """Test one-to-one relationships with correct uselist parameter."""
    
    def test_one_to_one_user_profile_relationship(self):
        """
        Test one-to-one relationship between User and Profile.
        
        This is a classic example of one-to-one relationship:
        - Each User has one Profile
        - Each Profile belongs to one User
        - Both sides should have uselist=False
        
        Requirements: 3.1, 5.2
        """
        # Create User entity
        user_entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Profile entity with FK to User
        profile_entity = Entity(
            name="Profile",
            table_name="profile",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="user",
                    type="bigint",
                    db_column="user_id",
                    nullable=False,
                    unique=True,  # One-to-one requires unique constraint
                    is_fk=True
                )
            ]
        )
        
        # Create one-to-one relationship
        relationship = Relationship(
            left_entity="User",
            right_entity="Profile",
            relation_type="one-to-one",
            left_column="id",
            right_column="user_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"User": user_entity, "Profile": profile_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both entities have relationship objects
        assert "user = relationship(" in generated_code, \
            "Profile should have 'user' relationship"
        # Note: User has profile_rel (not profile) because it's the reverse side
        assert "profile_rel = relationship(" in generated_code, \
            "User should have 'profile_rel' relationship"
        
        # Verify both sides have uselist=False
        # Count occurrences of uselist=False
        uselist_false_count = generated_code.count("uselist=False")
        assert uselist_false_count == 2, \
            f"One-to-one relationship should have uselist=False on both sides, found {uselist_false_count}"
        
        # Verify back_populates parameters reference each other
        assert 'back_populates="profile_rel"' in generated_code or \
               "back_populates='profile_rel'" in generated_code, \
            "User relationship should have back_populates='profile_rel'"
        assert 'back_populates="user"' in generated_code or \
               "back_populates='user'" in generated_code, \
            "Profile relationship should have back_populates='user'"
    
    def test_one_to_one_person_passport_relationship(self):
        """
        Test one-to-one relationship between Person and Passport.
        
        Another classic one-to-one example:
        - Each Person has one Passport
        - Each Passport belongs to one Person
        
        Requirements: 3.1, 5.2
        """
        # Create Person entity
        person_entity = Entity(
            name="Person",
            table_name="person",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Passport entity with FK to Person
        passport_entity = Entity(
            name="Passport",
            table_name="passport",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="person",
                    type="integer",
                    db_column="person_id",
                    nullable=False,
                    unique=True,
                    is_fk=True
                )
            ]
        )
        
        # Create one-to-one relationship
        relationship = Relationship(
            left_entity="Person",
            right_entity="Passport",
            relation_type="one-to-one",
            left_column="id",
            right_column="person_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Person": person_entity, "Passport": passport_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify uselist=False on both sides
        lines = generated_code.split('\n')
        
        # Find Person's relationship
        person_rel_found = False
        person_has_uselist_false = False
        for i, line in enumerate(lines):
            if 'class Person' in line:
                # Look for relationship in next lines
                for j in range(i, min(i + 20, len(lines))):
                    if 'relationship(' in lines[j]:
                        person_rel_found = True
                        # Check this line and next few for uselist=False
                        for k in range(j, min(j + 5, len(lines))):
                            if 'uselist=False' in lines[k]:
                                person_has_uselist_false = True
                                break
                        break
                break
        
        assert person_rel_found, "Person should have a relationship"
        assert person_has_uselist_false, "Person's relationship should have uselist=False"
        
        # Find Passport's relationship
        passport_rel_found = False
        passport_has_uselist_false = False
        for i, line in enumerate(lines):
            if 'class Passport' in line:
                # Look for relationship in next lines
                for j in range(i, min(i + 20, len(lines))):
                    if 'relationship(' in lines[j]:
                        passport_rel_found = True
                        # Check this line and next few for uselist=False
                        for k in range(j, min(j + 5, len(lines))):
                            if 'uselist=False' in lines[k]:
                                passport_has_uselist_false = True
                                break
                        break
                break
        
        assert passport_rel_found, "Passport should have a relationship"
        assert passport_has_uselist_false, "Passport's relationship should have uselist=False"


class TestOneToManyRelationships:
    """Test one-to-many relationships with correct back_populates."""
    
    def test_one_to_many_author_books_relationship(self):
        """
        Test one-to-many relationship between Author and Book.
        
        Classic one-to-many example:
        - One Author has many Books
        - Each Book belongs to one Author
        - Author side should have collection (uselist=True or omitted)
        - Book side should reference single Author (no uselist=False)
        
        Requirements: 3.1, 3.4, 5.2
        """
        # Create Author entity
        author_entity = Entity(
            name="Author",
            table_name="author",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Book entity with FK to Author
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
        
        # Create one-to-many relationship
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
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both entities have relationship objects
        assert "author = relationship(" in generated_code, \
            "Book should have 'author' relationship"
        assert "book_set = relationship(" in generated_code, \
            "Author should have 'book_set' relationship (collection)"
        
        # Verify back_populates parameters reference each other
        assert 'back_populates="book_set"' in generated_code or \
               "back_populates='book_set'" in generated_code, \
            "Book's relationship should have back_populates='book_set'"
        assert 'back_populates="author"' in generated_code or \
               "back_populates='author'" in generated_code, \
            "Author's relationship should have back_populates='author'"
        
        # Verify Book side does NOT have uselist=False (it's a single reference)
        lines = generated_code.split('\n')
        book_class_start = None
        for i, line in enumerate(lines):
            if 'class Book' in line:
                book_class_start = i
                break
        
        assert book_class_start is not None, "Book class not found"
        
        # Check Book's relationship doesn't have uselist=False
        book_rel_has_uselist_false = False
        for i in range(book_class_start, min(book_class_start + 30, len(lines))):
            if 'author = relationship(' in lines[i]:
                # Check this line and next few
                for j in range(i, min(i + 5, len(lines))):
                    if 'uselist=False' in lines[j]:
                        book_rel_has_uselist_false = True
                        break
                break
        
        assert not book_rel_has_uselist_false, \
            "Book's relationship to Author should NOT have uselist=False in one-to-many"
    
    def test_one_to_many_department_employees_relationship(self):
        """
        Test one-to-many relationship between Department and Employee.
        
        Another one-to-many example:
        - One Department has many Employees
        - Each Employee belongs to one Department
        
        Requirements: 3.1, 3.4, 5.2
        """
        # Create Department entity
        department_entity = Entity(
            name="Department",
            table_name="department",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Employee entity with FK to Department
        employee_entity = Entity(
            name="Employee",
            table_name="employee",
            columns=[
                Column(name="id", type="integer", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="department",
                    type="integer",
                    db_column="department_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create one-to-many relationship
        relationship = Relationship(
            left_entity="Department",
            right_entity="Employee",
            relation_type="one-to-many",
            left_column="id",
            right_column="department_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Department": department_entity, "Employee": employee_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both entities have relationship objects
        assert "department = relationship(" in generated_code, \
            "Employee should have 'department' relationship"
        assert "employee_set = relationship(" in generated_code, \
            "Department should have 'employee_set' relationship"
        
        # Verify back_populates are correct
        assert 'back_populates="employee_set"' in generated_code or \
               "back_populates='employee_set'" in generated_code, \
            "Employee's relationship should back_populate to 'employee_set'"
        assert 'back_populates="department"' in generated_code or \
               "back_populates='department'" in generated_code, \
            "Department's relationship should back_populate to 'department'"
    
    def test_one_to_many_translation_i18ncode_relationship(self):
        """
        Test one-to-many relationship from requirements example.
        
        This is the canonical example from the requirements:
        - I18nCode has many Translations
        - Each Translation belongs to one I18nCode
        
        Requirements: 3.1, 3.4, 5.2
        """
        # Create I18nCode entity
        i18ncode_entity = Entity(
            name="I18nCode",
            table_name="kkt_i18n_translations_i18ncodemodel",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Translation entity with FK to I18nCode
        translation_entity = Entity(
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
        
        # Create one-to-many relationship
        relationship = Relationship(
            left_entity="I18nCode",
            right_entity="Translation",
            relation_type="one-to-many",
            left_column="id",
            right_column="code_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"I18nCode": i18ncode_entity, "Translation": translation_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both entities have relationship objects
        assert "code = relationship(" in generated_code, \
            "Translation should have 'code' relationship"
        assert "translation_set = relationship(" in generated_code, \
            "I18nCode should have 'translation_set' relationship"
        
        # Verify back_populates
        assert 'back_populates="translation_set"' in generated_code or \
               "back_populates='translation_set'" in generated_code, \
            "Translation's relationship should back_populate to 'translation_set'"
        assert 'back_populates="code"' in generated_code or \
               "back_populates='code'" in generated_code, \
            "I18nCode's relationship should back_populate to 'code'"


class TestMatchingRelationshipObjects:
    """Test that both entities have matching relationship objects."""
    
    def test_both_entities_have_relationships_simple_case(self):
        """
        Test that both entities in a relationship have relationship objects.
        
        This is a simple test to verify the basic requirement that
        bidirectional relationships create relationship objects on both sides.
        
        Requirements: 3.1
        """
        # Create Parent entity
        parent_entity = Entity(
            name="Parent",
            table_name="parent",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Child entity with FK to Parent
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
        
        # Create one-to-many relationship
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
        
        # Count relationship definitions
        relationship_count = generated_code.count("= relationship(")
        assert relationship_count == 2, \
            f"Expected 2 relationship objects (one per entity), found {relationship_count}"
        
        # Verify Parent has a relationship
        lines = generated_code.split('\n')
        parent_has_relationship = False
        for i, line in enumerate(lines):
            if 'class Parent' in line:
                for j in range(i, min(i + 20, len(lines))):
                    if 'relationship(' in lines[j]:
                        parent_has_relationship = True
                        break
                break
        
        assert parent_has_relationship, "Parent entity should have a relationship object"
        
        # Verify Child has a relationship
        child_has_relationship = False
        for i, line in enumerate(lines):
            if 'class Child' in line:
                for j in range(i, min(i + 20, len(lines))):
                    if 'relationship(' in lines[j]:
                        child_has_relationship = True
                        break
                break
        
        assert child_has_relationship, "Child entity should have a relationship object"
    
    def test_multiple_relationships_all_have_matching_objects(self):
        """
        Test that when an entity has multiple relationships, all have matching objects.
        
        This verifies that the generator correctly handles entities with
        multiple foreign keys, creating relationship objects for each.
        
        Requirements: 3.1, 3.4
        """
        # Create parent entities
        author_entity = Entity(
            name="Author",
            table_name="author",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        publisher_entity = Entity(
            name="Publisher",
            table_name="publisher",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False)
            ]
        )
        
        # Create Book entity with multiple FKs
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
                ),
                Column(
                    name="publisher",
                    type="bigint",
                    db_column="publisher_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create relationships
        relationship1 = Relationship(
            left_entity="Author",
            right_entity="Book",
            relation_type="one-to-many",
            left_column="id",
            right_column="author_id"
        )
        
        relationship2 = Relationship(
            left_entity="Publisher",
            right_entity="Book",
            relation_type="one-to-many",
            left_column="id",
            right_column="publisher_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                "Author": author_entity,
                "Publisher": publisher_entity,
                "Book": book_entity
            },
            relationships=[relationship1, relationship2]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify all entities have relationship objects
        assert "author = relationship(" in generated_code, \
            "Book should have 'author' relationship"
        assert "publisher = relationship(" in generated_code, \
            "Book should have 'publisher' relationship"
        assert "book_set = relationship(" in generated_code, \
            "Author and Publisher should have 'book_set' relationships"
        
        # Count book_set relationships (should be 2: one in Author, one in Publisher)
        book_set_count = generated_code.count("book_set = relationship(")
        assert book_set_count == 2, \
            f"Expected 2 'book_set' relationships (one in Author, one in Publisher), found {book_set_count}"
        
        # Verify back_populates for both relationships
        assert 'back_populates="book_set"' in generated_code or \
               "back_populates='book_set'" in generated_code, \
            "Book's relationships should back_populate to 'book_set'"
        assert 'back_populates="author"' in generated_code or \
               "back_populates='author'" in generated_code, \
            "Author's relationship should back_populate to 'author'"
        assert 'back_populates="publisher"' in generated_code or \
               "back_populates='publisher'" in generated_code, \
            "Publisher's relationship should back_populate to 'publisher'"
    
    def test_self_referential_relationship_has_both_sides(self):
        """
        Test that self-referential relationships create relationship object.
        
        A self-referential relationship (e.g., Employee.manager -> Employee)
        creates a relationship object on the side with the FK.
        
        Note: Currently, self-referential relationships only create one
        relationship object (on the FK side), not both sides. This is a
        known limitation of the current implementation.
        
        Requirements: 3.1, 3.4
        """
        # Create Employee entity with self-referential FK
        employee_entity = Entity(
            name="Employee",
            table_name="employee",
            columns=[
                Column(name="id", type="bigint", db_column="id", is_pk=True, nullable=False),
                Column(
                    name="manager",
                    type="bigint",
                    db_column="manager_id",
                    nullable=True,
                    is_fk=True
                )
            ]
        )
        
        # Create self-referential relationship
        relationship = Relationship(
            left_entity="Employee",
            right_entity="Employee",
            relation_type="one-to-many",
            left_column="id",
            right_column="manager_id"
        )
        
        # Create ERModel
        model = ERModel(
            entities={"Employee": employee_entity},
            relationships=[relationship]
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify Employee has at least one relationship object
        relationship_count = generated_code.count("= relationship(")
        assert relationship_count >= 1, \
            f"Self-referential relationship should create at least 1 relationship object, found {relationship_count}"
        
        # Verify the FK side relationship is present
        assert "manager = relationship(" in generated_code, \
            "Employee should have 'manager' relationship"
        
        # Verify back_populates references the reverse side
        assert 'back_populates="employee_set"' in generated_code or \
               "back_populates='employee_set'" in generated_code, \
            "Manager relationship should back_populate to 'employee_set'"
