"""
Property-based tests for TOML output conditional inclusion of db_column.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.

Feature: field-db-column-and-path-separation
"""
import pytest
import toml
from hypothesis import given, settings as hypothesis_settings, strategies as st
from x007007007.er.models import Column, Entity, ERModel
from x007007007.er_django.renderers import TOMLRenderer


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) < 30 and s not in ['id']
)
safe_db_column = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) < 30
)
safe_table_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) < 30
)


@st.composite
def column_with_db_column(draw):
    """Generate a Column with name and db_column that may or may not be the same."""
    field_name = draw(safe_identifier)
    # Sometimes use same name, sometimes different
    use_different = draw(st.booleans())
    if use_different:
        db_column_name = draw(safe_db_column.filter(lambda s: s != field_name))
    else:
        db_column_name = field_name
    
    field_type = draw(st.sampled_from(['CharField', 'IntegerField', 'TextField', 'EmailField']))
    
    return Column(
        name=field_name,
        type=field_type,
        db_column=db_column_name,
        nullable=draw(st.booleans()),
        unique=draw(st.booleans())
    )


@st.composite
def entity_with_table_name(draw):
    """Generate an Entity with table_name."""
    entity_name = draw(safe_identifier.map(lambda s: s.capitalize()))
    table_name = draw(safe_table_name)
    
    # Generate 1-5 columns
    columns = draw(st.lists(column_with_db_column(), min_size=1, max_size=5))
    
    return Entity(
        name=entity_name,
        table_name=table_name,
        columns=columns
    )


class TestProperty3TOMLOutputConditionalDbColumn:
    """
    Property 3: TOML输出条件包含db_column
    
    **Feature: field-db-column-and-path-separation, Property 3: TOML输出条件包含db_column**
    **Validates: Requirements 1.4**
    
    For any Column object, if db_column differs from name, TOML output must include
    db_column field; if they are the same, db_column should not be output.
    For any Entity object, TOML output must always include table_name field.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(column_with_db_column())
    def test_db_column_output_when_different_from_name(self, column):
        """Test that db_column is output when it differs from name."""
        # Create an entity with the column
        entity = Entity(
            name="TestEntity",
            table_name="test_table",
            columns=[column]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "TestEntity" in data["entities"]
        assert "columns" in data["entities"]["TestEntity"]
        assert len(data["entities"]["TestEntity"]["columns"]) == 1
        
        col_data = data["entities"]["TestEntity"]["columns"][0]
        
        # Verify name is always present
        assert "name" in col_data
        assert col_data["name"] == column.name
        
        # Verify db_column is present only when different from name
        if column.db_column != column.name:
            assert "db_column" in col_data, \
                f"db_column should be present when different from name (name={column.name}, db_column={column.db_column})"
            assert col_data["db_column"] == column.db_column
        else:
            assert "db_column" not in col_data, \
                f"db_column should not be present when same as name (name={column.name}, db_column={column.db_column})"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(st.lists(column_with_db_column(), min_size=1, max_size=10))
    def test_multiple_columns_db_column_conditional_output(self, columns):
        """Test that multiple columns each follow the db_column output rule."""
        # Create an entity with multiple columns
        entity = Entity(
            name="TestEntity",
            table_name="test_table",
            columns=columns
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "TestEntity" in data["entities"]
        assert "columns" in data["entities"]["TestEntity"]
        assert len(data["entities"]["TestEntity"]["columns"]) == len(columns)
        
        # Verify each column follows the rule
        for i, column in enumerate(columns):
            col_data = data["entities"]["TestEntity"]["columns"][i]
            
            # Verify name is always present
            assert "name" in col_data
            assert col_data["name"] == column.name
            
            # Verify db_column is present only when different from name
            if column.db_column != column.name:
                assert "db_column" in col_data, \
                    f"Column {i}: db_column should be present when different from name"
                assert col_data["db_column"] == column.db_column
            else:
                assert "db_column" not in col_data, \
                    f"Column {i}: db_column should not be present when same as name"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(entity_with_table_name())
    def test_table_name_always_output(self, entity):
        """Test that table_name is always output for entities."""
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert entity.name in data["entities"]
        
        # Verify table_name is always present
        assert "table_name" in data["entities"][entity.name], \
            f"table_name must always be present in TOML output"
        assert data["entities"][entity.name]["table_name"] == entity.table_name
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(st.lists(entity_with_table_name(), min_size=1, max_size=5))
    def test_multiple_entities_table_name_always_output(self, entities):
        """Test that table_name is always output for multiple entities."""
        er_model = ERModel()
        
        # Add all entities with unique names
        unique_entities = []
        seen_names = set()
        for entity in entities:
            if entity.name not in seen_names:
                er_model.add_entity(entity)
                unique_entities.append(entity)
                seen_names.add(entity.name)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        
        # Verify each entity has table_name
        for entity in unique_entities:
            assert entity.name in data["entities"]
            assert "table_name" in data["entities"][entity.name], \
                f"Entity {entity.name}: table_name must always be present"
            assert data["entities"][entity.name]["table_name"] == entity.table_name
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(safe_identifier, st.sampled_from(['CharField', 'IntegerField', 'TextField']))
    def test_column_with_same_name_and_db_column(self, field_name, field_type):
        """Test that db_column is not output when it equals name."""
        # Create column where db_column equals name
        column = Column(
            name=field_name,
            type=field_type,
            db_column=field_name  # Same as name
        )
        
        entity = Entity(
            name="TestEntity",
            table_name="test_table",
            columns=[column]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        col_data = data["entities"]["TestEntity"]["columns"][0]
        
        # db_column should NOT be present when same as name
        assert "db_column" not in col_data, \
            f"db_column should not be present when same as name (name={field_name})"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(safe_identifier, safe_db_column, st.sampled_from(['CharField', 'IntegerField', 'TextField']))
    def test_column_with_different_name_and_db_column(self, field_name, db_column_name, field_type):
        """Test that db_column is output when it differs from name."""
        # Ensure they are different
        if field_name == db_column_name:
            db_column_name = db_column_name + "_col"
        
        # Create column where db_column differs from name
        column = Column(
            name=field_name,
            type=field_type,
            db_column=db_column_name  # Different from name
        )
        
        entity = Entity(
            name="TestEntity",
            table_name="test_table",
            columns=[column]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        col_data = data["entities"]["TestEntity"]["columns"][0]
        
        # db_column SHOULD be present when different from name
        assert "db_column" in col_data, \
            f"db_column should be present when different from name (name={field_name}, db_column={db_column_name})"
        assert col_data["db_column"] == db_column_name
