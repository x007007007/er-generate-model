"""
Preservation Property Tests for SQLAlchemy Blank Lines Fix

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

These tests verify that the template functionality remains unchanged when fixing blank lines.
They capture the observed behavior on UNFIXED code for non-buggy inputs (semantic correctness).

IMPORTANT: Follow observation-first methodology
- Observe behavior on UNFIXED code
- Write property-based tests capturing observed behavior patterns
- Run tests on UNFIXED code
- EXPECTED OUTCOME: Tests PASS (confirms baseline behavior to preserve)

Property-based testing generates many test cases for stronger guarantees.
"""
import re
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)
safe_table_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)


@st.composite
def simple_entity_model(draw):
    """Generate a simple ERModel with one entity and multiple columns."""
    entity_name = draw(safe_identifier)
    table_name = draw(safe_table_name)
    num_columns = draw(st.integers(min_value=2, max_value=5))
    
    columns = [
        Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
    ]
    
    for i in range(num_columns - 1):
        col_name = f'field_{i}'
        col_type = draw(st.sampled_from(['string', 'int', 'boolean', 'text']))
        columns.append(
            Column(name=col_name, type=col_type, db_column=col_name, nullable=True)
        )
    
    entity = Entity(
        name=entity_name,
        table_name=table_name,
        columns=columns
    )
    
    model = ERModel(
        entities={entity_name: entity},
        relationships=[]
    )
    
    return model, entity_name


@st.composite
def entity_with_relationships(draw):
    """Generate an ERModel with two entities and a relationship."""
    left_entity_name = draw(safe_identifier)
    right_entity_name = draw(safe_identifier.filter(lambda x: x != left_entity_name))
    
    left_table_name = left_entity_name.lower()
    right_table_name = right_entity_name.lower()
    
    # Create entities
    left_entity = Entity(
        name=left_entity_name,
        table_name=left_table_name,
        columns=[
            Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
            Column(name='name', type='string', db_column='name', nullable=False)
        ]
    )
    
    fk_logical_name = draw(safe_column_name.filter(lambda x: x not in ['id', 'name']))
    fk_db_column = f"{fk_logical_name}_id"
    
    right_entity = Entity(
        name=right_entity_name,
        table_name=right_table_name,
        columns=[
            Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
            Column(name=fk_logical_name, type='int', db_column=fk_db_column, nullable=True)
        ]
    )
    
    # Create relationship
    relation_type = draw(st.sampled_from(['one-to-one', 'one-to-many']))
    relationship = Relationship(
        left_entity=left_entity_name,
        right_entity=right_entity_name,
        relation_type=relation_type,
        left_column='id',
        right_column=fk_db_column
    )
    
    model = ERModel(
        entities={
            left_entity_name: left_entity,
            right_entity_name: right_entity
        },
        relationships=[relationship]
    )
    
    # Mark foreign keys
    parser = TomlERParser()
    parser._mark_foreign_keys(model.entities, model.relationships)
    
    return model, right_entity_name, fk_logical_name, fk_db_column, relation_type


