from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class Presenter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        pass
