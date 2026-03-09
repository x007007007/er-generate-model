"""
Unit tests for parser foreign key detection.

These tests verify specific examples of FK detection:
1. When db_column is explicitly set with _id suffix
2. When db_column is not set and should be inferred as {name}_id
3. When relationship's right_column matches column name or db_column

Requirements: 3.2, 4.1
"""
import pytest
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.models import ERModel, Entity, Column, Relationship


class TestParserFKDetection:
    """Unit tests for foreign key detection in the TOML parser."""
    
    def test_explicit_db_column_with_id_suffix(self):
        """
        Test FK detection when db_column is explicitly set with _id suffix.
        
        Scenario: A column has name="code" and db_column="code_id" explicitly set.
        The relationship's right_column="code_id" matches the db_column.
        
        Expected: Column should be marked as FK, db_column should remain "code_id".
        """
        # Create entities
        i18n_code = Entity(
            name='I18nCode',
            table_name='i18ncode',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        translation = Entity(
            name='Translation',
            table_name='translation',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='code', type='int', db_column='code_id', nullable=True)
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity='I18nCode',
            right_entity='Translation',
            relation_type='one-to-many',
            left_column='id',
            right_column='code_id'  # Matches db_column
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'I18nCode': i18n_code,
                'Translation': translation
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the code column
        code_col = next((col for col in translation.columns if col.name == 'code'), None)
        
        # Assertions
        assert code_col is not None, "Code column should exist"
        assert code_col.is_fk is True, "Column should be marked as FK"
        assert code_col.db_column == 'code_id', "db_column should remain 'code_id'"
        assert code_col.type == 'bigint', "FK type should match referenced column type"
    
    def test_implicit_db_column_inference(self):
        """
        Test FK detection when db_column is not set and should be inferred.
        
        Scenario: A column has name="code" and db_column="code" (not explicitly set).
        The relationship's right_column="code" matches the name.
        
        Expected: Column should be marked as FK, db_column should be inferred as "code_id".
        """
        # Create entities
        i18n_code = Entity(
            name='I18nCode',
            table_name='i18ncode',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        translation = Entity(
            name='Translation',
            table_name='translation',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='code', type='int', db_column='code', nullable=True)  # db_column same as name
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity='I18nCode',
            right_entity='Translation',
            relation_type='one-to-many',
            left_column='id',
            right_column='code'  # Matches name
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'I18nCode': i18n_code,
                'Translation': translation
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the code column
        code_col = next((col for col in translation.columns if col.name == 'code'), None)
        
        # Assertions
        assert code_col is not None, "Code column should exist"
        assert code_col.is_fk is True, "Column should be marked as FK"
        assert code_col.db_column == 'code_id', "db_column should be inferred as 'code_id'"
        assert code_col.type == 'bigint', "FK type should match referenced column type"
    
    def test_matching_against_relationship_right_column_by_name(self):
        """
        Test FK detection when relationship's right_column matches column name.
        
        Scenario: Column has name="author" and db_column="author".
        Relationship's right_column="author" matches the name.
        
        Expected: Column should be marked as FK, db_column inferred as "author_id".
        """
        # Create entities
        user = Entity(
            name='User',
            table_name='user',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        post = Entity(
            name='Post',
            table_name='post',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name='author', type='int', db_column='author', nullable=False)
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity='User',
            right_entity='Post',
            relation_type='one-to-many',
            left_column='id',
            right_column='author'  # Matches name
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'User': user,
                'Post': post
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the author column
        author_col = next((col for col in post.columns if col.name == 'author'), None)
        
        # Assertions
        assert author_col is not None, "Author column should exist"
        assert author_col.is_fk is True, "Column should be marked as FK"
        assert author_col.db_column == 'author_id', "db_column should be inferred as 'author_id'"
        assert author_col.type == 'int', "FK type should match referenced column type"
    
    def test_matching_against_relationship_right_column_by_db_column(self):
        """
        Test FK detection when relationship's right_column matches db_column.
        
        Scenario: Column has name="author" and db_column="author_id" (explicitly set).
        Relationship's right_column="author_id" matches the db_column.
        
        Expected: Column should be marked as FK, db_column remains "author_id".
        """
        # Create entities
        user = Entity(
            name='User',
            table_name='user',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        post = Entity(
            name='Post',
            table_name='post',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name='author', type='int', db_column='author_id', nullable=False)
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity='User',
            right_entity='Post',
            relation_type='one-to-many',
            left_column='id',
            right_column='author_id'  # Matches db_column
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'User': user,
                'Post': post
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the author column
        author_col = next((col for col in post.columns if col.name == 'author'), None)
        
        # Assertions
        assert author_col is not None, "Author column should exist"
        assert author_col.is_fk is True, "Column should be marked as FK"
        assert author_col.db_column == 'author_id', "db_column should remain 'author_id'"
        assert author_col.type == 'int', "FK type should match referenced column type"
    
    def test_multiple_foreign_keys_in_same_entity(self):
        """
        Test FK detection with multiple foreign keys in the same entity.
        
        Scenario: An entity has two foreign keys to different entities.
        
        Expected: Both columns should be marked as FK with correct db_columns.
        """
        # Create entities
        user = Entity(
            name='User',
            table_name='user',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        category = Entity(
            name='Category',
            table_name='category',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        post = Entity(
            name='Post',
            table_name='post',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name='author', type='int', db_column='author', nullable=False),
                Column(name='category', type='int', db_column='category', nullable=True)
            ]
        )
        
        # Create relationships
        author_rel = Relationship(
            left_entity='User',
            right_entity='Post',
            relation_type='one-to-many',
            left_column='id',
            right_column='author'
        )
        
        category_rel = Relationship(
            left_entity='Category',
            right_entity='Post',
            relation_type='one-to-many',
            left_column='id',
            right_column='category'
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'User': user,
                'Category': category,
                'Post': post
            },
            relationships=[author_rel, category_rel]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the FK columns
        author_col = next((col for col in post.columns if col.name == 'author'), None)
        category_col = next((col for col in post.columns if col.name == 'category'), None)
        
        # Assertions for author column
        assert author_col is not None, "Author column should exist"
        assert author_col.is_fk is True, "Author column should be marked as FK"
        assert author_col.db_column == 'author_id', "Author db_column should be inferred as 'author_id'"
        
        # Assertions for category column
        assert category_col is not None, "Category column should exist"
        assert category_col.is_fk is True, "Category column should be marked as FK"
        assert category_col.db_column == 'category_id', "Category db_column should be inferred as 'category_id'"
    
    def test_no_inference_when_name_already_ends_with_id(self):
        """
        Test that db_column is not modified when name already ends with _id.
        
        Scenario: Column has name="code_id" and db_column="code_id".
        
        Expected: db_column should remain "code_id" (not become "code_id_id").
        """
        # Create entities
        i18n_code = Entity(
            name='I18nCode',
            table_name='i18ncode',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        translation = Entity(
            name='Translation',
            table_name='translation',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='code_id', type='int', db_column='code_id', nullable=True)
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity='I18nCode',
            right_entity='Translation',
            relation_type='one-to-many',
            left_column='id',
            right_column='code_id'
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'I18nCode': i18n_code,
                'Translation': translation
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the code_id column
        code_col = next((col for col in translation.columns if col.name == 'code_id'), None)
        
        # Assertions
        assert code_col is not None, "code_id column should exist"
        assert code_col.is_fk is True, "Column should be marked as FK"
        assert code_col.db_column == 'code_id', "db_column should remain 'code_id' (not 'code_id_id')"
    
    def test_non_fk_columns_not_affected(self):
        """
        Test that non-FK columns are not affected by FK detection.
        
        Scenario: Entity has both FK and non-FK columns.
        
        Expected: Only FK columns should be marked, non-FK columns unchanged.
        """
        # Create entities
        user = Entity(
            name='User',
            table_name='user',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        post = Entity(
            name='Post',
            table_name='post',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name='author', type='int', db_column='author', nullable=False),
                Column(name='title', type='varchar', db_column='title', nullable=False),
                Column(name='view_count', type='int', db_column='view_count', nullable=True)
            ]
        )
        
        # Create relationship only for author
        relationship = Relationship(
            left_entity='User',
            right_entity='Post',
            relation_type='one-to-many',
            left_column='id',
            right_column='author'
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'User': user,
                'Post': post
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find columns
        author_col = next((col for col in post.columns if col.name == 'author'), None)
        title_col = next((col for col in post.columns if col.name == 'title'), None)
        view_count_col = next((col for col in post.columns if col.name == 'view_count'), None)
        
        # Assertions
        assert author_col is not None and author_col.is_fk is True, "Author should be FK"
        assert title_col is not None and title_col.is_fk is False, "Title should not be FK"
        assert title_col.db_column == 'title', "Title db_column should be unchanged"
        assert view_count_col is not None and view_count_col.is_fk is False, "view_count should not be FK"
        assert view_count_col.db_column == 'view_count', "view_count db_column should be unchanged"
    
    def test_one_to_one_relationship_fk_detection(self):
        """
        Test FK detection for one-to-one relationships.
        
        Scenario: A one-to-one relationship between User and Profile.
        
        Expected: FK column should be marked correctly.
        """
        # Create entities
        user = Entity(
            name='User',
            table_name='user',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        profile = Entity(
            name='Profile',
            table_name='profile',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name='user', type='int', db_column='user', nullable=False)
            ]
        )
        
        # Create one-to-one relationship
        relationship = Relationship(
            left_entity='User',
            right_entity='Profile',
            relation_type='one-to-one',
            left_column='id',
            right_column='user'
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'User': user,
                'Profile': profile
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the user column
        user_col = next((col for col in profile.columns if col.name == 'user'), None)
        
        # Assertions
        assert user_col is not None, "User column should exist"
        assert user_col.is_fk is True, "Column should be marked as FK for one-to-one relationship"
        assert user_col.db_column == 'user_id', "db_column should be inferred as 'user_id'"
    
    def test_many_to_one_relationship_fk_detection(self):
        """
        Test FK detection for many-to-one relationships.
        
        Scenario: A many-to-one relationship (multiple posts to one user).
        
        Expected: FK column should be marked correctly.
        """
        # Create entities
        user = Entity(
            name='User',
            table_name='user',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        post = Entity(
            name='Post',
            table_name='post',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name='author', type='int', db_column='author', nullable=False)
            ]
        )
        
        # Create many-to-one relationship
        relationship = Relationship(
            left_entity='User',
            right_entity='Post',
            relation_type='many-to-one',
            left_column='id',
            right_column='author'
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'User': user,
                'Post': post
            },
            relationships=[relationship]
        )
        
        # Apply FK detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the author column
        author_col = next((col for col in post.columns if col.name == 'author'), None)
        
        # Assertions
        assert author_col is not None, "Author column should exist"
        assert author_col.is_fk is True, "Column should be marked as FK for many-to-one relationship"
        assert author_col.db_column == 'author_id', "db_column should be inferred as 'author_id'"
