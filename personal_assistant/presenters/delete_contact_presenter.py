from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage
from personal_assistant.tui.screens.confirmation_screen import ConfirmationScreen

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class DeleteContactPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "delete-contact"

    @property
    def description(self) -> str:
        return "Deletes a contact by name or UUID"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        app.run_worker(self._handle_delete_contact(app, args))

    async def _handle_delete_contact(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a contact's first name, or UUID.[/bold red]")
            return

        search_term = " ".join(args)

        contacts = self.storage.search_by_first_name(args[0])

        if len(args) > 1:
            last_name = args[1]
            contacts = [c for c in contacts if c.last_name and c.last_name.value.lower() == last_name.lower()]

        if not contacts:
            contact = self.storage.get_record_by_id(search_term)
            contacts = [contact] if contact else []

        if not contacts:
            app.log_widget.write(f"[bold red]Contact '{search_term}' not found[/bold red]")
            return

        if len(contacts) > 1:
            app.log_widget.write(
                "[bold yellow]Multiple contacts found. Please be more specific by providing a last name or UUID.[/bold yellow]"
            )
            for contact in contacts:
                app.log_widget.write(
                    f"- {contact.first_name.value} {contact.last_name.value} (UUID: {contact.uuid})"
                )
            return

        contact_to_delete = contacts[0]

        confirmed = await app.push_screen_wait(
            ConfirmationScreen(
                f"Are you sure you want to delete {contact_to_delete.first_name.value} {contact_to_delete.last_name.value}?"
            )
        )

        if confirmed:
            if self.storage.delete_record(contact_to_delete.uuid):
                app.log_widget.write(
                    f"[bold green]✅ Contact '{contact_to_delete.first_name.value} {contact_to_delete.last_name.value}' deleted.[/bold green]"
                )
            else:
                app.log_widget.write(
                    f"[bold red]Failed to delete contact '{contact_to_delete.first_name.value} {contact_to_delete.last_name.value}'.[/bold red]"
                )
        else:
            app.log_widget.write("[bold yellow]Deletion cancelled.[/bold yellow]")

