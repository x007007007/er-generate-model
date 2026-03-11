"""
Property-based tests for entity rendering with mixins.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import ast
import keyword
import re
from pathlib import Path
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from x007007007.er.models import ERModel, Entity, Column, TemplateInfo
from x007007007.er.renderers.python.sqlalchemy.renderer import SQLAlchemyRenderer


# Custom strategies for generating valid test data
valid_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(
    lambda s: len(s) > 0 and len(s) < 30
)

valid_package_component = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) > 0 and len(s) < 20 and not s.startswith('_') and not keyword.iskeyword(s)
)


@st.composite
def valid_export_path(draw, min_components=1, max_components=5):
    """Generate a valid export path."""
    num_components = draw(st.integers(min_value=min_components, max_value=max_components))
    components = [draw(valid_package_component) for _ in range(num_components)]
    return '.'.join(components)


@st.composite
def valid_column(draw):
    """Generate a valid Column object."""
    col_types = ['string', 'integer', 'bigint', 'datetime', 'boolean', 'text']
    col_type = draw(st.sampled_from(col_types))
    
    name = draw(st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
        lambda s: len(s) > 0 and len(s) < 20
    ))
    
    max_length = draw(st.integers(min_value=1, max_value=500)) if col_type == 'string' else None
    
    # Generate valid comment text (printable ASCII characters only, no null bytes)
    comment_text = draw(st.one_of(
        st.none(),
        st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=50
        )
    ))
    
    return Column(
        name=name,
        type=col_type,
        db_column=name,
        is_pk=draw(st.booleans()),
        nullable=draw(st.booleans()),
        unique=draw(st.booleans()),
        indexed=draw(st.booleans()),
        max_length=max_length,
        comment=comment_text
    )


@st.composite
def entity_with_templates(draw, inheritance_mode='reference'):
    """Generate an entity with templates for testing."""
    entity_name = draw(valid_identifier)
    table_name = draw(st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True))
    
    # Generate 1-3 templates
    num_templates = draw(st.integers(min_value=1, max_value=3))
    templates = {}
    template_names = []
    
    for i in range(num_templates):
        template_name = draw(valid_identifier)
        export_path = draw(valid_export_path())
        columns = draw(st.lists(valid_column(), min_size=1, max_size=5))
        
        templates[template_name] = {
            'name': template_name,
            'package': f"test.{export_path}",
            'export_path': export_path,
            'columns': columns,
            'source_file': 'test.toml'
        }
        template_names.append(template_name)
    
    # Generate entity-specific columns
    entity_columns = draw(st.lists(valid_column(), min_size=1, max_size=5))
    
    # In flatten mode, expand template columns into entity columns
    if inheritance_mode == 'flatten':
        # Prepend template columns to entity columns (template fields first)
        all_columns = []
        for template_name in template_names:
            for col in templates[template_name]['columns']:
                # Create a copy with source template metadata
                col_copy = Column(
                    name=col.name,
                    type=col.type,
                    db_column=col.db_column,
                    is_pk=col.is_pk,
                    is_fk=col.is_fk,
                    nullable=col.nullable,
                    comment=col.comment,
                    default=col.default,
                    max_length=col.max_length,
                    precision=col.precision,
                    scale=col.scale,
                    unique=col.unique,
                    indexed=col.indexed
                )
                col_copy._source_template = template_name
                all_columns.append(col_copy)
        all_columns.extend(entity_columns)
        entity_columns = all_columns
    
    entity = Entity(
        name=entity_name,
        table_name=table_name,
        columns=entity_columns,
        extends=template_names
    )
    
    model = ERModel()
    model.entities[entity_name] = entity
    model.templates = templates
    
    return model, entity, templates


class TestProperty12ReferenceModeImportGeneration:
    """
    Property 12: Reference Mode Import Generation
    
    **Validates: Requirements 5.1**
    
    For any entity extending templates in reference mode, the generated code
    should include import statements for all mixin classes.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='reference'))
    def test_import_statements_generated_for_mixins(self, test_data):
        """
        Test that import statements are generated for all referenced mixins.
        
        This verifies Requirement 5.1: WHEN an entity extends templates in
        reference mode, THE Entity_Renderer SHALL generate import statements
        for the mixin classes.
        """
        model, entity, templates = test_data
        
        # Render in reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='reference'
        )
        
        # Property: For each template, there should be an import statement
        for template_name in entity.extends:
            if template_name in templates:
                export_path = templates[template_name]['export_path']
                import_pattern = f'from {export_path} import {template_name}'
                
                assert import_pattern in content, (
                    f"Missing import statement for mixin:\n"
                    f"  Template: {template_name}\n"
                    f"  Expected: {import_pattern}\n"
                    f"  Content preview: {content[:1000]}"
                )


