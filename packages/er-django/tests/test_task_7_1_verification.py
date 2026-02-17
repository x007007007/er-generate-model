"""
Verification test for Task 7.1: 修改 render() 方法输出 extends 字段

This test demonstrates the complete functionality of the extends field output
in the TOMLRenderer as specified in the design document.
"""
import toml
from x007007007.er.models import Entity, Column, ERModel
from x007007007.er_django.renderers import TOMLRenderer


def test_task_7_1_complete_example():
    """
    Complete example demonstrating Task 7.1 functionality.
    
    Requirements validated:
    - 6.1: TOML format records inheritance relationship
    - 6.2: TOML contains extends = ["BaseModel"]
    - 6.3: TOML supports multiple inheritance
    - 10.1: TOMLRenderer outputs extends field
    - 10.4: TOMLRenderer does not output extends when empty
    """
    # Create a model with inheritance (like Django's AbstractUser)
    user_entity = Entity(
        name="User",
            table_name="user",
        extends=["django.contrib.auth.models.AbstractUser"],
        package="kinkotech.common.domains.account.models",
        columns=[
            Column(name="phone", db_column="phone", type="CharField", max_length=20, nullable=True, unique=True),
            Column(name="avatar", db_column="avatar", type="ImageField", nullable=True)
        ]
    )
    
    # Create a model with multiple inheritance
    profile_entity = Entity(
        name="Profile",
            table_name="profile",
        extends=[
            "kinkotech.common.base.TimeStampedModel",
            "kinkotech.common.base.SoftDeleteModel"
        ],
        package="kinkotech.common.domains.account.models",
        columns=[
            Column(name="user", db_column="user", type="OneToOneField", is_fk=True, nullable=False),
            Column(name="bio", db_column="bio", type="TextField", nullable=True)
        ]
    )
    
    # Create a simple model without inheritance
    tag_entity = Entity(
        name="Tag",
            table_name="tag",
        extends=[],  # Empty list - should not be output
        package="kinkotech.common.domains.blog.models",
        columns=[
            Column(name="name", db_column="name", type="CharField", max_length=50, unique=True)
        ]
    )
    
    # Build ER model
    er_model = ERModel()
    er_model.add_entity(user_entity)
    er_model.add_entity(profile_entity)
    er_model.add_entity(tag_entity)
    
    # Render to TOML
    renderer = TOMLRenderer()
    toml_output = renderer.render(er_model)
    
    # Parse and verify
    data = toml.loads(toml_output)
    
    # Verify User entity with single inheritance
    assert "User" in data["entities"]
    assert "extends" in data["entities"]["User"]
    assert data["entities"]["User"]["extends"] == ["django.contrib.auth.models.AbstractUser"]
    assert len(data["entities"]["User"]["columns"]) == 2
    
    # Verify Profile entity with multiple inheritance
    assert "Profile" in data["entities"]
    assert "extends" in data["entities"]["Profile"]
    assert len(data["entities"]["Profile"]["extends"]) == 2
    assert "kinkotech.common.base.TimeStampedModel" in data["entities"]["Profile"]["extends"]
    assert "kinkotech.common.base.SoftDeleteModel" in data["entities"]["Profile"]["extends"]
    assert len(data["entities"]["Profile"]["columns"]) == 2
    
    # Verify Tag entity without inheritance (extends field should not be present)
    assert "Tag" in data["entities"]
    assert "extends" not in data["entities"]["Tag"]
    assert len(data["entities"]["Tag"]["columns"]) == 1
    
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

[[entities.User.columns]]
name = "phone"
type = "CharField"
max_length = 20
nullable = true
unique = true

[[entities.User.columns]]
name = "avatar"
type = "ImageField"
nullable = true

[entities.Profile]
extends = ["kinkotech.common.base.TimeStampedModel", "kinkotech.common.base.SoftDeleteModel"]

[[entities.Profile.columns]]
name = "user"
type = "OneToOneField"
is_fk = true
nullable = false

[[entities.Profile.columns]]
name = "bio"
type = "TextField"
nullable = true

[entities.Tag]

[[entities.Tag.columns]]
name = "name"
type = "CharField"
max_length = 50
unique = true
"""
    
    # Verify key elements are present in the output
    assert "extends = [" in toml_output
    assert "django.contrib.auth.models.AbstractUser" in toml_output
    assert "kinkotech.common.base.TimeStampedModel" in toml_output
    assert "kinkotech.common.base.SoftDeleteModel" in toml_output
    
    print("\n✅ Task 7.1 verification complete!")
    print("   - extends field is output when present")
    print("   - Multiple inheritance is supported")
    print("   - extends field is not output when empty")
    print("   - TOML format is valid and parseable")


if __name__ == "__main__":
    test_task_7_1_complete_example()
