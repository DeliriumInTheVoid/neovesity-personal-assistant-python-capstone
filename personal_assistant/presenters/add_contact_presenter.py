from typing import TYPE_CHECKING
from personal_assistant.models.record import Record
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class AddContactPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "add-contact"

    @property
    def description(self) -> str:
        return "Adds a new contact"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        app.run_worker(self._handle_add_contact(app))

    async def _handle_add_contact(self, app: "AddressBookApp") -> None:
        from personal_assistant.tui.screens.add_contact import AddContactScreen

        result = await app.push_screen_wait(AddContactScreen())

        if result and result[0]:
            success, message, contact_data = result

            try:
                record = Record.from_dict(contact_data)
                self.storage.add_record(record)
                app.log_widget.write(f"[bold green]✅ {message}[/bold green]")
            except Exception as e:
                app.log_widget.write(f"[bold red]Failed to save contact: {e}[/bold red]")
        elif result:
            app.log_widget.write(f"[bold yellow]{result[1]}[/bold yellow]")
