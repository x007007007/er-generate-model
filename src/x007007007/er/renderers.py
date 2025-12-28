import logging
from jinja2 import Environment, PackageLoader, select_autoescape
from x007007007.er.base import Renderer
from x007007007.er.models import ERModel

logger = logging.getLogger(__name__)

class JinjaRenderer(Renderer):
    def __init__(self, template_name: str):
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        self.template = self.env.get_template(template_name)

    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(model=model)

class DjangoRenderer(JinjaRenderer):
    def __init__(self):
        super().__init__("django_model.j2")

class SQLAlchemyRenderer(JinjaRenderer):
    def __init__(self):
        super().__init__("sqlalchemy_model.j2")
