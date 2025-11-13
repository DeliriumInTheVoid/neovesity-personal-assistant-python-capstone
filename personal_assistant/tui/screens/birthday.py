from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, DataTable, Footer

from personal_assistant.models import AddressBook


class BirthdaysScreen(Screen):
    """
    Modal screen to display upcoming birthdays.
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
        yield Header(name="🎂 Upcoming Birthdays")
        yield DataTable(id="birthdays-table")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted. Populate the table."""
        table = self.query_one(DataTable)

        table.add_columns("№", "Name", "Congratulation date")

        upcoming = self.book.get_upcoming_birthdays()

        if not upcoming:
            table.add_row("[italic]No upcoming birthdays found.[/italic]")
            return

        # for i, user in enumerate(upcoming, start=1):
        #     table.add_row(str(i), user["name"], user["congratulation_date"])
        for i, (record, date_) in enumerate(upcoming, start=1):
            table.add_row(str(i), record.name.value, str(date_))
