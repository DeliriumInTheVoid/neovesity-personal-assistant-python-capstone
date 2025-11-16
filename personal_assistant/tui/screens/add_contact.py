from textual.screen import ModalScreen
from typing import Optional
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Input,
    Static,
    Button,
)

from personal_assistant.models.record import Record


class AddContactScreen(ModalScreen):

    def __init__(
        self,
        existing_contact: Optional[Record] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.existing_contact = existing_contact

    def compose(self) -> ComposeResult:
        with Vertical(id="add-contact-form"):

            yield Static("Add New Contact", classes="title")

            yield Static(id="form-error")

            yield Static("Name: [red]*[/red]")
            yield Input(id="name-input", placeholder="John Doe")

            yield Static("Phone1: [red]*[/red]")
            yield Input(id="phone1-input", placeholder="0XXXXXXXXX")

            yield Static("Phone2:")
            yield Input(id="phone2-input", placeholder="0XXXXXXXXX")

            yield Static("Birthday:")
            yield Input(id="birthday-input", placeholder="DD.MM.YYYY")

            yield Static("Email:")
            yield Input(id="email-input", placeholder="john.doe@example.com")

            yield Static("Address:")
            yield Input(id="address-input", placeholder="123 Main St")

            with Horizontal(id="form-buttons"):
                yield Button("Submit", id="submit-form", variant="primary")
                yield Button("Cancel", id="cancel-form", variant="error")

    def on_mount(self) -> None:
        self.query_one("#form-error", Static).display = False

        if self.existing_contact:
            self.query_one(".title", Static).update("Edit Contact")

            first_name = self.existing_contact.first_name.value
            last_name = (
                self.existing_contact.last_name.value
                if self.existing_contact.last_name
                else ""
            )
            name = f"{first_name} {last_name}".strip()

            name_input = self.query_one("#name-input", Input)
            name_input.value = name

            phones = self.existing_contact.phones
            if len(phones) > 0:
                self.query_one("#phone1-input", Input).value = phones[0].value
            if len(phones) > 1:
                self.query_one("#phone2-input", Input).value = phones[1].value

            if self.existing_contact.birthday:
                self.query_one("#birthday-input", Input).value = (
                    self.existing_contact.birthday.value.strftime("%d.%m.%Y")
                )

            if self.existing_contact.email:
                self.query_one("#email-input", Input).value = (
                    self.existing_contact.email
                )

            if self.existing_contact.address:
                self.query_one("#address-input", Input).value = (
                    self.existing_contact.address
                )

            self.query_one("#phone1-input", Input).focus()

        else:

            self.query_one("#name-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-form":
            self.dismiss((False, "Operation cancelled", None))

        elif event.button.id == "submit-form":
            error_widget = self.query_one("#form-error", Static)

            name = self.query_one("#name-input", Input).value.strip()
            phone1 = self.query_one("#phone1-input", Input).value.strip()
            phone2 = self.query_one("#phone2-input", Input).value.strip()
            birthday_str = self.query_one("#birthday-input", Input).value.strip()
            email = self.query_one("#email-input", Input).value.strip()
            address = self.query_one("#address-input", Input).value.strip()

            if not name:
                error_widget.update("[red]Error:[/red] Name is required")
                error_widget.display = True
                return

            if not phone1:
                error_widget.update("[red]Error:[/red] Phone is required")
                error_widget.display = True
                return

            try:
                name_parts = name.split(maxsplit=1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                contact_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phones": [phone1, phone2],
                    "email": email if email else None,
                    "address": address if address else None,
                    "birthday": birthday_str if birthday_str else None,
                }

                if self.existing_contact:
                    contact_data["uuid"] = self.existing_contact.uuid
                    message = f"Contact '{name}' updated"
                else:
                    message = f"Contact '{name}' added"

                self.dismiss((True, message, contact_data))

            except Exception as e:
                error_widget.update(f"[red]Error:[/red] {str(e)}")
                error_widget.display = True
