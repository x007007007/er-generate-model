"""
Tests for Task 7.4: 确保 TOML 输出符合规范

This test file verifies that the TOMLRenderer produces valid TOML output
that conforms to the TOML specification, including:
- Proper special character escaping
- Valid TOML format using toml.dumps()
- Compliance with requirements 10.6 and 10.7
"""
import pytest
import toml
from x007007007.er.models import Entity, Column, ERModel, Relationship
from x007007007.er_django.renderers import TOMLRenderer


class TestTOMLCompliance:
    """Test TOML output compliance with TOML specification - Task 7.4"""
    
    def test_toml_output_is_valid_parseable(self):
        """Test that TOML output can be parsed back without errors - Requirement 10.6"""
        # Create a complex entity with various field types
        entity = Entity(
            name="User", table_name="user",
            extends=["django.contrib.auth.models.AbstractUser"],
            package="kinkotech.common.domains.account.models",
            export_path="src/kinkotech/common/domains/account/models.toml",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True, nullable=False),
                Column(name="username", db_column="username", type="CharField", max_length=150, unique=True, nullable=False),
                Column(name="email", db_column="email", type="EmailField", max_length=254, nullable=True),
                Column(name="is_active", db_column="is_active", type="BooleanField", default=True, nullable=False),
                Column(name="created_at", db_column="created_at", type="DateTimeField", nullable=False),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML by parsing it
        try:
            data = toml.loads(toml_output)
            assert data is not None
            assert "entities" in data
            assert "User" in data["entities"]
        except toml.TomlDecodeError as e:
            pytest.fail(f"Generated TOML is not valid: {e}")
    
    def test_special_characters_in_strings_are_escaped(self):
        """Test that special characters in strings are properly escaped - Requirement 10.7"""
        # Create entity with special characters in various fields
        entity = Entity(
            name="TestModel", table_name="test_model",
            package='test.models',
            columns=[
                # Test backslash
                Column(name="path", db_column="path", type="CharField", max_length=255, comment="Path with \\ backslash"),
                # Test quotes
                Column(name="quote", db_column="quote", type="CharField", max_length=100, comment='Field with "quotes"'),
                # Test newline
                Column(name="multiline", db_column="multiline", type="TextField", comment="Line 1\nLine 2"),
                # Test tab
                Column(name="tabbed", db_column="tabbed", type="CharField", max_length=50, comment="Tab\there"),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML
        try:
            data = toml.loads(toml_output)
            
            # Verify special characters are preserved correctly after parsing
            columns = data["entities"]["TestModel"]["columns"]
            
            # Find each column by name and check comment
            path_col = next(c for c in columns if c["name"] == "path")
            assert "\\" in path_col["comment"]
            
            quote_col = next(c for c in columns if c["name"] == "quote")
            assert '"' in quote_col["comment"]
            
            multiline_col = next(c for c in columns if c["name"] == "multiline")
            assert "\n" in multiline_col["comment"]
            
            tabbed_col = next(c for c in columns if c["name"] == "tabbed")
            assert "\t" in tabbed_col["comment"]
            
        except toml.TomlDecodeError as e:
            pytest.fail(f"TOML with special characters is not valid: {e}")
    
    def test_unicode_characters_are_handled_correctly(self):
        """Test that Unicode characters are handled correctly - Requirement 10.7"""
        # Create entity with Unicode characters
        entity = Entity(
            name="InternationalModel", table_name="international_model",
            package="test.models",
            columns=[
                Column(name="chinese", db_column="chinese", type="CharField", max_length=100, comment="中文字符"),
                Column(name="japanese", db_column="japanese", type="CharField", max_length=100, comment="日本語"),
                Column(name="emoji", db_column="emoji", type="CharField", max_length=50, comment="Emoji: 😀🎉"),
                Column(name="arabic", db_column="arabic", type="CharField", max_length=100, comment="العربية"),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML and Unicode is preserved
        try:
            data = toml.loads(toml_output)
            columns = data["entities"]["InternationalModel"]["columns"]
            
            chinese_col = next(c for c in columns if c["name"] == "chinese")
            assert "中文字符" in chinese_col["comment"]
            
            japanese_col = next(c for c in columns if c["name"] == "japanese")
            assert "日本語" in japanese_col["comment"]
            
            emoji_col = next(c for c in columns if c["name"] == "emoji")
            assert "😀" in emoji_col["comment"]
            assert "🎉" in emoji_col["comment"]
            
            arabic_col = next(c for c in columns if c["name"] == "arabic")
            assert "العربية" in arabic_col["comment"]
            
        except toml.TomlDecodeError as e:
            pytest.fail(f"TOML with Unicode characters is not valid: {e}")
    
    def test_toml_uses_standard_format(self):
        """Test that TOML output uses standard format via toml.dumps() - Requirement 10.6"""
        # Create a simple entity
        entity = Entity(
            name="SimpleModel", table_name="simple_model",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True),
                Column(name="name", db_column="name", type="CharField", max_length=100),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse and re-dump to verify format consistency
        data = toml.loads(toml_output)
        re_dumped = toml.dumps(data)
        
        # Both should be parseable and produce the same data structure
        original_data = toml.loads(toml_output)
        re_parsed_data = toml.loads(re_dumped)
        
        assert original_data == re_parsed_data
    
    def test_empty_strings_are_handled_correctly(self):
        """Test that empty strings are handled correctly - Requirement 10.7"""
        # Create entity with empty string default
        entity = Entity(
            name="TestModel", table_name="test_model",
            columns=[
                Column(name="empty_field", db_column="empty_field", type="CharField", max_length=50, default=""),
                Column(name="normal_field", db_column="normal_field", type="CharField", max_length=50, default="value"),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML
        try:
            data = toml.loads(toml_output)
            columns = data["entities"]["TestModel"]["columns"]
            
            empty_col = next(c for c in columns if c["name"] == "empty_field")
            assert empty_col["default"] == ""
            
            normal_col = next(c for c in columns if c["name"] == "normal_field")
            assert normal_col["default"] == "value"
            
        except toml.TomlDecodeError as e:
            pytest.fail(f"TOML with empty strings is not valid: {e}")
    
    def test_special_characters_in_entity_names(self):
        """Test that entity names with special characters are handled - Requirement 10.7"""
        # Note: In practice, Python class names shouldn't have special chars,
        # but we test the renderer's robustness
        entity = Entity(
            name="User_Profile", table_name="user__profile",  # Underscore is common
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML
        try:
            data = toml.loads(toml_output)
            assert "User_Profile" in data["entities"]
        except toml.TomlDecodeError as e:
            pytest.fail(f"TOML with special entity names is not valid: {e}")
    
    def test_relationships_are_valid_toml(self):
        """Test that relationships section produces valid TOML - Requirement 10.6"""
        # Create entities with relationships
        user = Entity(
            name="User", table_name="user",
            columns=[Column(name="id", db_column="id", type="IntegerField", is_pk=True)]
        )
        
        profile = Entity(
            name="Profile", table_name="profile",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True),
                Column(name="user_id", db_column="user_id", type="IntegerField", nullable=False),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(user)
        er_model.add_entity(profile)
        
        # Add relationship
        relationship = Relationship(
            left_entity="User",
            right_entity="Profile",
            relation_type="one-to-one",
            left_column="id",
            right_column="user_id"
        )
        er_model.add_relationship(relationship)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML
        try:
            data = toml.loads(toml_output)
            assert "relationships" in data
            assert len(data["relationships"]) == 1
            assert data["relationships"][0]["left"] == "User"
            assert data["relationships"][0]["right"] == "Profile"
            assert data["relationships"][0]["type"] == "one-to-one"
        except toml.TomlDecodeError as e:
            pytest.fail(f"TOML with relationships is not valid: {e}")
    
    def test_complex_model_with_all_features(self):
        """Test a complex model with all features produces valid TOML - Requirements 10.6, 10.7"""
        # Create a complex entity with all possible features
        entity = Entity(
            name="ComplexModel", table_name="complex_model",
            extends=["django.contrib.auth.models.AbstractUser", "kinkotech.common.base.TimeStampedModel"],
            package="kinkotech.complex.models",
            export_path="src/kinkotech/complex/models.toml",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True, nullable=False),
                Column(name="name", db_column="name", type="CharField", max_length=200, unique=True, nullable=False, comment="User's full name"),
                Column(name="email", db_column="email", type="EmailField", max_length=254, unique=True, nullable=False),
                Column(name="bio", db_column="bio", type="TextField", nullable=True, comment="Biography with\nnewlines and \"quotes\""),
                Column(name="age", db_column="age", type="IntegerField", nullable=True, default=0),
                Column(name="score", db_column="score", type="DecimalField", precision=10, scale=2, nullable=True),
                Column(name="is_active", db_column="is_active", type="BooleanField", default=True, nullable=False),
                Column(name="path", db_column="path", type="CharField", max_length=500, comment="Path: C:\\Users\\test"),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Verify it's valid TOML
        try:
            data = toml.loads(toml_output)
            
            # Verify all fields are present and correct
            assert "entities" in data
            assert "ComplexModel" in data["entities"]
            
            model_data = data["entities"]["ComplexModel"]
            
            # Check metadata fields
            assert "extends" in model_data
            assert len(model_data["extends"]) == 2
            assert "package" in model_data
            assert model_data["package"] == "kinkotech.complex.models"
            # export_path should NOT be present (removed in Task 3.1)
            assert "export_path" not in model_data
            
            # Check columns
            assert "columns" in model_data
            assert len(model_data["columns"]) == 8
            
            # Verify special characters in comments are preserved
            bio_col = next(c for c in model_data["columns"] if c["name"] == "bio")
            assert "\n" in bio_col["comment"]
            assert '"' in bio_col["comment"]
            
            path_col = next(c for c in model_data["columns"] if c["name"] == "path")
            assert "\\" in path_col["comment"]
            
        except toml.TomlDecodeError as e:
            pytest.fail(f"Complex TOML model is not valid: {e}")
    
    def test_toml_roundtrip_preserves_data(self):
        """Test that TOML can be dumped and loaded without data loss - Requirement 10.6"""
        # Create entity with various data types
        entity = Entity(
            name="RoundtripModel", table_name="roundtrip_model",
            extends=["BaseModel"],
            package="test.models",
            export_path="test/models.toml",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True, nullable=False),
                Column(name="name", db_column="name", type="CharField", max_length=100, unique=True, nullable=False),
                Column(name="count", db_column="count", type="IntegerField", default=0, nullable=True),
                Column(name="active", db_column="active", type="BooleanField", default=True, nullable=False),
                Column(name="price", db_column="price", type="DecimalField", precision=10, scale=2, nullable=True),
                Column(name="description", db_column="description", type="TextField", nullable=True, comment="Test comment"),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse it
        data1 = toml.loads(toml_output)
        
        # Dump it again
        toml_output2 = toml.dumps(data1)
        
        # Parse the second output
        data2 = toml.loads(toml_output2)
        
        # Both parsed data structures should be identical
        assert data1 == data2
    
    def test_null_values_are_not_included(self):
        """Test that None/null values are not included in TOML output - Requirement 10.6"""
        # Create entity with some None values
        entity = Entity(
            name="NullTestModel", table_name="null_test_model",
            extends=[],  # Empty, should not be included
            package=None,  # None, should not be included
            export_path=None,  # None, should not be included
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True),
                Column(name="optional", db_column="optional", type="CharField", max_length=50, nullable=True, default=None),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse and verify
        data = toml.loads(toml_output)
        model_data = data["entities"]["NullTestModel"]
        
        # These fields should not be present
        assert "extends" not in model_data
        assert "package" not in model_data
        assert "export_path" not in model_data
        
        # Columns should be present
        assert "columns" in model_data
    
    def test_boolean_values_are_correct_type(self):
        """Test that boolean values are rendered as TOML booleans - Requirement 10.6"""
        # Create entity with boolean fields
        entity = Entity(
            name="BooleanTestModel", table_name="boolean_test_model",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True, nullable=False),
                Column(name="active", db_column="active", type="BooleanField", default=True, nullable=False),
                Column(name="deleted", db_column="deleted", type="BooleanField", default=False, nullable=False),
                Column(name="optional", db_column="optional", type="CharField", max_length=50, unique=True, nullable=True),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse and verify
        data = toml.loads(toml_output)
        columns = data["entities"]["BooleanTestModel"]["columns"]
        
        # Check that boolean values are actual booleans, not strings
        id_col = next(c for c in columns if c["name"] == "id")
        assert id_col["primary_key"] is True
        assert isinstance(id_col["primary_key"], bool)
        assert id_col["nullable"] is False
        assert isinstance(id_col["nullable"], bool)
        
        active_col = next(c for c in columns if c["name"] == "active")
        assert active_col["default"] is True
        assert isinstance(active_col["default"], bool)
        
        deleted_col = next(c for c in columns if c["name"] == "deleted")
        assert deleted_col["default"] is False
        assert isinstance(deleted_col["default"], bool)
        
        optional_col = next(c for c in columns if c["name"] == "optional")
        assert optional_col["unique"] is True
        assert isinstance(optional_col["unique"], bool)
    
    def test_integer_values_are_correct_type(self):
        """Test that integer values are rendered as TOML integers - Requirement 10.6"""
        # Create entity with integer fields
        entity = Entity(
            name="IntegerTestModel", table_name="integer_test_model",
            columns=[
                Column(name="id", db_column="id", type="IntegerField", is_pk=True),
                Column(name="max_length_field", db_column="max_length_field", type="CharField", max_length=255),
                Column(name="precision_field", db_column="precision_field", type="DecimalField", precision=10, scale=2),
                Column(name="default_int", db_column="default_int", type="IntegerField", default=42),
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse and verify
        data = toml.loads(toml_output)
        columns = data["entities"]["IntegerTestModel"]["columns"]
        
        # Check that integer values are actual integers, not strings
        max_length_col = next(c for c in columns if c["name"] == "max_length_field")
        assert max_length_col["max_length"] == 255
        assert isinstance(max_length_col["max_length"], int)
        
        precision_col = next(c for c in columns if c["name"] == "precision_field")
        assert precision_col["precision"] == 10
        assert isinstance(precision_col["precision"], int)
        assert precision_col["scale"] == 2
        assert isinstance(precision_col["scale"], int)
        
        default_col = next(c for c in columns if c["name"] == "default_int")
        assert default_col["default"] == 42
        assert isinstance(default_col["default"], int)
