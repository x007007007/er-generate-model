import logging
from jinja2 import Environment, PackageLoader, select_autoescape
from x007007007.er.base import Renderer
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper

logger = logging.getLogger(__name__)


def django_field_type(col):
    """Jinja2 filter for Django field type."""
    field_type, params = TypeMapper.get_django_type(col.type, col.max_length)
    return field_type, params


def sqlalchemy_column_type(col):
    """Jinja2 filter for SQLAlchemy column type."""
    column_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
    return column_type, params


class JinjaRenderer(Renderer):
    def __init__(self, template_name: str, table_prefix: str = ''):
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        # Register custom filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.template = self.env.get_template(template_name)
        self.table_prefix = table_prefix

    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(model=model, table_prefix=self.table_prefix)

class DjangoRenderer(JinjaRenderer):
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        super().__init__("django_model.j2", table_prefix=table_prefix)
        self.app_label = app_label

    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(model=model, app_label=self.app_label, table_prefix=self.table_prefix)

class SQLAlchemyRenderer(JinjaRenderer):
    def __init__(self, table_prefix: str = ''):
        super().__init__("sqlalchemy_model.j2", table_prefix=table_prefix)
