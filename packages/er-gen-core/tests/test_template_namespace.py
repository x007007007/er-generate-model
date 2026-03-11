"""
Tests for template namespace/package support.

This test verifies that templates with package attributes are generated
to the correct directories based on whether they're third-party or current project.
"""
import pytest
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers import SQLAlchemyRenderer


def test_third_party_template_generation():
    """
    Test that third-party templates (with 3+ part packages) are generated to third/ directory.
    """
    toml_content = """
[templates.ThirdPartyMixin]
package = "external.library.models.base"
export_path = "external.library.models.base"
[[templates.ThirdPartyMixin.columns]]
name = "created_at"
type = "datetime"
nullable = false

[[templates.ThirdPartyMixin.columns]]
name = "updated_at"
type = "datetime"
nullable = false

[entities.MyEntity]
extends = ["ThirdPartyMixin"]
table_name = "my_entity"
package = "myapp.models"
[[entities.MyEntity.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
    
    # Parse with reference mode
    parser = TomlERParser(inheritance_mode='reference')
    model = parser.parse(toml_content)
    
    # Generate with reference mode
    renderer = SQLAlchemyRenderer(inheritance_mode='reference')
    files = renderer.render_multi_file(model)
    
    # Verify third-party template is generated to third/ directory
    assert 'third/external/library/models/base.py' in files
    
    # Verify the generated file contains the mixin class
    mixin_file = files['third/external/library/models/base.py']
    assert 'class ThirdPartyMixin(Base):' in mixin_file
    assert '__abstract__ = True' in mixin_file
    assert 'created_at' in mixin_file
    assert 'updated_at' in mixin_file
    
    # Verify entity file imports from third/ directory
    entity_file = files['my_entity.py']
    assert 'from third.external.library.models.base import ThirdPartyMixin' in entity_file
    assert 'class MyEntity(ThirdPartyMixin):' in entity_file


def test_current_project_template_generation():
    """
    Test that current project templates (auto-generated with mixins. prefix) are generated to mixins/ directory.
    """
    toml_content = """
[templates.TimestampMixin]
# No package specified, parser will auto-generate export_path as mixins.timestampmixin
[[templates.TimestampMixin.columns]]
name = "created_at"
type = "datetime"
nullable = false

[entities.MyEntity]
extends = ["TimestampMixin"]
table_name = "my_entity"
package = "myapp.models"
[[entities.MyEntity.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
    
    # Parse with reference mode
    parser = TomlERParser(inheritance_mode='reference')
    model = parser.parse(toml_content)
    
    # Generate with reference mode
    renderer = SQLAlchemyRenderer(inheritance_mode='reference')
    files = renderer.render_multi_file(model)
    
    # Verify template is generated to mixins/ directory
    assert 'mixins/timestampmixin.py' in files
    
    # Verify the generated file contains the mixin class
    mixin_file = files['mixins/timestampmixin.py']
    assert 'class TimestampMixin(Base):' in mixin_file
    assert '__abstract__ = True' in mixin_file
    assert 'created_at' in mixin_file
    
    # Verify entity file imports from mixins/ directory
    entity_file = files['my_entity.py']
    assert 'from mixins.timestampmixin import TimestampMixin' in entity_file
    assert 'class MyEntity(TimestampMixin):' in entity_file


def test_external_class_without_columns_not_generated():
    """
    Test that templates without columns (external class markers) are not generated.
    """
    toml_content = """
[templates.ExternalBase]
package = "external.library.models.base"
export_path = "external.library.models.base"
# No columns - this is just a marker for an external class

[templates.MixinWithColumns]
package = "external.library.models.base"
export_path = "external.library.models.base"
[[templates.MixinWithColumns.columns]]
name = "field1"
type = "string"

[entities.MyEntity]
extends = ["ExternalBase", "MixinWithColumns"]
table_name = "my_entity"
package = "myapp.models"
[[entities.MyEntity.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
    
    # Parse with reference mode
    parser = TomlERParser(inheritance_mode='reference')
    model = parser.parse(toml_content)
    
    # Generate with reference mode
    renderer = SQLAlchemyRenderer(inheritance_mode='reference')
    files = renderer.render_multi_file(model)
    
    # Verify only MixinWithColumns is generated (ExternalBase has no columns)
    assert 'third/external/library/models/base.py' in files
    mixin_file = files['third/external/library/models/base.py']
    assert 'class MixinWithColumns(Base):' in mixin_file
    assert 'class ExternalBase' not in mixin_file
    
    # Verify entity imports both (ExternalBase from original, MixinWithColumns from third/)
    entity_file = files['my_entity.py']
    assert 'from external.library.models.base import ExternalBase' in entity_file
    assert 'from third.external.library.models.base import MixinWithColumns' in entity_file
    assert 'class MyEntity(ExternalBase, MixinWithColumns):' in entity_file


def test_multiple_templates_same_package():
    """
    Test that multiple templates in the same package are generated to the same file.
    """
    toml_content = """
[templates.Mixin1]
package = "external.library.models.base"
export_path = "external.library.models.base"
[[templates.Mixin1.columns]]
name = "field1"
type = "string"

[templates.Mixin2]
package = "external.library.models.base"
export_path = "external.library.models.base"
[[templates.Mixin2.columns]]
name = "field2"
type = "string"

[entities.MyEntity]
extends = ["Mixin1", "Mixin2"]
table_name = "my_entity"
package = "myapp.models"
[[entities.MyEntity.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
    
    # Parse with reference mode
    parser = TomlERParser(inheritance_mode='reference')
    model = parser.parse(toml_content)
    
    # Generate with reference mode
    renderer = SQLAlchemyRenderer(inheritance_mode='reference')
    files = renderer.render_multi_file(model)
    
    # Verify both mixins are in the same file
    assert 'third/external/library/models/base.py' in files
    mixin_file = files['third/external/library/models/base.py']
    assert 'class Mixin1(Base):' in mixin_file
    assert 'class Mixin2(Base):' in mixin_file
    assert 'field1' in mixin_file
    assert 'field2' in mixin_file
    
    # Verify entity imports both from the same module
    entity_file = files['my_entity.py']
    assert 'from third.external.library.models.base import Mixin1' in entity_file
    assert 'from third.external.library.models.base import Mixin2' in entity_file


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
