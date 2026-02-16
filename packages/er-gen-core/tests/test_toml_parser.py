"""
TOML ER图解析器测试。
"""
import pytest
import os
from x007007007.er.parser.toml_parser import TomlERParser


def get_asset_path(case_name: str, filename: str) -> str:
    """获取测试资产文件路径。"""
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return os.path.join(assets_dir, case_name, filename)


def test_toml_parser_basic():
    """测试基本的TOML解析功能。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_basic", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    assert len(model.entities) == 2
    assert "USER" in model.entities
    assert "POST" in model.entities
    assert len(model.entities["USER"].columns) == 2
    assert len(model.relationships) == 1


def test_toml_parser_with_template():
    """测试模板继承功能（数组格式）。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_with_template", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    assert len(model.entities) == 1
    user = model.entities["USER"]
    
    # 应该包含继承的字段和自己的字段
    column_names = [col.name for col in user.columns]
    assert "id" in column_names
    assert "created_at" in column_names
    assert "username" in column_names
    assert len(user.columns) == 3
    # 验证继承信息被保存
    assert user.extends == ["audit_fields"]


def test_toml_parser_multiple_templates():
    """测试多模板继承功能。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_multiple_templates", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    assert len(model.entities) == 1
    user = model.entities["USER"]
    
    # 应该包含所有模板的字段和自己的字段
    column_names = [col.name for col in user.columns]
    assert "created_at" in column_names
    assert "updated_at" in column_names
    assert "is_enabled" in column_names
    assert "name" in column_names
    assert "email" in column_names
    assert len(user.columns) == 5


def test_toml_parser_template_override_order():
    """测试模板覆盖顺序（后面的模板覆盖前面的）。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_template_override_order", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    user = model.entities["USER"]
    
    # template2的name应该覆盖template1的name
    name_col = next(col for col in user.columns if col.name == "name")
    assert name_col.comment == "Template 2 name"


def test_toml_parser_field_override():
    """测试字段覆盖功能。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_field_override", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    user = model.entities["USER"]
    
    # name字段应该被覆盖
    name_col = next(col for col in user.columns if col.name == "name")
    assert name_col.comment == "Overridden name"
    
    # 应该只有3个字段（id和覆盖后的name，加上email）
    assert len(user.columns) == 3


def test_toml_parser_complex():
    """测试复杂的TOML ER图（包含模板、继承、关系）。"""
    asset_path = get_asset_path("complex_toml", "input.toml")
    
    if not os.path.exists(asset_path):
        pytest.skip(f"Test asset not found: {asset_path}")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = TomlERParser()
    model = parser.parse(content)
    
    # 验证实体
    assert len(model.entities) >= 4
    assert "USER" in model.entities
    assert "POST" in model.entities
    assert "PROFILE" in model.entities
    assert "TAG" in model.entities
    
    # 验证USER实体继承了audit_fields模板
    user = model.entities["USER"]
    column_names = [col.name for col in user.columns]
    assert "id" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names
    assert "username" in column_names
    
    # 验证关系
    assert len(model.relationships) >= 3
    
    # 验证USER -> POST关系
    user_post_rel = next(
        (r for r in model.relationships if r.left_entity == "USER" and r.right_entity == "POST"),
        None
    )
    assert user_post_rel is not None
    assert user_post_rel.relation_type == "one-to-many"


def test_toml_parser_invalid_template():
    """测试引用不存在的模板时的行为。
    
    根据设计文档，如果模板不在templates中，说明是外部类（如AbstractUser），
    这种情况下不展开字段，但保留extends关系供代码生成器使用。
    """
    parser = TomlERParser()
    asset_path = get_asset_path("toml_invalid_template", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    # 不应该抛出错误，而是正常解析
    model = parser.parse(toml_content)
    assert "USER" in model.entities
    
    user = model.entities["USER"]
    # extends关系应该被保留
    assert user.extends == ["nonexistent_template"]
    # 但不会展开字段（因为模板不存在）
    assert len(user.columns) == 1  # 只有自己定义的id字段


def test_toml_parser_single_extends_not_allowed():
    """测试单个extends不再支持（必须是数组）。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_single_extends_not_allowed", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    with pytest.raises(ValueError, match="must be an array"):
        parser.parse(toml_content)


