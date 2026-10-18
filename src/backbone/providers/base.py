from abc import ABC, abstractmethod


class Provider(ABC):
    model: str

    @abstractmethod
    async def complete(self, messages: list[dict], **params) -> str:
        """Send chat messages to a model and return the reply text."""
