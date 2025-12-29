"""
测试TOML多继承的代码输出功能。
"""
import pytest
import os
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer


def get_asset_path(case_name: str, filename: str) -> str:
    """获取测试资产文件路径。"""
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return os.path.join(assets_dir, case_name, filename)


def test_django_output_multiple_inheritance():
    """测试Django输出多继承的引用。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_django_multiple_inheritance", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = DjangoRenderer(app_label="testapp")
    output = renderer.render(model)
    
    # 验证导入语句
    assert "from common.mixins import" in output
    assert "CreateupdatetimeMixin" in output
    assert "EnableMixin" in output
    assert "NameMixin" in output
    
    # 验证类继承
    assert "class USER(CreateupdatetimeMixin, EnableMixin, NameMixin):" in output
    
    # 验证只包含非继承字段
    assert "email" in output
    assert "created_at" not in output  # 继承的字段不应该在实体类中
    assert "updated_at" not in output
    assert "is_enabled" not in output
    assert "name" not in output
    
    # 验证Manager和QuerySet
    assert "class USERQuerySet" in output
    assert "class USERManager" in output
    assert "objects = USERManager()" in output


def test_django_output_single_inheritance():
    """测试Django输出单继承的引用。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_django_single_inheritance", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = DjangoRenderer(app_label="testapp")
    output = renderer.render(model)
    
    # 验证导入语句
    assert "from common.mixins import CreateupdatetimeMixin" in output
    
    # 验证类继承
    assert "class USER(CreateupdatetimeMixin):" in output
    
    # 验证Manager和QuerySet
    assert "class USERQuerySet" in output
    assert "class USERManager" in output


def test_django_output_no_inheritance():
    """测试Django输出无继承的情况。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_django_no_inheritance", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = DjangoRenderer(app_label="testapp")
    output = renderer.render(model)
    
    # 验证类继承models.Model
    assert "class USER(models.Model):" in output
    
    # 验证Manager和QuerySet
    assert "class USERQuerySet" in output
    assert "class USERManager" in output


def test_django_output_inheritance_without_export_path():
    """测试Django输出继承但没有export_path的情况（不导入）。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_django_inheritance_without_export_path", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = DjangoRenderer(app_label="testapp")
    output = renderer.render(model)
    
    # 验证不导入（因为没有export_path）
    assert "from" not in output or "common.mixins" not in output
    
    # 验证类继承models.Model（因为没有export_path的模板）
    assert "class USER(models.Model):" in output
    
    # 验证字段都在实体类中（因为没有export_path，字段会展开）
    assert "username" in output
    assert "created_at" in output  # 因为没有export_path，字段会展开到实体类中


def test_sqlalchemy_output_multiple_inheritance():
    """测试SQLAlchemy输出多继承的引用。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_sqlalchemy_multiple_inheritance", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = SQLAlchemyRenderer()
    output = renderer.render(model)
    
    # 验证导入语句
    assert "from common.mixins import" in output
    assert "CreateupdatetimeMixin" in output
    assert "EnableMixin" in output
    
    # 验证类继承
    assert "class USER(CreateupdatetimeMixin, EnableMixin):" in output
    
    # 验证只包含非继承字段
    assert "email" in output
    assert "created_at" not in output  # 继承的字段不应该在实体类中
    assert "updated_at" not in output
    assert "is_enabled" not in output


def test_sqlalchemy_output_no_inheritance():
    """测试SQLAlchemy输出无继承的情况。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_sqlalchemy_no_inheritance", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = SQLAlchemyRenderer()
    output = renderer.render(model)
    
    # 验证类继承Base
    assert "class USER(Base):" in output


def test_multiple_entities_with_different_inheritance():
    """测试多个实体使用不同继承的情况。"""
    parser = TomlERParser()
    asset_path = get_asset_path("toml_multiple_entities_different_inheritance", "input.toml")
    
    with open(asset_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()
    
    model = parser.parse(toml_content)
    renderer = DjangoRenderer(app_label="testapp")
    output = renderer.render(model)
    
    # 验证USER继承两个Mixin
    assert "class USER(CreateupdatetimeMixin, EnableMixin):" in output
    
    # 验证POST继承一个Mixin
    assert "class POST(CreateupdatetimeMixin):" in output
    
    # 验证TAG不继承
    assert "class TAG(models.Model):" in output
    
    # 验证所有实体都有Manager和QuerySet
    assert "class USERQuerySet" in output
    assert "class USERManager" in output
    assert "class POSTQuerySet" in output
    assert "class POSTManager" in output
    assert "class TAGQuerySet" in output
    assert "class TAGManager" in output

