import logging
from abc import ABC, abstractmethod
from x007007007.er.models import ERModel

logger = logging.getLogger(__name__)

class Parser(ABC):
    @abstractmethod
    def parse(self, content: str) -> ERModel:
        pass

class Renderer(ABC):
    @abstractmethod
    def render(self, model: ERModel) -> str:
        pass
