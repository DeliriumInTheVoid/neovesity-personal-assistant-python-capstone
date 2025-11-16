from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class SearchContactsPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Searches for contacts"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a search term[/bold red]")
            return

        search_term = args[0]
        contacts = self.storage.search_by_first_name(search_term)

        if not contacts:
            contacts = self.storage.search_by_last_name(search_term)

        if not contacts:
            app.log_widget.write(f"[bold yellow]No contacts found for '{search_term}'[/bold yellow]")
            return

        output = f"[bold green]Found {len(contacts)} contact(s):[/bold green]\n"
        for contact in contacts:
            output += f"\n[bold cyan]{contact.first_name.value} {contact.last_name.value if contact.last_name else ''}[/bold cyan]\n"
            if contact.phones:
                output += f"Phones: {', '.join(phone.value for phone in contact.phones)}\n"
            # if contact.emails:
            #     output += f"Email: {', '.join(email.value for email in contact.emails)}\n"
            if contact.email:
                output += f"Email: {contact.email.value}\n"
            if contact.address:
                output += f"Address: {contact.address.value}\n"
            if contact.birthday:
                output += f"Birthday: {contact.birthday.value.strftime('%d.%m.%Y')}\n"

        app.log_widget.write(output)
