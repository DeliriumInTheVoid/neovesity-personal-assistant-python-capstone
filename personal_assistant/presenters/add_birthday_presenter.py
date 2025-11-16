from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage
from personal_assistant.models.field import Birthday

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class AddBirthdayPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "add-birthday"

    @property
    def description(self) -> str:
        return "Adds a birthday to a contact"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if len(args) < 2:
            app.log_widget.write("[bold red]Usage: add-birthday <name> <date (DD.MM.YYYY)>[/bold red]")
            return

        name = args[0]
        birthday_str = args[1]

        contacts = self.storage.search_by_first_name(name)

        if not contacts:
            contacts = self.storage.search_by_last_name(name)

        if not contacts:
            app.log_widget.write(f"[bold yellow]Contact '{name}' not found[/bold yellow]")
            return

        contact = contacts[0]

        try:
            # birthday = datetime.strptime(birthday_str, "%d.%m.%Y").date()
            # contact.birthday =  birthday.strftime("%Y-%m-%d")
            contact.birthday = Birthday(birthday_str)
            self.storage.update_record(contact)
            app.log_widget.write(f"[bold green]✅ Birthday added for {contact.first_name} {contact.last_name}[/bold green]")
        except ValueError:
            app.log_widget.write("[bold red]Invalid date format. Use DD.MM.YYYY[/bold red]")

