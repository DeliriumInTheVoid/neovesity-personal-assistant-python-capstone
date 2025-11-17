from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class SearchContactsByEmailPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "search-email"

    @property
    def description(self) -> str:
        return "Search contacts by email address"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide an email address to search for.[/bold red]")
            return

        email = " ".join(args)

        contacts = self.storage.search_by_email(email)

        if not contacts:
            app.log_widget.write(f"[bold yellow]No contacts found with email '{email}'[/bold yellow]")
            return

        app.log_widget.write(f"[bold green]Found {len(contacts)} contact(s) with email '{email}':[/bold green]\n")

        for contact in contacts:
            phones_str = ", ".join([p.value for p in contact.phones]) if contact.phones else "No phones"
            email_str = contact.email.value if contact.email else "No email"
            app.log_widget.write(f"[bold cyan]Name:[/bold cyan] {contact.first_name.value} {contact.last_name.value}")
            app.log_widget.write(f"[bold cyan]Email:[/bold cyan] {email_str}")
            app.log_widget.write(f"[bold cyan]Phones:[/bold cyan] {phones_str}")
            app.log_widget.write(f"[bold cyan]UUID:[/bold cyan] {contact.uuid}")
