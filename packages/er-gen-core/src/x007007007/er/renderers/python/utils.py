"""Utility functions for Python code renderers."""
import re


def to_snake_case(name: str) -> str:
    """
    Convert CamelCase or PascalCase to snake_case.
    
    Handles:
    - Simple CamelCase: User -> user
    - Multi-word: UserProfile -> user_profile
    - Complex: ConversationSessionModel -> conversation_session_model
    - Acronyms: HTTPRequest -> http_request, XMLParser -> xml_parser
    - Numbers: User2 -> user2, Model3D -> model3_d
    - Already snake_case: user_profile -> user_profile
    - Single letter: A -> a
    
    Args:
        name: The name to convert (CamelCase, PascalCase, or snake_case)
    
    Returns:
        The name in snake_case format
    
    Examples:
        >>> to_snake_case("User")
        'user'
        >>> to_snake_case("UserAccount")
        'user_account'
        >>> to_snake_case("HTTPRequest")
        'http_request'
        >>> to_snake_case("Model3D")
        'model3_d'
    """
    # Insert underscore before uppercase letters (except at start)
    # This handles: UserProfile -> User_Profile
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    
    # Insert underscore before uppercase letters preceded by lowercase or digit
    # This handles: HTTPRequest -> HTTP_Request, Model3D -> Model3_D
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    # Convert to lowercase
    return s2.lower()
