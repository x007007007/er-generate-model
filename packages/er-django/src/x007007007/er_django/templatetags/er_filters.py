"""
Django template filters for ER diagram rendering
"""
from django import template

register = template.Library()


@register.filter
def mermaid_relation(relation_type):
    """Convert relation type to Mermaid relation symbol"""
    mapping = {
        "one-to-one": "||--||",
        "one-to-many": "||--o{",
        "many-to-many": "}|--|{",
        "many-to-one": "}o--||"
    }
    return mapping.get(relation_type, "||--o{")


@register.filter
def plantuml_relation(relation_type):
    """Convert relation type to PlantUML relation symbol"""
    mapping = {
        "one-to-one": "||--||",
        "one-to-many": "||--o{",
        "many-to-many": "}|--|{",
        "many-to-one": "}o--||"
    }
    return mapping.get(relation_type, "||--o{")