class TestProperty13ReferenceModeInheritance:
    """
    Property 13: Reference Mode Inheritance
    
    **Validates: Requirements 5.2**
    
    For any entity extending templates in reference mode, the generated class
    should inherit from all referenced mixin classes.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='reference'))
    def test_class_inherits_from_mixins(self, test_data):
        """
        Test that the entity class inherits from all referenced mixins.
        
        This verifies Requirement 5.2: WHEN an entity extends templates in
        reference mode, THE Entity_Renderer SHALL include mixins in the class
        inheritance list.
        """
        model, entity, templates = test_data
        
        # Render in reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='reference'
        )
        
        # Property: Class definition should include all template names in inheritance
        template_names = [t for t in entity.extends if t in templates]
        
        if template_names:
            # Build expected class definition pattern
            inheritance_list = ', '.join(template_names)
            class_pattern = f'class {entity.name}({inheritance_list})'
            
            assert class_pattern in content, (
                f"Class does not inherit from mixins:\n"
                f"  Entity: {entity.name}\n"
                f"  Expected inheritance: {inheritance_list}\n"
                f"  Content preview: {content[:1000]}"
            )


class TestProperty14FlattenModeFieldExpansion:
    """
    Property 14: Flatten Mode Field Expansion
    
    **Validates: Requirements 5.3**
    
    For any entity extending templates in flatten mode, all fields from all
    referenced templates should be expanded inline in the entity.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='flatten'))
    def test_template_fields_expanded_inline(self, test_data):
        """
        Test that all template fields are expanded inline in flatten mode.
        
        This verifies Requirement 5.3: WHEN an entity extends templates in
        flatten mode, THE Entity_Renderer SHALL expand all mixin fields inline.
        """
        model, entity, templates = test_data
        
        # Render in flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='flatten'
        )
        
        # Property: All columns from all templates should appear in the entity
        for template_name in entity.extends:
            if template_name in templates:
                template_columns = templates[template_name]['columns']
                
                for col in template_columns:
                    column_pattern = f'{col.name} = Column('
                    
                    assert column_pattern in content, (
                        f"Template column not expanded inline:\n"
                        f"  Template: {template_name}\n"
                        f"  Column: {col.name}\n"
                        f"  Expected pattern: {column_pattern}\n"
                        f"  Content preview: {content[:2000]}"
                    )


class TestProperty15FieldOrderPreservation:
    """
    Property 15: Field Order Preservation
    
    **Validates: Requirements 5.4**
    
    For any entity with template inheritance, the order of fields should be
    preserved (template fields first, then entity-specific fields).
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='flatten'))
    def test_field_order_preserved(self, test_data):
        """
        Test that field order is preserved in flatten mode.
        
        This verifies Requirement 5.4: THE Entity_Renderer SHALL preserve the
        order of fields from templates and entity-specific columns.
        """
        model, entity, templates = test_data
        
        # Render in flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='flatten'
        )
        
        # Property: Template fields should appear before entity fields
        # Find positions of template columns and entity columns
        template_column_positions = []
        entity_column_positions = []
        
        # Use the _source_template attribute to identify template columns
        # Build a mapping of column names to their source
        column_sources = {}
        for col in entity.columns:
            if hasattr(col, '_source_template'):
                # This is a template column
                if col.name not in column_sources:
                    column_sources[col.name] = []
                column_sources[col.name].append(('template', col._source_template))
            else:
                # This is an entity column
                if col.name not in column_sources:
                    column_sources[col.name] = []
                column_sources[col.name].append(('entity', None))
        
        # Find positions in content
        lines = content.split('\n')
        column_occurrences = {}  # Track how many times we've seen each column name
        
        for i, line in enumerate(lines):
            if ' = Column(' in line:
                # Extract column name
                match = re.match(r'\s+(\w+)\s*=\s*Column\(', line)
                if match:
                    col_name = match.group(1)
                    
                    # Track occurrence count
                    if col_name not in column_occurrences:
                        column_occurrences[col_name] = 0
                    occurrence_idx = column_occurrences[col_name]
                    column_occurrences[col_name] += 1
                    
                    # Check if this occurrence is a template or entity column
                    if col_name in column_sources and occurrence_idx < len(column_sources[col_name]):
                        source_type, _ = column_sources[col_name][occurrence_idx]
                        if source_type == 'template':
                            template_column_positions.append(i)
                        else:
                            entity_column_positions.append(i)
        
        # Property: All template columns should appear before entity columns
        if template_column_positions and entity_column_positions:
            max_template_pos = max(template_column_positions)
            min_entity_pos = min(entity_column_positions)
            
            assert max_template_pos < min_entity_pos, (
                f"Field order not preserved:\n"
                f"  Template columns end at line: {max_template_pos}\n"
                f"  Entity columns start at line: {min_entity_pos}\n"
                f"  Template columns should appear before entity columns"
            )


class TestProperty19CrossFileImportPathCorrectness:
    """
    Property 19: Cross-File Import Path Correctness
    
    **Validates: Requirements 8.3**
    
    For any entity referencing a template from a different file, the generated
    import path should be correct and based on the template's export_path.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='reference'))
    def test_import_path_uses_export_path(self, test_data):
        """
        Test that import paths are based on template export_path.
        
        This verifies Requirement 8.3: WHEN generating entities, THE
        Entity_Renderer SHALL generate correct import paths regardless of which
        file defined the template.
        """
        model, entity, templates = test_data
        
        # Render in reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='reference'
        )
        
        # Property: Import paths should use the export_path from template
        for template_name in entity.extends:
            if template_name in templates:
                export_path = templates[template_name]['export_path']
                
                # The import should use the export_path
                import_line = f'from {export_path} import {template_name}'
                
                assert import_line in content, (
                    f"Import path does not use export_path:\n"
                    f"  Template: {template_name}\n"
                    f"  Export path: {export_path}\n"
                    f"  Expected: {import_line}\n"
                    f"  Content preview: {content[:1000]}"
                )


