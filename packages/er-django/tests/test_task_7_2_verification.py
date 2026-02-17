"""
Verification test for Task 7.2: 修改 render() 方法输出 package 字段

This test demonstrates the complete functionality of the package field output
in the TOMLRenderer as specified in the design document.
"""
import toml
from x007007007.er.models import Entity, Column, ERModel
from x007007007.er_django.renderers import TOMLRenderer


def test_task_7_2_complete_example():
    """
    Complete example demonstrating Task 7.2 functionality.
    
    Requirements validated:
    - 7.1: TOML records model's complete package path
    - 10.3: TOMLRenderer outputs package field
    - 10.5: TOMLRenderer does not output package when None
    """
    # Create a model with package information
    user_entity = Entity(
        name="User",
            table_name="user",
        extends=["django.contrib.auth.models.AbstractUser"],
        package="kinkotech.common.domains.account.models",
        columns=[
            Column(name="phone",
            table_name="user", db_column="phone", type="CharField", max_length=20, nullable=True, unique=True),
            Column(name="avatar",
            table_name="user", db_column="avatar", type="ImageField", nullable=True)
        ]
    )
    
    # Create a model with different package
    profile_entity = Entity(
        name="Profile",
            table_name="profile",
        extends=["kinkotech.common.base.TimeStampedModel"],
        package="kinkotech.common.domains.account.models",
        columns=[
            Column(name="user",
            table_name="profile", db_column="user", type="OneToOneField", is_fk=True, nullable=False),
            Column(name="bio",
            table_name="profile", db_column="bio", type="TextField", nullable=True)
        ]
    )
    
    # Create a model without package (should not output package field)
    tag_entity = Entity(
        name="Tag",
            table_name="tag",
        package=None,  # None - should not be output
        columns=[
            Column(name="name",
            table_name="tag", db_column="name", type="CharField", max_length=50, unique=True)
        ]
    )
    
    # Create a model with empty string package (should not output package field)
    category_entity = Entity(
        name="Category",
            table_name="category",
        package="",  # Empty string - should not be output
        columns=[
            Column(name="title",
            table_name="category", db_column="title", type="CharField", max_length=100)
        ]
    )
    
    # Build ER model
    er_model = ERModel()
    er_model.add_entity(user_entity)
    er_model.add_entity(profile_entity)
    er_model.add_entity(tag_entity)
    er_model.add_entity(category_entity)
    
    # Render to TOML
    renderer = TOMLRenderer()
    toml_output = renderer.render(er_model)
    
    # Parse and verify
    data = toml.loads(toml_output)
    
    # Verify User entity with package
    assert "User" in data["entities"]
    assert "package" in data["entities"]["User"]
    assert data["entities"]["User"]["package"] == "kinkotech.common.domains.account.models"
    assert data["entities"]["User"]["extends"] == ["django.contrib.auth.models.AbstractUser"]
    
    # Verify Profile entity with package
    assert "Profile" in data["entities"]
    assert "package" in data["entities"]["Profile"]
    assert data["entities"]["Profile"]["package"] == "kinkotech.common.domains.account.models"
    
    # Verify Tag entity without package (package field should not be present)
    assert "Tag" in data["entities"]
    assert "package" not in data["entities"]["Tag"]
    
    # Verify Category entity with empty package (package field should not be present)
    assert "Category" in data["entities"]
    assert "package" not in data["entities"]["Category"]
    
    # Print the TOML output for manual verification
    print("\n" + "="*80)
    print("Generated TOML Output:")
    print("="*80)
    print(toml_output)
    print("="*80)
    
    # Verify the TOML structure matches the design document example
    expected_structure = """
[entities.User]
extends = ["django.contrib.auth.models.AbstractUser"]
package = "kinkotech.common.domains.account.models"

[[entities.User.columns]]
name = "phone"
type = "CharField"
max_length = 20
nullable = true
unique = true

[entities.Profile]
extends = ["kinkotech.common.base.TimeStampedModel"]
package = "kinkotech.common.domains.account.models"

[[entities.Profile.columns]]
name = "user"
type = "OneToOneField"
is_fk = true
nullable = false
"""
    
    # Verify key elements are present in the output
    assert 'package = "kinkotech.common.domains.account.models"' in toml_output
    assert toml_output.count('package = "kinkotech.common.domains.account.models"') == 2
    
    # Verify package appears after extends in the output
    user_section = toml_output[toml_output.find("[entities.User]"):toml_output.find("[entities.Profile]")]
    extends_pos = user_section.find("extends")
    package_pos = user_section.find("package")
    assert extends_pos < package_pos, "package should appear after extends"
    
    print("\n✅ Task 7.2 verification complete!")
    print("   - package field is output when present")
    print("   - package field is not output when None")
    print("   - package field is not output when empty string")
    print("   - TOML format is valid and parseable")
    print("   - package field appears after extends field")


def test_package_field_with_various_module_paths():
    """
    Test package field with various Python module path formats.
    """
    test_cases = [
        "myapp.models",
        "src.myapp.models",
        "kinkotech.common.domains.account.models",
        "django.contrib.auth.models",
        "a.b.c.d.e.f.models",
    ]
    
    for package_path in test_cases:
        entity = Entity(
            name="TestModel",
            table_name="test_model",
            package=package_path,
            columns=[Column(name="id",
            table_name="test_model", db_column="id", type="IntegerField", is_pk=True)]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        data = toml.loads(toml_output)
        
        assert "TestModel" in data["entities"]
        assert "package" in data["entities"]["TestModel"]
        assert data["entities"]["TestModel"]["package"] == package_path
        
        print(f"✓ Package path '{package_path}' correctly rendered")
    
    print("\n✅ All package path formats verified!")


if __name__ == "__main__":
    test_task_7_2_complete_example()
    print("\n" + "="*80 + "\n")
    test_package_field_with_various_module_paths()
