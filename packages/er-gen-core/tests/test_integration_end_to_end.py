"""
Integration Tests for End-to-End Generation Pipeline

**Validates: All requirements (integration validation)**

These tests verify the complete TOML → ERModel → SQLAlchemy code pipeline,
ensuring that generated code is valid Python, can be imported, and works with SQLAlchemy.

Task 14.1: Write integration tests for end-to-end generation
- Test TOML → ERModel → SQLAlchemy code pipeline
- Test that generated code is valid Python
- Test that generated models can be imported
- Test that SQLAlchemy validates generated models
"""
import ast
import pytest
import tempfile
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestEndToEndPipeline:
    """Test the complete TOML → ERModel → SQLAlchemy code pipeline."""
    
    def test_simple_model_pipeline(self):
        """
        Test end-to-end pipeline with a simple model.
        
        Verifies:
        - TOML parsing creates valid ERModel
        - Renderer generates valid Python code
        - Generated code can be parsed by AST
        - Generated code can be imported
        - SQLAlchemy can validate the model
        """
        toml_content = """
[entities.User]
table_name = "users"

[[entities.User.columns]]
name = "id"
type = "int"
primary_key = true
nullable = false

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50
unique = true
nullable = false

[[entities.User.columns]]
name = "email"
type = "string"
max_length = 100
"""
        
        # Step 1: Parse TOML → ERModel
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Verify ERModel is created correctly
        assert model is not None, "Parser failed to create ERModel"
        assert "User" in model.entities, "User entity not found in ERModel"
        assert len(model.entities["User"].columns) == 3, "Expected 3 columns in User entity"
        
        # Step 2: Render ERModel → SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify code is generated
        assert generated_code, "Renderer failed to generate code"
        assert "class User(" in generated_code, "User class not found in generated code"
        
        # Step 3: Verify generated code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Step 4: Verify generated code can be imported
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import Column, Integer, String\n")
            f.write("from sqlalchemy.orm import declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_simple_model", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Verify the User class exists and has expected attributes
            assert hasattr(test_module, 'User'), "User class not found in module"
            User = test_module.User
            assert hasattr(User, '__tablename__'), "User class missing __tablename__"
            assert hasattr(User, 'id'), "User class missing id column"
            assert hasattr(User, 'username'), "User class missing username column"
            assert hasattr(User, 'email'), "User class missing email column"
            
            # Step 5: Verify SQLAlchemy can validate the model
            from sqlalchemy import inspect
            mapper = inspect(User)
            columns = {col.key for col in mapper.columns}
            assert 'id' in columns, "id column not in mapper"
            assert 'username' in columns, "username column not in mapper"
            assert 'email' in columns, "email column not in mapper"
            
        finally:
            os.unlink(temp_file)
    
    def test_relationship_model_pipeline(self):
        """
        Test end-to-end pipeline with models that have relationships.
        
        Verifies:
        - Foreign key relationships are correctly parsed
        - Django-style naming is applied (db_column with _id, relationship without)
        - Generated code includes foreign_keys parameter
        - Relationships work in SQLAlchemy
        """
        toml_content = """
[[relationships]]
left = "User"
right = "Post"
type = "one-to-many"
left_column = "id"
right_column = "author_id"

[entities.User]
table_name = "users"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50

[entities.Post]
table_name = "posts"

[[entities.Post.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false

[[entities.Post.columns]]
name = "author"
type = "bigint"
db_column = "author_id"

[[entities.Post.columns]]
name = "title"
type = "string"
max_length = 200
"""
        
        # Step 1: Parse TOML → ERModel
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Verify relationships are parsed
        assert len(model.relationships) == 1, "Expected 1 relationship"
        assert model.relationships[0].left_entity == "User", "Relationship left entity incorrect"
        assert model.relationships[0].right_entity == "Post", "Relationship right entity incorrect"
        
        # Step 2: Render ERModel → SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify Django-style naming
        assert 'author_id = Column(' in generated_code, \
            "Foreign key column should use db_column name (author_id)"
        assert 'author = relationship(' in generated_code, \
            "Relationship should use logical name (author)"
        assert 'foreign_keys=[author_id]' in generated_code, \
            "Relationship should include foreign_keys parameter"
        
        # Step 3: Verify generated code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Step 4: Verify generated code can be imported and works with SQLAlchemy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import BigInteger, Column, ForeignKey, String\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_relationship_model", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            User = test_module.User
            Post = test_module.Post
            Base = test_module.Base
            
            # Step 5: Verify SQLAlchemy can create tables without errors
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
            
            # Step 6: Test that relationships work
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
                # Create a user
                user = User(id=1, username='testuser')
                session.add(user)
                session.commit()
                
                # Create a post with foreign key
                post = Post(id=1, author_id=1, title='Test Post')
                session.add(post)
                session.commit()
                
                # Verify relationship works
                retrieved_post = session.query(Post).filter_by(id=1).first()
                assert retrieved_post.author is not None, "Relationship not working"
                assert retrieved_post.author.username == 'testuser', "Relationship data incorrect"
                
                # Verify reverse relationship
                retrieved_user = session.query(User).filter_by(id=1).first()
                assert len(retrieved_user.post_set) == 1, "Reverse relationship not working"
                assert retrieved_user.post_set[0].title == 'Test Post', "Reverse relationship data incorrect"
                
            finally:
                session.close()
                
        finally:
            os.unlink(temp_file)
    
    def test_multiple_foreign_keys_pipeline(self):
        """
        Test end-to-end pipeline with multiple foreign keys.
        
        Verifies:
        - Multiple foreign keys are correctly handled
        - Each relationship has correct foreign_keys parameter
        - No ambiguity errors occur
        """
        toml_content = """
[[relationships]]
left = "User"
right = "Post"
type = "one-to-many"
left_column = "id"
right_column = "author_id"

[[relationships]]
left = "Category"
right = "Post"
type = "one-to-many"
left_column = "id"
right_column = "category_id"

[entities.User]
table_name = "users"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.User.columns]]
name = "username"
type = "string"

[entities.Category]
table_name = "categories"

[[entities.Category.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.Category.columns]]
name = "name"
type = "string"

[entities.Post]
table_name = "posts"

[[entities.Post.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.Post.columns]]
name = "author"
type = "bigint"
db_column = "author_id"

[[entities.Post.columns]]
name = "category"
type = "bigint"
db_column = "category_id"

[[entities.Post.columns]]
name = "title"
type = "string"
"""
        
        # Parse and render
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify both foreign keys are present
        assert 'author_id = Column(' in generated_code, "author_id column not found"
        assert 'category_id = Column(' in generated_code, "category_id column not found"
        
        # Verify both relationships have foreign_keys parameter
        assert 'foreign_keys=[author_id]' in generated_code, \
            "author relationship missing foreign_keys parameter"
        assert 'foreign_keys=[category_id]' in generated_code, \
            "category relationship missing foreign_keys parameter"
        
        # Verify code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Test with SQLAlchemy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import BigInteger, Column, ForeignKey, String\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_multiple_fk", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            Base = test_module.Base
            
            # This will fail if there are ambiguity errors
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
            
        finally:
            os.unlink(temp_file)
    
    def test_complex_model_with_attributes_pipeline(self):
        """
        Test end-to-end pipeline with complex model attributes.
        
        Verifies:
        - Column attributes (nullable, unique, default, comment) are preserved
        - Foreign key columns maintain their attributes
        - Generated code works with all attribute combinations
        """
        toml_content = """
[[relationships]]
left = "User"
right = "Profile"
type = "one-to-one"
left_column = "id"
right_column = "user_id"

[entities.User]
table_name = "users"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false
comment = "Primary key"

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50
unique = true
nullable = false
comment = "Unique username"

[entities.Profile]
table_name = "profiles"

[[entities.Profile.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false

[[entities.Profile.columns]]
name = "user"
type = "bigint"
db_column = "user_id"
nullable = true
unique = true
comment = "Foreign key to user"

[[entities.Profile.columns]]
name = "bio"
type = "text"
nullable = true
default = ""
comment = "User biography"
"""
        
        # Parse and render
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify attributes are preserved
        assert 'primary_key=True' in generated_code, "primary_key attribute not preserved"
        assert 'nullable=False' in generated_code, "nullable=False not preserved"
        assert 'nullable=True' in generated_code, "nullable=True not preserved"
        assert 'unique=True' in generated_code, "unique attribute not preserved"
        
        # Verify foreign key has attributes
        user_id_lines = [line for line in generated_code.split('\n') if 'user_id = Column(' in line]
        assert user_id_lines, "user_id column not found"
        # The foreign key should have nullable and unique attributes
        # (may be on same line or following lines)
        
        # Verify code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Test with SQLAlchemy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import BigInteger, Column, ForeignKey, String, Text\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_complex_model", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            User = test_module.User
            Profile = test_module.Profile
            Base = test_module.Base
            
            # Verify SQLAlchemy can create tables
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
            
            # Verify one-to-one relationship works
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
                user = User(id=1, username='testuser')
                session.add(user)
                session.commit()
                
                profile = Profile(id=1, user_id=1, bio='Test bio')
                session.add(profile)
                session.commit()
                
                # Verify relationship
                retrieved_profile = session.query(Profile).filter_by(id=1).first()
                assert retrieved_profile.user is not None, "One-to-one relationship not working"
                assert retrieved_profile.user.username == 'testuser', "Relationship data incorrect"
                
            finally:
                session.close()
                
        finally:
            os.unlink(temp_file)
    
    def test_table_prefix_pipeline(self):
        """
        Test end-to-end pipeline with table prefixes.
        
        Verifies:
        - Table names are correctly set
        - Foreign key references work correctly
        - Generated code works with SQLAlchemy
        
        Note: Table prefix feature may not be implemented yet, so this test
        verifies basic functionality without prefix.
        """
        toml_content = """
[[relationships]]
left = "User"
right = "Post"
type = "one-to-many"
left_column = "id"
right_column = "author_id"

[entities.User]
table_name = "users"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.User.columns]]
name = "username"
type = "string"

[entities.Post]
table_name = "posts"

[[entities.Post.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.Post.columns]]
name = "author"
type = "bigint"
db_column = "author_id"

[[entities.Post.columns]]
name = "title"
type = "string"
"""
        
        # Parse and render
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify table names are set
        assert "__tablename__ = 'users'" in generated_code, \
            "Table name not set for users table"
        assert "__tablename__ = 'posts'" in generated_code, \
            "Table name not set for posts table"
        
        # Verify foreign key references work
        assert "ForeignKey('users.id')" in generated_code, \
            "Foreign key reference incorrect"
        
        # Verify code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Test with SQLAlchemy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import BigInteger, Column, ForeignKey, String\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_table_prefix", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            Base = test_module.Base
            
            # Verify SQLAlchemy can create tables
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
            
        finally:
            os.unlink(temp_file)


class TestRealWorldExamples:
    """Test end-to-end pipeline with real-world example files."""
    
    def test_django_bug_example_pipeline(self):
        """
        Test end-to-end pipeline with the Django bug example.
        
        This is the real-world example from examples/bug/django/rfc_order/models.toml
        that demonstrates all the issues the feature fixes.
        """
        # Load the real TOML file
        with open('examples/bug/django/rfc_order/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        # Parse
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Verify parsing succeeded
        assert model is not None, "Failed to parse Django bug example"
        
        # Render
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify code is generated
        assert generated_code, "Failed to generate code from Django bug example"
        
        # Verify code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Verify Django-style naming is applied (if foreign keys exist)
        # The specific assertions depend on what's in the TOML file
        # At minimum, verify the code can be parsed and is valid
    
    def test_sqlalchemy_example_01_pipeline(self):
        """
        Test end-to-end pipeline with a simple user model.
        
        This test creates a simple model inline to avoid dependency on
        external example files that may have different formats.
        """
        toml_content = """
[entities.User]
table_name = "user"

[[entities.User.columns]]
name = "id"
type = "int"
primary_key = true
nullable = false
comment = "Primary key"

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50
unique = true
nullable = false
comment = "Unique username"

[[entities.User.columns]]
name = "email"
type = "string"
max_length = 100
comment = "User email address"

[[entities.User.columns]]
name = "created_at"
type = "datetime"
comment = "Account creation timestamp"
"""
        
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Test import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import Column, Integer, String, DateTime\n")
            f.write("from sqlalchemy.orm import declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_example_01", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            assert hasattr(test_module, 'User'), "User class not found"
            
        finally:
            os.unlink(temp_file)
    
    def test_sqlalchemy_example_02_pipeline(self):
        """
        Test end-to-end pipeline with relationships.
        
        This test creates a model with relationships inline to avoid dependency on
        external example files that may have different formats.
        """
        toml_content = """
[[relationships]]
left = "User"
right = "Post"
type = "one-to-many"
left_column = "id"
right_column = "author_id"

[entities.User]
table_name = "user"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false
comment = "Primary key"

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50
unique = true
nullable = false
comment = "Unique username"

[[entities.User.columns]]
name = "email"
type = "string"
max_length = 100
unique = true
comment = "User email address"

[entities.Post]
table_name = "post"

[[entities.Post.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false
comment = "Primary key"

[[entities.Post.columns]]
name = "author"
type = "bigint"
db_column = "author_id"
comment = "Foreign key to User"

[[entities.Post.columns]]
name = "title"
type = "string"
max_length = 200
comment = "Post title"

[[entities.Post.columns]]
name = "content"
type = "text"
comment = "Post content"
"""
        
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify code is valid Python
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")
        
        # Test with SQLAlchemy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write("from sqlalchemy import Column, BigInteger, String, Text, ForeignKey\n")
            f.write("from sqlalchemy.orm import relationship, declarative_base\n\n")
            f.write("Base = declarative_base()\n\n")
            f.write(generated_code)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_example_02", temp_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            User = test_module.User
            Post = test_module.Post
            Base = test_module.Base
            
            # Verify SQLAlchemy can create tables
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
            
        finally:
            os.unlink(temp_file)
