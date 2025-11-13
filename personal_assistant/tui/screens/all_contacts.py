from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from personal_assistant.models import AddressBook


class AllContactsScreen(Screen):
    """
    Modal screen to display all contacts in a table.
    """

    BINDINGS = [
        (
            "escape",
            "app.pop_screen",
            "Close View",
        ),
    ]

    def __init__(self, book: AddressBook, **kwargs):
        super().__init__(**kwargs)
        self.book = book

    def compose(self) -> ComposeResult:
        yield Header(name="All Contacts")

        yield DataTable(id="all-contacts-table")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted. Populate the table."""
        table = self.query_one(DataTable)

        table.add_columns("№", "Name", "Phones", "Birthday")

        if not self.book.data:
            table.add_row("[italic]No contacts found.[/italic]")
            return

        for i, record in enumerate(self.book.data.values(), start=1):
            phones = (
                ", ".join(p.value for p in record.phones)
                or "[italic]No phones[/italic]"
            )
            birthday = (
                record.birthday.value.strftime("%d.%m.%Y")
                if record.birthday
                else "[italic]No birthday[/italic]"
            )

            table.add_row(str(i), record.name.value, phones, birthday)
