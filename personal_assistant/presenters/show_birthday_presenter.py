from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ShowBirthdayPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "show-birthday"

    @property
    def description(self) -> str:
        return "Shows birthday for a contact"

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
            name = f"{contact.first_name.value} {contact.last_name.value if contact.last_name else ''}".strip()
            if contact.birthday:
                birthday_str = contact.birthday.value.strftime("%d.%m.%Y")
                app.log_widget.write(f"[bold green]Birthday for {name}:[/bold green] {birthday_str}")
            else:
                app.log_widget.write(f"[bold yellow]{name} has no birthday set[/bold yellow]")
