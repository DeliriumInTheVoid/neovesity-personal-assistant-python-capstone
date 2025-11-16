from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header
from personal_assistant.models.record import Record


class AllContactsScreen(Screen):

    BINDINGS = [
        (
            "escape",
            "app.pop_screen",
            "Close View",
        ),
    ]

    def __init__(self, contacts: list[Record], **kwargs):
        super().__init__(**kwargs)
        self.contacts = contacts

    def compose(self) -> ComposeResult:
        yield Header(name="All Contacts")

        yield DataTable(id="all-contacts-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        table.add_columns("№", "Name", "Phones", "Birthday", "Email", "Address")

        contacts = self.contacts

        if not contacts:
            table.add_row("[italic]No contacts found.[/italic]")
            return

        for i, record in enumerate(contacts, start=1):
            name = f"{record.first_name.value} {record.last_name.value if record.last_name else ''}".strip()

            phones = (
                ", ".join(p.value for p in record.phones)
                or "[italic]No phones[/italic]"
            )
            birthday = (
                record.birthday.value.strftime("%d.%m.%Y")
                if record.birthday
                else "[italic]No birthday[/italic]"
            )
            email = (
                record.email
                if record.email and record.email
                else "[italic]No email[/italic]"
            )

            address = (
                record.address
                if record.address and record.address
                else "[italic]No address[/italic]"
            )

            table.add_row(str(i), name, phones, birthday, email, address)
