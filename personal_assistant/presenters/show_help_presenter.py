from typing import TYPE_CHECKING, Dict
from personal_assistant.presenters.presenter import Presenter

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ShowHelpPresenter(Presenter):
    def __init__(self, commands: Dict[str, Presenter]):
        self.commands = commands

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Shows available commands"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        output = "[bold green]Available commands:[/bold green]\n\n"

        for cmd_name, presenter in sorted(self.commands.items()):
            if cmd_name != "exit":
                output += f"[bold cyan]{cmd_name:20}[/bold cyan] - {presenter.description}\n"

        output += f"[bold cyan]{'exit':20}[/bold cyan] - Exit the application\n"

        app.log_widget.write(output)

