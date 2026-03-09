"""
Bug Condition Exploration Test for SQLAlchemy Generator Fixes

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

This test encodes the expected behavior - it will validate the fix when it passes after implementation.

GOAL: Surface counterexamples that demonstrate the bug exists.

Scoped PBT Approach: Test the concrete failing cases from the bug examples.
"""
import pytest
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


class TestBugConditionExploration:
    """
    Bug Condition Exploration Test
    
    This test generates SQLAlchemy models from the TOML specification and verifies
    that the generated code includes all required parameters and uses correct field names.
    
    Expected Outcome: Test FAILS on unfixed code (this proves the bug exists)
    
    Counterexamples to document:
    - Primary key columns missing `primary_key=True`
    - Foreign key columns using wrong field names (relationship name instead of db_column)
    - Foreign key columns using `Integer` instead of `BigInteger`
    - Nullable foreign keys missing `nullable=True`
    - Reverse relationships missing `foreign_keys` parameter
    """
    
    def test_sqlalchemy_generator_produces_correct_code(self):
        """
        Property 1: Fault Condition - SQLAlchemy Generator Produces Correct Code
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
        
        Generate SQLAlchemy models from examples/bug/django/models.toml and verify:
        1. Primary key columns include `primary_key=True` parameter (Req 1.1)
        2. Foreign key columns use `db_column` field name instead of relationship name (Req 1.2)
        3. Foreign key columns use correct type from TOML (e.g., `BigInteger` for `bigint`) (Req 1.3)
        4. Nullable foreign key columns include `nullable=True` parameter (Req 1.5)
        5. Reverse relationships include `foreign_keys` parameter (Req 1.4)
        """
        # Load the TOML file
        with open('examples/bug/django/models.toml', 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        # Parse the TOML
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code using UNFIXED template
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Verify the generated code contains the expected behavior
        # These assertions will FAIL on unfixed code, proving the bug exists
        
        # 1. Primary key columns should include `primary_key=True` (Req 1.1)
        # The Translation entity has an id column with primary_key=true in TOML
        assert 'id = Column(Integer, primary_key=True' in generated_code or \
               'id = Column(BigInteger, primary_key=True' in generated_code, \
               "COUNTEREXAMPLE: Primary key column 'id' is missing 'primary_key=True' parameter"
        
        # 2. Foreign key columns should use db_column field name (Req 1.2)
        # The Translation entity has a 'code' column with db_column='code_id'
        # It should generate 'code_id = Column(...)' not 'code = Column(...)'
        assert 'code_id = Column(' in generated_code, \
               "COUNTEREXAMPLE: Foreign key column uses relationship name 'code' instead of db_column 'code_id'"
        
        assert 'block_id = Column(' in generated_code, \
               "COUNTEREXAMPLE: Foreign key column uses relationship name 'block' instead of db_column 'block_id'"
        
        # 3. Foreign key columns should use correct type from TOML (Req 1.3)
        # The code_id and block_id columns should be BigInteger (since id columns are bigint)
        assert 'code_id = Column(BigInteger' in generated_code, \
               "COUNTEREXAMPLE: Foreign key column 'code_id' uses 'Integer' instead of 'BigInteger'"
        
        assert 'block_id = Column(BigInteger' in generated_code, \
               "COUNTEREXAMPLE: Foreign key column 'block_id' uses 'Integer' instead of 'BigInteger'"
        
        # 4. Nullable foreign key columns should include `nullable=True` (Req 1.5)
        # The code_id and block_id columns don't have nullable=false in TOML, so they should be nullable
        assert 'code_id = Column(BigInteger, ForeignKey' in generated_code and \
               'nullable=True' in generated_code.split('code_id = Column')[1].split('\n')[0], \
               "COUNTEREXAMPLE: Nullable foreign key column 'code_id' is missing 'nullable=True' parameter"
        
        # 5. Reverse relationships should include `foreign_keys` parameter (Req 1.4)
        # The Translation entity has reverse relationships to I18nCode and I18nBlock
        # These should include foreign_keys=[code_id] and foreign_keys=[block_id]
        assert 'foreign_keys=[code_id]' in generated_code, \
               "COUNTEREXAMPLE: Reverse relationship to I18nCode is missing 'foreign_keys=[code_id]' parameter"
        
        assert 'foreign_keys=[block_id]' in generated_code, \
               "COUNTEREXAMPLE: Reverse relationship to I18nBlock is missing 'foreign_keys=[block_id]' parameter"
        
        # If we reach here, all assertions passed - the bug is fixed!
        # On unfixed code, at least one assertion will fail, documenting the counterexample
