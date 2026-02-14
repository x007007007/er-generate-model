"""Django models package."""
from .user_model import USER
from .post_model import POST

__all__ = [
    'USER',
    'POST',
]