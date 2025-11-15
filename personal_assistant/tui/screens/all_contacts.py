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

        table.add_columns("№", "Name", "Phones", "Birthday", "Email")

        contacts = self.contacts

        if not contacts:
            table.add_row("[italic]No contacts found.[/italic]")
            return

        for i, contact in enumerate(contacts, start=1):
            name = f"{contact.first_name.value} {contact.last_name.value if contact.last_name else ''}".strip()
            phones = ", ".join(str(phone) for phone in contact.phones) or "[italic]No phones[/italic]"

            birthday = "[italic]No birthday[/italic]"
            if contact.birthday:
                birthday = contact.birthday #.value.strftime("%d.%m.%Y") should be fine due to __str__ method

            # email = ", ".join(email.value for email in contact.emails) or "[italic]No email[/italic]"
            email = contact.email or "[italic]No email[/italic]"

            table.add_row(str(i), name, phones, birthday, email)
