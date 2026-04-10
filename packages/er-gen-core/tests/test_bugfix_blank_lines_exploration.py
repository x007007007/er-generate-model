"""
Bug Condition Exploration Test for SQLAlchemy Excessive Blank Lines Fix

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

This test encodes the expected behavior - it will validate the fix when it passes after implementation.

GOAL: Surface counterexamples that demonstrate the bug exists.

Scoped PBT Approach: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility.
"""
import pytest
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestBugConditionExploration:
    """
    Bug Condition Exploration Test
    
    This test generates SQLAlchemy models from TOML specifications and verifies
    that the generated code has correct blank line spacing according to PEP 8.
    
    Expected Outcome: Test FAILS on unfixed code (this proves the bug exists)
    
    Counterexamples to document:
    - Import block: 7 blank lines between `from sqlalchemy.orm import relationship` and base model import (expected: 1)
    - External imports: 6 blank lines between last import and class definition (expected: 2)
    - Field definitions: 3 blank lines between consecutive fields (expected: 0)
    - Relationship definitions: 3 blank lines between consecutive relationships (expected: 0)
    - Field-to-relationship transition: 2 blank lines (expected: 1)
    """
    
    def test_sqlalchemy_template_blank_line_control(self):
        """
        Property 1: Fault Condition - SQLAlchemy 模板空行控制缺陷
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
        
        Generate SQLAlchemy models and verify blank line spacing:
        1. Import block: 1 blank line between relationship import and base model import (Req 1.1)
        2. External imports: 2 blank lines between last import and class definition (Req 1.2)
        3. Field definitions: 0 blank lines between consecutive fields (Req 1.3)
        4. Relationship definitions: 0 blank lines between consecutive relationships (Req 1.4)
        5. Field-to-relationship transition: 1 blank line (Req 1.5)
        """
        # Create a TOML specification with multiple fields and relationships
        toml_content = """
[entities.User]
table_name = "users"

[[entities.User.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.User.columns]]
name = "name"
type = "string"
max_length = 100
nullable = false

[[entities.User.columns]]
name = "email"
type = "string"
max_length = 255
nullable = false

[entities.Post]
table_name = "posts"

[[entities.Post.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.Post.columns]]
name = "title"
type = "string"
max_length = 200
nullable = false

[[entities.Post.columns]]
name = "content"
type = "text"
nullable = false

[[entities.Post.columns]]
name = "user_id"
type = "int"
nullable = false

[[relationships]]
left = "User"
right = "Post"
left_column = "id"
right_column = "user_id"
type = "1:N"
"""
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code using UNFIXED template (multi-file mode)
        renderer = SQLAlchemyRenderer(base_model_import='myapp.base')
        files = renderer.render_multi_file(model)
        
        # Get the Post entity file (which has fields and relationships)
        generated_code = files.get('post.py', '')
        
        # Split into lines for analysis
        lines = generated_code.split('\n')
        
        # Test 1: Import block spacing (Req 1.1)
        # Find the line with "from sqlalchemy.orm import relationship"
        relationship_import_idx = None
        base_import_idx = None
        
        for i, line in enumerate(lines):
            if 'from sqlalchemy.orm import relationship' in line:
                relationship_import_idx = i
            if 'from myapp.base import Base' in line:
                base_import_idx = i
        
        if relationship_import_idx is not None and base_import_idx is not None:
            blank_lines_between = base_import_idx - relationship_import_idx - 1
            assert blank_lines_between == 1, \
                f"COUNTEREXAMPLE (Req 1.1): Import block has {blank_lines_between} blank lines " \
                f"between relationship import and base model import (expected: 1)"
        
        # Test 2: Import to class definition spacing (Req 1.2)
        # Find the last import line and the class definition line
        last_import_idx = None
        class_def_idx = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                last_import_idx = i
            if line.strip().startswith('class Post('):
                class_def_idx = i
                break
        
        if last_import_idx is not None and class_def_idx is not None:
            blank_lines_between = class_def_idx - last_import_idx - 1
            assert blank_lines_between == 2, \
                f"COUNTEREXAMPLE (Req 1.2): Found {blank_lines_between} blank lines " \
                f"between last import and class definition (expected: 2)\n" \
                f"Last import (line {last_import_idx+1}): {lines[last_import_idx]}\n" \
                f"Class definition (line {class_def_idx+1}): {lines[class_def_idx]}"
        
        # Test 3: Field definitions spacing (Req 1.3)
        # Find consecutive field definitions and count blank lines
        # Look for patterns like "id = Column" followed by "name = Column"
        field_pattern_found = False
        for i in range(len(lines) - 1):
            if '= Column(' in lines[i] and not lines[i].strip().startswith('#'):
                # Found a field definition, check the next non-empty line
                j = i + 1
                blank_count = 0
                while j < len(lines) and lines[j].strip() == '':
                    blank_count += 1
                    j += 1
                
                if j < len(lines) and '= Column(' in lines[j] and not lines[j].strip().startswith('#'):
                    # Found consecutive field definitions
                    field_pattern_found = True
                    assert blank_count == 0, \
                        f"COUNTEREXAMPLE (Req 1.3): Found {blank_count} blank lines between field definitions " \
                        f"at lines {i+1} and {j+1} (expected: 0)\n" \
                        f"Field 1: {lines[i].strip()}\n" \
                        f"Field 2: {lines[j].strip()}"
        
        # Test 4: Relationship definitions spacing (Req 1.4)
        # Find consecutive relationship definitions
        relationship_pattern_found = False
        for i in range(len(lines) - 1):
            if '= relationship(' in lines[i]:
                # Found a relationship definition, check the next non-empty line
                j = i + 1
                blank_count = 0
                while j < len(lines) and lines[j].strip() == '':
                    blank_count += 1
                    j += 1
                
                if j < len(lines) and '= relationship(' in lines[j]:
                    # Found consecutive relationship definitions
                    relationship_pattern_found = True
                    assert blank_count == 0, \
                        f"COUNTEREXAMPLE (Req 1.4): Found {blank_count} blank lines between relationship definitions " \
                        f"at lines {i+1} and {j+1} (expected: 0)\n" \
                        f"Relationship 1: {lines[i].strip()}\n" \
                        f"Relationship 2: {lines[j].strip()}"
        
        # Test 5: Field-to-relationship transition spacing (Req 1.5)
        # Find where a field definition is followed by a relationship definition
        transition_found = False
        for i in range(len(lines) - 1):
            if '= Column(' in lines[i] and not lines[i].strip().startswith('#'):
                # Found a field definition, look for a relationship after it
                j = i + 1
                blank_count = 0
                while j < len(lines) and lines[j].strip() == '':
                    blank_count += 1
                    j += 1
                
                if j < len(lines) and '= relationship(' in lines[j]:
                    # Found field-to-relationship transition
                    transition_found = True
                    assert blank_count == 1, \
                        f"COUNTEREXAMPLE (Req 1.5): Found {blank_count} blank lines between field and relationship " \
                        f"at lines {i+1} and {j+1} (expected: 1)\n" \
                        f"Field: {lines[i].strip()}\n" \
                        f"Relationship: {lines[j].strip()}"
        
        # If we reach here, all assertions passed - the bug is fixed!
        # On unfixed code, at least one assertion will fail, documenting the counterexample
    
    def test_external_class_inheritance_blank_lines(self):
        """
        Test blank lines with external class inheritance (reference mode)
        
        **Validates: Requirement 1.2**
        
        This test verifies that there are exactly 2 blank lines between the last import
        and the class definition when using external class inheritance.
        """
        # Create a TOML specification with external class inheritance
        toml_content = """
[entities.MyModel]
table_name = "my_model"
extends = ["external.models.ExternalClass"]

[[entities.MyModel.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.MyModel.columns]]
name = "name"
type = "string"
max_length = 100
nullable = false
"""
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code in reference mode (which imports external classes)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(model)
        generated_code = files.get('my_model.py', '')
        
        # Split into lines for analysis
        lines = generated_code.split('\n')
        
        # Find the last import line and the class definition line
        last_import_idx = None
        class_def_idx = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                last_import_idx = i
            if line.strip().startswith('class MyModel('):
                class_def_idx = i
                break
        
        if last_import_idx is not None and class_def_idx is not None:
            blank_lines_between = class_def_idx - last_import_idx - 1
            assert blank_lines_between == 2, \
                f"COUNTEREXAMPLE (Req 1.2): Found {blank_lines_between} blank lines " \
                f"between last import and class definition (expected: 2)\n" \
                f"Last import (line {last_import_idx+1}): {lines[last_import_idx]}\n" \
                f"Class definition (line {class_def_idx+1}): {lines[class_def_idx]}"