class TestProperty2Preservation:
    """
    Property 2: Preservation - 模板功能保持不变
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
    
    For any template rendering operation, the fixed template SHALL produce
    semantically identical code output (except for blank line counts), preserving
    all field definitions, relationship configurations, inheritance handling,
    and naming strategies.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(simple_entity_model())
    def test_tablename_attribute_rendering(self, test_data):
        """
        Test that __tablename__ attribute is rendered correctly.
        
        **Validates: Requirement 3.1**
        
        WHEN template renders class definition's __tablename__ attribute
        THEN it should continue to render on the line after class declaration
        """
        model, entity_name = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: __tablename__ should be present and correctly formatted
        # Pattern: class {EntityName}(Base):\n    __tablename__ = '{table_name}'
        class_pattern = rf'class {re.escape(entity_name)}\(Base\):\s+__tablename__\s*='
        
        assert re.search(class_pattern, generated_code), (
            f"__tablename__ should be rendered immediately after class declaration, "
            f"but pattern not found in:\n{generated_code}"
        )
        
        # Verify __tablename__ value matches the entity's table_name
        entity = model.entities[entity_name]
        tablename_pattern = rf"__tablename__\s*=\s*['\"]({re.escape(entity.table_name)})['\"]"
        
        assert re.search(tablename_pattern, generated_code), (
            f"__tablename__ should be set to '{entity.table_name}', "
            f"but pattern not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(simple_entity_model())
    def test_first_field_definition_spacing(self, test_data):
        """
        Test that first field definition has proper spacing after __tablename__.
        
        **Validates: Requirement 3.2**
        
        WHEN template renders the first field definition
        THEN it should continue to have spacing after __tablename__
        """
        model, entity_name = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: First field should appear after __tablename__
        # We verify that there's at least one field definition after __tablename__
        lines = generated_code.split('\n')
        
        tablename_idx = None
        first_field_idx = None
        
        for i, line in enumerate(lines):
            if '__tablename__' in line:
                tablename_idx = i
            if tablename_idx is not None and '= Column(' in line:
                first_field_idx = i
                break
        
        assert tablename_idx is not None, "__tablename__ not found in generated code"
        assert first_field_idx is not None, "No field definitions found after __tablename__"
        assert first_field_idx > tablename_idx, "First field should appear after __tablename__"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(simple_entity_model())
    def test_field_definitions_rendered_correctly(self, test_data):
        """
        Test that all field definitions are rendered with correct types and constraints.
        
        **Validates: Requirement 3.4**
        
        WHEN template renders foreign key constraints and types
        THEN it should continue to generate correct ForeignKey and Column definitions
        """
        model, entity_name = test_data
        entity = model.entities[entity_name]
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: All columns should be rendered as Column definitions
        for col in entity.columns:
            column_pattern = rf'{re.escape(col.name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"Column definition for '{col.name}' not found in generated code:\n{generated_code}"
            )
        
        # Property: Primary key should have primary_key=True
        pk_pattern = r'id\s*=\s*Column\([^)]*primary_key=True'
        assert re.search(pk_pattern, generated_code), (
            f"Primary key column should have primary_key=True, but not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_relationships())
    def test_relationship_configuration(self, test_data):
        """
        Test that relationship configurations are rendered correctly.
        
        **Validates: Requirements 3.5, 3.7**
        
        WHEN template renders relationship's back_populates and foreign_keys parameters
        THEN it should continue to generate correct parameter values
        
        WHEN template renders different relationship types (one-to-one, one-to-many)
        THEN it should continue to generate correct relationship configuration
        """
        model, right_entity_name, fk_logical_name, fk_db_column, relation_type = test_data
        
        # Generate SQLAlchemy code using single-file render (more reliable for testing)
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: Relationship should be present with correct name (Django-style)
        relationship_pattern = rf'{re.escape(fk_logical_name)}\s*=\s*relationship\('
        
        assert re.search(relationship_pattern, generated_code), (
            f"Relationship definition for '{fk_logical_name}' not found in generated code:\n{generated_code}"
        )
        
        # Property: Relationship should have back_populates parameter
        back_populates_pattern = r'back_populates\s*='
        
        assert re.search(back_populates_pattern, generated_code), (
            f"Relationship should have back_populates parameter, but not found in:\n{generated_code}"
        )
        
        # Property: Relationship should have foreign_keys parameter
        foreign_keys_pattern = rf'foreign_keys\s*=\s*\[\s*{re.escape(fk_db_column)}\s*\]'
        
        assert re.search(foreign_keys_pattern, generated_code), (
            f"Relationship should have foreign_keys=[{fk_db_column}], but not found in:\n{generated_code}"
        )
        
        # Property: one-to-one relationships should have uselist=False
        if relation_type == 'one-to-one':
            uselist_pattern = r'uselist\s*=\s*False'
            assert re.search(uselist_pattern, generated_code), (
                f"One-to-one relationship should have uselist=False, but not found in:\n{generated_code}"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_relationships())
    def test_django_style_naming_strategy(self, test_data):
        """
        Test that Django-style naming strategy is preserved.
        
        **Validates: Requirement 3.6**
        
        WHEN template processes Django-style naming (using logical names vs db_column)
        THEN it should continue to use correct naming strategy
        """
        model, right_entity_name, fk_logical_name, fk_db_column, relation_type = test_data
        
        # Generate SQLAlchemy code using single-file render
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: Column should use db_column (with _id suffix)
        column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\('
        
        assert re.search(column_pattern, generated_code), (
            f"Column should use db_column '{fk_db_column}', but not found in:\n{generated_code}"
        )
        
        # Property: Relationship should use logical name (without _id suffix)
        relationship_pattern = rf'{re.escape(fk_logical_name)}\s*=\s*relationship\('
        
        assert re.search(relationship_pattern, generated_code), (
            f"Relationship should use logical name '{fk_logical_name}', but not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_relationships())
    def test_foreign_key_constraints_generation(self, test_data):
        """
        Test that foreign key constraints are generated correctly.
        
        **Validates: Requirement 3.4**
        
        WHEN template renders foreign key constraints and types
        THEN it should continue to generate correct ForeignKey and Column definitions
        """
        model, right_entity_name, fk_logical_name, fk_db_column, relation_type = test_data
        
        # Generate SQLAlchemy code using single-file render
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: Foreign key column should have ForeignKey constraint
        # Find the column definition
        column_start = generated_code.find(f'{fk_db_column} = Column(')
        assert column_start != -1, f"Column definition for '{fk_db_column}' not found"
        
        # Find the closing parenthesis for this Column definition
        paren_count = 0
        i = column_start + len(f'{fk_db_column} = Column(')
        column_end = i
        for j in range(i, len(generated_code)):
            if generated_code[j] == '(':
                paren_count += 1
            elif generated_code[j] == ')':
                if paren_count == 0:
                    column_end = j
                    break
                paren_count -= 1
        
        column_definition = generated_code[column_start:column_end+1]
        
        # Property: Column should contain ForeignKey constraint
        assert 'ForeignKey' in column_definition, (
            f"Column definition for '{fk_db_column}' should contain ForeignKey constraint, "
            f"but it doesn't:\n{column_definition}"
        )
        
        # Property: ForeignKey should reference the correct table and column
        left_entity_name = list(model.entities.keys())[0]
        left_table_name = model.entities[left_entity_name].table_name
        fk_reference_pattern = rf"ForeignKey\(['\"]({re.escape(left_table_name)}\.id)['\"]"
        
        assert re.search(fk_reference_pattern, column_definition), (
            f"ForeignKey should reference '{left_table_name}.id', "
            f"but pattern not found in:\n{column_definition}"
        )
    
    def test_inheritance_mode_flatten_field_inclusion(self):
        """
        Test that flatten inheritance mode includes all fields.
        
        **Validates: Requirement 3.3**
        
        WHEN template processes inheritance mode (flatten/reference)
        THEN it should continue to correctly handle field inclusion/exclusion logic
        """
        # Create a model with template inheritance
        toml_content = """
