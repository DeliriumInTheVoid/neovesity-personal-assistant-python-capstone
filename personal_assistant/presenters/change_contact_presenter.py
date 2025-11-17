from typing import TYPE_CHECKING
from personal_assistant.models.record import Record
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ChangeContactPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "change-contact"

    @property
    def description(self) -> str:
        return "Changes a contact's information"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide contact name or UUID[/bold red]")
            return

        search_term = args[0]
        contacts = self.storage.search_by_first_name(search_term)

        if not contacts:
            contacts = self.storage.search_by_last_name(search_term)

        if not contacts:
            contact = self.storage.get_record_by_id(search_term)
            contacts = [contact] if contact else []

        if not contacts:
            app.log_widget.write(f"[bold red]Contact '{search_term}' not found[/bold red]")
            return

        if len(contacts) > 1:
            app.log_widget.write(
                "[bold yellow]Multiple contacts found. Please be more specific.[/bold yellow]"
            )
            for contact in contacts:
                app.log_widget.write(
                    f"- {contact.first_name.value} {contact.last_name.value} (UUID: {contact.uuid})"
                )
            return

        existing_contact = contacts[0]

        app.run_worker(self._handle_change_contact(app, existing_contact))

    async def _handle_change_contact(self, app: "AddressBookApp", existing_contact: Record) -> None:
        from personal_assistant.tui.screens.add_contact import AddContactScreen

        result = await app.push_screen_wait(AddContactScreen(existing_contact=existing_contact))

        if result and result[0]:
            success, message, contact_data = result

            try:
                record = Record.from_dict(contact_data)
                if existing_contact:
                    record.uuid = existing_contact.uuid  # preserve the original ID
                self.storage.update_record(record)
                app.log_widget.write(f"[bold green]✅ {message}[/bold green]")
            except Exception as e:
                app.log_widget.write(f"[bold red]Failed to update contact: {e}[/bold red]")
        elif result:
            app.log_widget.write(f"[bold yellow]{result[1]}[/bold yellow]")
