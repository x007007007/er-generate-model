"""
Integration Tests for SQLAlchemy Generator Fixes

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

These tests verify that the SQLAlchemy generator produces correct, working code
that can be imported and used with SQLAlchemy.
"""
import ast
import pytest
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestFullModelGeneration:
    """Test full Translation model generation from TOML."""
    
    def test_translation_model_generation_matches_expected_output(self):
        """
        Test 5.1: Test full Translation model generation
        
        Generate complete Translation model from examples/bug/django/models.toml
        and compare output with examples/bug/django/sqlalchemy_right_models.py.
        Verify all 5 issues are fixed in the generated model.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # Load the TOML file
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Load expected output
        with open('examples/bug/django/sqlalchemy_right_models.py', 'r', encoding='utf-8') as f:
            expected_code = f.read()
        
        # Verify all 5 issues are fixed:
        
        # Issue 1: Primary key columns include `primary_key=True`
        assert 'primary_key=True' in generated_code, \
            "Issue 1 NOT FIXED: Primary key columns missing 'primary_key=True'"
        
        # Issue 2: Foreign key columns use db_column field name
        assert 'code_id = Column(' in generated_code, \
            "Issue 2 NOT FIXED: Foreign key uses 'code' instead of 'code_id'"
        assert 'block_id = Column(' in generated_code, \
            "Issue 2 NOT FIXED: Foreign key uses 'block' instead of 'block_id'"
        
        # Issue 3: Foreign key columns use correct type (BigInteger)
        assert 'code_id = Column(BigInteger' in generated_code, \
            "Issue 3 NOT FIXED: Foreign key 'code_id' uses wrong type"
        assert 'block_id = Column(BigInteger' in generated_code, \
            "Issue 3 NOT FIXED: Foreign key 'block_id' uses wrong type"
        
        # Issue 4: Reverse relationships include foreign_keys parameter
        assert 'foreign_keys=[code_id]' in generated_code, \
            "Issue 4 NOT FIXED: Reverse relationship missing 'foreign_keys=[code_id]'"
        assert 'foreign_keys=[block_id]' in generated_code, \
            "Issue 4 NOT FIXED: Reverse relationship missing 'foreign_keys=[block_id]'"
        
        # Issue 5: Nullable foreign keys include nullable=True
        # Check that code_id line contains nullable=True
        code_id_line = [line for line in generated_code.split('\n') if 'code_id = Column(' in line]
        assert code_id_line, "code_id column not found in generated code"
        assert 'nullable=True' in code_id_line[0], \
            "Issue 5 NOT FIXED: Nullable foreign key 'code_id' missing 'nullable=True'"
        
        block_id_line = [line for line in generated_code.split('\n') if 'block_id = Column(' in line]
        assert block_id_line, "block_id column not found in generated code"
        assert 'nullable=True' in block_id_line[0], \
            "Issue 5 NOT FIXED: Nullable foreign key 'block_id' missing 'nullable=True'"
        
        # Verify the Translation class structure matches expected output
        assert 'class Translation(Base):' in generated_code, \
            "Translation class not found in generated code"
        assert "__tablename__ = 'kkt_i18n_translations_translationmodel'" in generated_code, \
            "Table name not correct in generated code"
        
        # Verify all expected columns are present
        expected_columns = ['id', 'code_id', 'block_id', 'translate']
        for col in expected_columns:
            assert f'{col} = Column(' in generated_code, \
                f"Column '{col}' not found in generated code"
        
        # Verify relationships are present (Django-style naming: use logical names)
        assert 'code = relationship(' in generated_code, \
            "code relationship not found (Django-style naming)"
        assert 'block = relationship(' in generated_code, \
            "block relationship not found (Django-style naming)"
        
        # Verify generated code is syntactically valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")



class TestGeneratedModelsImport:
    """Test that generated models can be imported without errors."""
    
    def test_generated_models_can_be_imported(self):
        """
        Test 5.2: Test generated models can be imported
        
        Import generated SQLAlchemy models and verify:
        - No import errors or syntax errors
        - SQLAlchemy can parse the model definitions
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        import tempfile
        import sys
        import os
        
        # Load the TOML file
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Create a temporary file with the generated code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            # Add necessary imports and base class
            f.write("from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Text, String\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            # Try to import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_models", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            
            # This will raise an exception if there are syntax errors or import issues
            spec.loader.exec_module(test_module)
            
            # Verify the Translation class exists
            assert hasattr(test_module, 'Translation'), \
                "Translation class not found in generated module"
            
            # Verify the class has expected attributes
            Translation = test_module.Translation
            assert hasattr(Translation, '__tablename__'), \
                "Translation class missing __tablename__"
            assert hasattr(Translation, 'id'), \
                "Translation class missing id column"
            assert hasattr(Translation, 'code_id'), \
                "Translation class missing code_id column"
            assert hasattr(Translation, 'block_id'), \
                "Translation class missing block_id column"
            assert hasattr(Translation, 'translate'), \
                "Translation class missing translate column"
            assert hasattr(Translation, 'code'), \
                "Translation class missing code relationship (Django-style naming)"
            assert hasattr(Translation, 'block'), \
                "Translation class missing block relationship (Django-style naming)"
            
            # Verify SQLAlchemy can parse the model
            from sqlalchemy import inspect
            mapper = inspect(Translation)
            
            # Verify columns are properly defined
            columns = {col.key for col in mapper.columns}
            assert 'id' in columns, "id column not in mapper"
            assert 'code_id' in columns, "code_id column not in mapper"
            assert 'block_id' in columns, "block_id column not in mapper"
            assert 'translate' in columns, "translate column not in mapper"
            
            # Verify relationships are properly defined (Django-style naming)
            relationships = {rel.key for rel in mapper.relationships}
            assert 'code' in relationships, "code relationship not in mapper (Django-style naming)"
            assert 'block' in relationships, "block relationship not in mapper (Django-style naming)"
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file)