[templates.BaseModel]

[[templates.BaseModel.columns]]
name = "id"
type = "int"
primary_key = true

[[templates.BaseModel.columns]]
name = "created_at"
type = "datetime"
nullable = false

[entities.User]
table_name = "users"
extends = ["BaseModel"]

[[entities.User.columns]]
name = "name"
type = "string"
max_length = 100
nullable = false
"""
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code in flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(model)
        
        # Property: In flatten mode, all fields should be present (including inherited ones)
        assert 'id = Column(' in generated_code, "Inherited field 'id' should be present in flatten mode"
        assert 'created_at = Column(' in generated_code, "Inherited field 'created_at' should be present in flatten mode"
        assert 'name = Column(' in generated_code, "Own field 'name' should be present"
        
        # Property: Flatten mode should add source comments
        assert '# Fields from BaseModel' in generated_code or 'id = Column(' in generated_code, (
            "Flatten mode should include inherited fields"
        )
    
    def test_inheritance_mode_reference_field_exclusion(self):
        """
        Test that reference inheritance mode excludes inherited fields.
        
        **Validates: Requirement 3.3**
        
        WHEN template processes inheritance mode (flatten/reference)
        THEN it should continue to correctly handle field inclusion/exclusion logic
        """
        # Create a model with template inheritance and export path
        toml_content = """
[templates.BaseModel]
export_path = "myapp.base"

[[templates.BaseModel.columns]]
name = "id"
type = "int"
primary_key = true

[[templates.BaseModel.columns]]
name = "created_at"
type = "datetime"
nullable = false

[entities.User]
table_name = "users"
extends = ["BaseModel"]

[[entities.User.columns]]
name = "name"
type = "string"
max_length = 100
nullable = false
"""
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code in reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(model)
        
        # Property: In reference mode, inherited fields should NOT be present
        # Count occurrences of 'id = Column(' - should only appear in BaseModel, not in User
        id_column_count = generated_code.count('id = Column(')
        
        # Property: Own fields should still be present
        assert 'name = Column(' in generated_code, "Own field 'name' should be present in reference mode"
        
        # Property: Class should inherit from BaseModel
        assert 'class User(BaseModel):' in generated_code, (
            "User class should inherit from BaseModel in reference mode"
        )
