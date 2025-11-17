from typing import TYPE_CHECKING

from personal_assistant.models import Phone
from personal_assistant.models.exceptions import InvalidPhoneFormatError
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class SearchContactsByPhonePresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "search-phone"

    @property
    def description(self) -> str:
        return "Search contacts by phone number"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a phone number to search for.[/bold red]")
            return

        phone = args[0]

        try:
            phone_model = Phone(phone)
        except InvalidPhoneFormatError as e:
            app.log_widget.write(f"[bold red]Invalid phone number: {e}[/bold red]")
            return

        contacts = self.storage.search_by_phone(phone_model.value)

        if not contacts:
            app.log_widget.write(f"[bold yellow]No contacts found with phone number '{phone}'[/bold yellow]")
            return

        app.log_widget.write(f"[bold green]Found {len(contacts)} contact(s) with phone number '{phone}':[/bold green]\n")

        for contact in contacts:
            phones_str = ", ".join([p.value for p in contact.phones]) if contact.phones else "No phones"
            email_str = contact.email.value if contact.email else "No email"
            app.log_widget.write(f"[bold cyan]Name:[/bold cyan] {contact.first_name.value} {contact.last_name.value}")
            app.log_widget.write(f"[bold cyan]Phones:[/bold cyan] {phones_str}")
            app.log_widget.write(f"[bold cyan]Email:[/bold cyan] {email_str}")
            app.log_widget.write(f"[bold cyan]UUID:[/bold cyan] {contact.uuid}")
