from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ShowAllContactsPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "all"

    @property
    def description(self) -> str:
        return "Shows all contacts"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        from personal_assistant.tui.screens.all_contacts import AllContactsScreen

        contacts = self.storage.get_all_records()
        await app.push_screen(AllContactsScreen(contacts))
