from typing import TYPE_CHECKING, Dict
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.tui.screens.help.help import HelpScreen

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
        await app.push_screen(HelpScreen())
