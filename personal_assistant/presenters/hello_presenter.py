from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class HelloPresenter(Presenter):
    @property
    def name(self) -> str:
        return "hello"

    @property
    def description(self) -> str:
        return "Greets the user"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        app.log_widget.write("[bold green]How can I help you?[/bold green]")