def test_toml_parser_export_path():
    """测试export_path功能。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_export_path", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    assert "create_update_time" in model.templates
    assert model.templates["create_update_time"]["export_path"] == "common.mixins"
    user = model.entities["USER"]
    assert user.extends == ["create_update_time"]


def test_toml_parser_invalid_toml():
    """测试无效的TOML格式。"""
    parser = TomlERParser()
    
    invalid_content = "[entities.USER\ncolumns = [\n"
    
    with pytest.raises(ValueError, match="Invalid TOML format"):
        parser.parse(invalid_content)


def test_toml_parser_relationship_types():
    """测试各种关系类型。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_relationship_types", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    assert len(model.relationships) == 2
    
    rel1 = model.relationships[0]
    assert rel1.relation_type == "one-to-many"
    
    rel2 = model.relationships[1]
    assert rel2.relation_type == "many-to-many"



def test_toml_parser_package_field():
    """测试package字段解析功能（Task 3.1）。"""
    parser = TomlERParser()
    
    toml_content = """
[entities.User]
table_name = "test_user"
package = "kinkotech.common.domains.account.models"
extends = []

[[entities.User.columns]]
name = "id"
type = "int"
is_pk = true

[[entities.User.columns]]
name = "username"
type = "str"
"""
    
    model = parser.parse(toml_content)
    assert "User" in model.entities
    
    user = model.entities["User"]
    assert user.package == "kinkotech.common.domains.account.models"
    assert user.name == "User"
    assert len(user.columns) == 2


def test_toml_parser_package_field_optional():
    """测试package字段为可选（向后兼容）。"""
    parser = TomlERParser()
    
    toml_content = """
[entities.Product]
table_name = "test_product"
extends = []

[[entities.Product.columns]]
name = "id"
type = "int"
is_pk = true
"""
    
    model = parser.parse(toml_content)
    assert "Product" in model.entities
    
    product = model.entities["Product"]
    assert product.package is None  # 未指定时应为None
    assert product.name == "Product"


def test_toml_parser_package_with_extends_and_export_path():
    """测试package字段与extends和export_path一起使用。"""
    parser = TomlERParser()
    
    toml_content = """
[templates.BaseModel]
export_path = "common.base"

[[templates.BaseModel.columns]]
name = "created_at"
type = "datetime"

[entities.Order]
table_name = "test_order"
extends = ["BaseModel"]
package = "myapp.orders.models"
export_path = "src/myapp/orders/models.toml"

[[entities.Order.columns]]
name = "id"
type = "int"
is_pk = true
"""
    
    model = parser.parse(toml_content)
    assert "Order" in model.entities
    
    order = model.entities["Order"]
    assert order.package == "myapp.orders.models"
    assert order.export_path == "src/myapp/orders/models.toml"
    assert order.extends == ["BaseModel"]
    assert len(order.columns) == 2  # created_at + id


def test_toml_parser_table_name_required():
    """测试table_name字段为必需（Task 9.1）。"""
    parser = TomlERParser()
    
    # TOML缺少table_name字段
    toml_content = """
[entities.Account]
package = "kinkotech.common.domains.account.models"
extends = []

[[entities.Account.columns]]
name = "id"
type = "int"
is_pk = true
"""
    
    # 应该抛出ValueError并包含清晰的错误信息
    with pytest.raises(ValueError) as exc_info:
        parser.parse(toml_content)
    
    error_message = str(exc_info.value)
    assert "Account" in error_message
    assert "table_name" in error_message
    assert "missing required field" in error_message
    assert "er_export" in error_message  # 应该提示如何重新生成


def test_toml_parser_table_name_present():
    """测试包含table_name字段的TOML可以正常解析（Task 9.1）。"""
    parser = TomlERParser()
    
    toml_content = """
[entities.Account]
table_name = "kinkotech_com_account_accountmodel"
package = "kinkotech.common.domains.account.models"
extends = []

[[entities.Account.columns]]
name = "id"
type = "int"
is_pk = true
"""
    
    model = parser.parse(toml_content)
    assert "Account" in model.entities
    
    account = model.entities["Account"]
    assert account.table_name == "kinkotech_com_account_accountmodel"
    assert account.package == "kinkotech.common.domains.account.models"


def test_toml_parser_export_path_ignored():
    """测试export_path字段被忽略（向后兼容，Task 9.1）。"""
    parser = TomlERParser()
    
    toml_content = """
[entities.User]
table_name = "myapp_user"
package = "myapp.models"
export_path = "/absolute/path/to/models.toml"
extends = []

[[entities.User.columns]]
name = "id"
type = "int"
is_pk = true
"""
    
    # 应该能够正常解析，export_path被保留但不影响功能
    model = parser.parse(toml_content)
    assert "User" in model.entities
    
    user = model.entities["User"]
    assert user.table_name == "myapp_user"
    assert user.export_path == "/absolute/path/to/models.toml"  # 保留但不使用
