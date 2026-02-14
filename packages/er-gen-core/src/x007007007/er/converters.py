"""
Converters for converting ERModel to Mermaid and PlantUML formats.
Uses Jinja2 templates for rendering, consistent with other renderers.
"""
from jinja2 import Environment, PackageLoader, select_autoescape
from x007007007.er.models import ERModel
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser


def get_mermaid_relation_symbol(relation_type: str) -> str:
    """Get Mermaid relation symbol from relation type."""
    mapping = {
        "one-to-one": "||--||",
        "one-to-many": "||--o{",
        "many-to-many": "}|--|{",
        "many-to-one": "}o--||"
    }
    return mapping.get(relation_type, "||--o{")


def get_plantuml_relation_symbol(relation_type: str) -> str:
    """Get PlantUML relation symbol from relation type."""
    mapping = {
        "one-to-one": "||--||",
        "one-to-many": "||--o{",
        "many-to-many": "}|--|{",
        "many-to-one": "}o--||"
    }
    return mapping.get(relation_type, "||--o{")


class MermaidConverter:
    """Converter to convert ERModel to Mermaid ER diagram format using Jinja2 template."""
    
    def __init__(self):
        # Use custom delimiters to avoid conflicts with Mermaid's {} syntax
        # Use [[ ]] for variables instead of {{ }}
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape(),
            variable_start_string='[[',
            variable_end_string=']]'
        )
        # Register custom filters
        self.env.filters['mermaid_relation_symbol'] = get_mermaid_relation_symbol
        self.template = self.env.get_template("mermaid_er.j2")
    
    def convert(self, model: ERModel) -> str:
        """Convert ERModel to Mermaid ER diagram format."""
        assert isinstance(model, ERModel), "model must be an ERModel instance"
        return self.template.render(model=model)


class PlantUMLConverter:
    """Converter to convert ERModel to PlantUML ER diagram format using Jinja2 template."""
    
    def __init__(self):
        # Use custom delimiters to avoid conflicts with PlantUML's {} syntax
        # Use [[ ]] for variables instead of {{ }}
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape(),
            variable_start_string='[[',
            variable_end_string=']]'
        )
        # Register custom filters
        self.env.filters['plantuml_relation_symbol'] = get_plantuml_relation_symbol
        self.template = self.env.get_template("plantuml_er.j2")
    
    def convert(self, model: ERModel) -> str:
        """Convert ERModel to PlantUML ER diagram format."""
        assert isinstance(model, ERModel), "model must be an ERModel instance"
        return self.template.render(model=model)

