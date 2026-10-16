from abc import ABC, abstractmethod


class BaseIncidentTool(ABC):
    name: str

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        raise NotImplementedError