from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, DataTable, Footer


class BirthdaysScreen(Screen):

    BINDINGS = [
        (
            "escape",
            "app.pop_screen",
            "Close View",
        ),
    ]

    def __init__(self, upcoming_birthdays: list[tuple[str, str, int]], **kwargs):
        """
        Args:
            upcoming_birthdays: List of tuples (name, birthday_str, days_until)
        """
        super().__init__(**kwargs)
        self.upcoming_birthdays = upcoming_birthdays

    def compose(self) -> ComposeResult:
        yield Header(name="🎂 Upcoming Birthdays")
        yield DataTable(id="birthdays-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        table.add_columns("№", "Name", "Birthday", "Days Until")

        if not self.upcoming_birthdays:
            table.add_row("[italic]No upcoming birthdays in the next 7 days.[/italic]")
            return

        for i, (name, birthday_str, days_until) in enumerate(self.upcoming_birthdays, start=1):
            day_str = "Today!" if days_until == 0 else f"{days_until} day(s)"
            table.add_row(str(i), name, birthday_str, day_str)
