from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ShowPhonePresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "phone"

    @property
    def description(self) -> str:
        return "Shows phone number(s) for a contact"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a contact name[/bold red]")
            return

        search_term = args[0]
        contacts = self.storage.search_by_first_name(search_term)

        if not contacts:
            contacts = self.storage.search_by_last_name(search_term)

        if not contacts:
            app.log_widget.write(f"[bold yellow]Contact '{search_term}' not found[/bold yellow]")
            return

        for contact in contacts:

            if not contact.phones:
                app.log_widget.write(f"[bold yellow]{contact.first_name.value} {contact.last_name.value if contact.last_name else ''} has no phone numbers[/bold yellow]")
                continue

            output = f"[bold green]Phone numbers for {contact.first_name.value} {contact.last_name.value if contact.last_name else ''}:[/bold green]\n"
            for phone in contact.phones:
                output += f"  {phone.value}\n"

            app.log_widget.write(output)