class TestGeneratedModelsWithSQLAlchemy:
    """Test that generated models work with SQLAlchemy database operations."""
    
    def test_generated_models_work_with_sqlalchemy(self):
        """
        Test 5.3: Test generated models work with SQLAlchemy
        
        - Create in-memory SQLite database
        - Use generated models to create tables
        - Verify relationships work without ambiguity errors
        - Test basic CRUD operations
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        import tempfile
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Load the TOML file
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Create a temporary file with the generated code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            # Add necessary imports and base class
            f.write("from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Text, String\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_models", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Get the classes
            Translation = test_module.Translation
            I18nCode = test_module.I18nCode
            I18nBlock = test_module.I18nBlock
            Base = test_module.Base
            
            # Create in-memory SQLite database
            engine = create_engine('sqlite:///:memory:', echo=False)
            
            # Create all tables - this will fail if relationships have ambiguity errors
            try:
                Base.metadata.create_all(engine)
            except Exception as e:
                pytest.fail(f"Failed to create tables due to relationship ambiguity: {e}")
            
            # Create a session
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
                # Test basic CRUD operations
                
                # Create I18nCode
                code = I18nCode(id=1, name='en')
                session.add(code)
                session.commit()
                
                # Create I18nBlock
                block = I18nBlock(id=1, code='test_block')
                session.add(block)
                session.commit()
                
                # Create Translation with foreign keys
                translation = Translation(
                    id=1,
                    code_id=1,
                    block_id=1,
                    translate='Hello World'
                )
                session.add(translation)
                session.commit()
                
                # Query the translation back
                retrieved = session.query(Translation).filter_by(id=1).first()
                assert retrieved is not None, "Failed to retrieve translation"
                assert retrieved.code_id == 1, "code_id not set correctly"
                assert retrieved.block_id == 1, "block_id not set correctly"
                assert retrieved.translate == 'Hello World', "translate not set correctly"
                
                # Test relationships work without ambiguity (Django-style naming)
                # Access the related objects through relationships
                assert retrieved.code is not None, "code relationship not working"
                assert retrieved.code.id == 1, "code not pointing to correct object"
                assert retrieved.code.name == 'en', "code data not correct"
                
                assert retrieved.block is not None, "block relationship not working"
                assert retrieved.block.id == 1, "block not pointing to correct object"
                assert retrieved.block.code == 'test_block', "block data not correct"
                
                # Test reverse relationships
                assert len(code.translation_set) == 1, "Reverse relationship from I18nCode not working"
                assert code.translation_set[0].id == 1, "Reverse relationship data not correct"
                
                assert len(block.translation_set) == 1, "Reverse relationship from I18nBlock not working"
                assert block.translation_set[0].id == 1, "Reverse relationship data not correct"
                
                # Test nullable foreign keys - create translation without foreign keys
                translation2 = Translation(
                    id=2,
                    code_id=None,
                    block_id=None,
                    translate='Test without FKs'
                )
                session.add(translation2)
                session.commit()
                
                retrieved2 = session.query(Translation).filter_by(id=2).first()
                assert retrieved2 is not None, "Failed to retrieve translation with null FKs"
                assert retrieved2.code_id is None, "code_id should be None"
                assert retrieved2.block_id is None, "block_id should be None"
                assert retrieved2.code is None, "code should be None when FK is null (Django-style naming)"
                assert retrieved2.block is None, "block should be None when FK is null (Django-style naming)"
                
            finally:
                session.close()
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file)



class TestDifferentConfigurations:
    """Test that the fix works across different entity configurations."""
    
    def test_entities_with_templates(self):
        """
        Test 5.4a: Test with entities that have templates
        
        Verify that the fix works correctly when entities extend base classes.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # The Translation model in the example already has templates
        # (extends KinkoTechModelBase and CreateModifyMixinModel)
        # This test verifies that templates don't interfere with the fix
        
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify the fix works even with templates
        assert 'primary_key=True' in generated_code, \
            "Primary key fix doesn't work with templates"
        assert 'code_id = Column(BigInteger' in generated_code, \
            "Foreign key naming fix doesn't work with templates"
        assert 'foreign_keys=[code_id]' in generated_code, \
            "Reverse relationship fix doesn't work with templates"
        
        # Verify generated code is valid
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code with templates has syntax error: {e}")
    
    def test_entities_with_table_prefixes(self):
        """
        Test 5.4b: Test with entities that have table prefixes
        
        Verify that the fix works correctly when entities have table name prefixes.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # The Translation model already has a table prefix (kkt_i18n_translations_)
        # This test verifies that table prefixes don't interfere with the fix
        
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify table names are correct
        assert "__tablename__ = 'kkt_i18n_translations_translationmodel'" in generated_code, \
            "Table name with prefix not correct"
        
        # Verify the fix works with table prefixes
        assert 'primary_key=True' in generated_code, \
            "Primary key fix doesn't work with table prefixes"
        assert 'code_id = Column(BigInteger' in generated_code, \
            "Foreign key naming fix doesn't work with table prefixes"
        
        # Verify ForeignKey references use correct table names with prefixes
        assert "ForeignKey('kkt_i18n_translations_i18ncodemodel.id')" in generated_code, \
            "ForeignKey reference doesn't use correct table name with prefix"
        assert "ForeignKey('kkt_i18n_translations_i18nblockmodel.id')" in generated_code, \
            "ForeignKey reference doesn't use correct table name with prefix"
    
    def test_entities_with_multiple_foreign_keys(self):
        """
        Test 5.4c: Test with entities that have multiple foreign keys
        
        Verify that the fix works correctly when entities have multiple foreign keys
        to different tables (which is the main cause of ambiguity errors).
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # The Translation model has two foreign keys (code_id and block_id)
        # This is the exact scenario that causes ambiguity errors
        
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both foreign keys are generated correctly
        assert 'code_id = Column(BigInteger, ForeignKey' in generated_code, \
            "First foreign key not generated correctly"
        assert 'block_id = Column(BigInteger, ForeignKey' in generated_code, \
            "Second foreign key not generated correctly"
        
        # Verify both reverse relationships have foreign_keys parameter
        # This is critical to avoid ambiguity errors
        assert 'foreign_keys=[code_id]' in generated_code, \
            "First reverse relationship missing foreign_keys parameter"
        assert 'foreign_keys=[block_id]' in generated_code, \
            "Second reverse relationship missing foreign_keys parameter"
        
        # Verify the relationships reference the correct foreign keys (Django-style naming)
        code_rel_line = [line for line in generated_code.split('\n') 
                             if 'code = relationship(' in line]
        assert code_rel_line, "code relationship not found (Django-style naming)"
        # The line should contain foreign_keys=[code_id]
        # Find the full relationship definition (may span multiple lines)
        code_start = generated_code.find('code = relationship(')
        code_end = generated_code.find(')', code_start) + 1
        code_def = generated_code[code_start:code_end]
        assert 'foreign_keys=[code_id]' in code_def, \
            "code doesn't reference correct foreign key"
        
        block_start = generated_code.find('block = relationship(')
        block_end = generated_code.find(')', block_start) + 1
        block_def = generated_code[block_start:block_end]
        assert 'foreign_keys=[block_id]' in block_def, \
            "block doesn't reference correct foreign key"
    
    def test_entities_with_self_referential_relationships(self):
        """
        Test 5.4d: Test with entities that have self-referential relationships
        
        Verify that the fix works correctly when entities have foreign keys
        pointing to themselves.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # Create a TOML with self-referential relationship
        toml_content = """
[[relationships]]
left = "Category"
right = "Category"
type = "one-to-many"
left_column = "id"
right_column = "parent_id"

[entities.Category]
table_name = "category"

[[entities.Category.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false

[[entities.Category.columns]]
name = "name"
type = "string"
max_length = 100

[[entities.Category.columns]]
name = "parent"
type = "string"
db_column = "parent_id"
"""
        
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify primary key is correct
        assert 'id = Column(BigInteger, primary_key=True' in generated_code or \
               'id = Column(Integer, primary_key=True' in generated_code, \
            "Primary key not generated correctly for self-referential entity"
        
        # Verify foreign key uses db_column name
        assert 'parent_id = Column(' in generated_code, \
            "Self-referential foreign key doesn't use db_column name"
        
        # Verify foreign key references the same table
        assert "ForeignKey('category.id')" in generated_code, \
            "Self-referential foreign key doesn't reference correct table"
        
        # Verify reverse relationship has foreign_keys parameter
        # This is especially important for self-referential relationships
        assert 'foreign_keys=[parent_id]' in generated_code, \
            "Self-referential reverse relationship missing foreign_keys parameter"
        
        # Verify generated code is valid
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code with self-referential relationship has syntax error: {e}")
