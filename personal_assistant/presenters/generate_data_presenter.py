from typing import List, TYPE_CHECKING
import asyncio
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage
from personal_assistant.storage.notes_storage import NotesStorage
from personal_assistant.utils.random_address_book import (
    generate_contacts,
    generate_notes,
)

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class GenerateDataPresenter(Presenter):
    """
    Presenter for generating fake data.
    """

    def __init__(
        self,
        address_book_storage: AddressBookStorage,
        notes_storage: NotesStorage,
    ):
        self.address_book_storage = address_book_storage
        self.notes_storage = notes_storage
        super().__init__()

    @property
    def name(self) -> str:
        return "generate-data"

    @property
    def description(self) -> str:
        return "Generate fake data for testing. Usage: generate-data [num_contacts] [num_notes]"

    async def execute_tui(self, app: "AddressBookApp", args: List[str]) -> None:
        """
        Executes the command to generate fake data.
        """
        try:
            num_contacts = int(args[0]) if len(args) > 0 else 10
            num_notes = int(args[1]) if len(args) > 1 else 10
        except ValueError:
            app.log_widget.write(
                "[bold red]Invalid arguments. Please provide numbers for contacts and notes.[/bold red]"
            )
            return

        contact_uuids = []
        app.log_widget.write(f"Generating {num_contacts} contacts...")
        for record in generate_contacts(num_contacts):
            uuid = self.address_book_storage.add_record(record)
            contact_uuids.append(uuid)
            app.log_widget.write(f"  - Generated contact: {record.first_name.value} {record.last_name.value if record.last_name else ''}")
            await asyncio.sleep(0.1)
        app.log_widget.write(
            f"[bold green]✅ All {num_contacts} contacts generated.[/bold green]"
        )

        app.log_widget.write(f"\nGenerating {num_notes} notes...")
        for note in generate_notes(num_notes, contact_uuids):
            self.notes_storage.add_note(note)
            app.log_widget.write(f"  - Generated note: {note.title.value}")
            await asyncio.sleep(0.1)
        app.log_widget.write(
            f"[bold green]✅ All {num_notes} notes generated.[/bold green]"
        )