class TestProperty22EntityImportStatementValidity:
    """
    Property 22: Entity Import Statement Validity
    
    **Validates: Requirements 9.4**
    
    For any entity with template inheritance in reference mode, all import
    statements should be syntactically valid.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='reference'))
    def test_import_statements_syntactically_valid(self, test_data):
        """
        Test that all import statements are syntactically valid.
        
        This verifies Requirement 9.4: THE Entity_Renderer SHALL generate valid
        import statements for mixin classes.
        """
        model, entity, templates = test_data
        
        # Render in reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='reference'
        )
        
        # Property: Code should be parseable by Python AST
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(
                f"Generated code has syntax errors:\n"
                f"  Entity: {entity.name}\n"
                f"  Error: {e}\n"
                f"  Content:\n{content}"
            )
        
        # Property: All import statements should be valid
        # Extract import lines
        import_lines = [line for line in content.split('\n') if line.strip().startswith('from ') and ' import ' in line]
        
        for import_line in import_lines:
            try:
                ast.parse(import_line)
            except SyntaxError as e:
                pytest.fail(
                    f"Invalid import statement:\n"
                    f"  Import: {import_line}\n"
                    f"  Error: {e}"
                )


class TestProperty23EntityInheritanceSyntaxValidity:
    """
    Property 23: Entity Inheritance Syntax Validity
    
    **Validates: Requirements 9.5**
    
    For any entity with template inheritance, the class inheritance syntax
    should be valid Python.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(entity_with_templates(inheritance_mode='reference'))
    def test_inheritance_syntax_valid(self, test_data):
        """
        Test that class inheritance syntax is valid.
        
        This verifies Requirement 9.5: THE Entity_Renderer SHALL generate valid
        class inheritance syntax.
        """
        model, entity, templates = test_data
        
        # Render in reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model,
            entity=entity,
            entity_relationships=[],
            table_prefix='',
            base_model_import=None,
            inheritance_mode='reference'
        )
        
        # Property: Code should be parseable and compilable
        try:
            ast.parse(content)
            compile(content, '<string>', 'exec')
        except SyntaxError as e:
            pytest.fail(
                f"Generated code has syntax errors:\n"
                f"  Entity: {entity.name}\n"
                f"  Error: {e}\n"
                f"  Content:\n{content}"
            )
        
        # Property: Class definition should be valid
        # Extract class definition line
        class_def_pattern = re.compile(r'class\s+(\w+)\s*\((.*?)\):')
        match = class_def_pattern.search(content)
        
        assert match, (
            f"No valid class definition found:\n"
            f"  Entity: {entity.name}\n"
            f"  Content preview: {content[:1000]}"
        )
        
        class_name = match.group(1)
        inheritance_list = match.group(2)
        
        # Property: Class name should match entity name
        assert class_name == entity.name, (
            f"Class name mismatch:\n"
            f"  Expected: {entity.name}\n"
            f"  Got: {class_name}"
        )
        
        # Property: Inheritance list should not be empty
        assert inheritance_list.strip(), (
            f"Empty inheritance list for entity with templates:\n"
            f"  Entity: {entity.name}\n"
            f"  Templates: {entity.extends}"
        )
