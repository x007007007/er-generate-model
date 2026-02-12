"""SQLAlchemy model code renderer."""
from jinja2 import PackageLoader
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper
from x007007007.er.renderers.python.base import PythonRenderer


def sqlalchemy_column_type(col):
    """Jinja2 filter for SQLAlchemy column type."""
    column_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
    return column_type, params


class SQLAlchemyRenderer(PythonRenderer):
    """SQLAlchemy model code renderer."""
    
    def __init__(self, table_prefix: str = ''):
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment WITHOUT whitespace control for backward compatibility
        loader = PackageLoader("x007007007.er.renderers.python.sqlalchemy", "templates")
        from jinja2 import Environment, select_autoescape
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape()
        )
        
        # Register filters
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.env.filters['code_value'] = self.serialize_value
        
        self.template = self.env.get_template("sqlalchemy_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            table_prefix=self.table_prefix
        )
