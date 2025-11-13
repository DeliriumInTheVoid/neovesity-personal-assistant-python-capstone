from textual.screen import ModalScreen
from personal_assistant.models.address_book import AddressBook
from personal_assistant.models.phone import Phone
from typing import Optional
from personal_assistant.models.record import Record
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Input,
    Static,
    Button,
)


class AddContactScreen(ModalScreen):
    """Screen with a form to add or edit a contact."""

    def __init__(
        self,
        book: AddressBook,
        record_to_edit: Optional[Record] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.book = book
        self.record_to_edit = record_to_edit

    def compose(self) -> ComposeResult:
        with Vertical(id="add-contact-form"):

            yield Static("Add New Contact", classes="title")

            yield Static(id="form-error")

            yield Static("Name: [red]*[/red]")
            yield Input(id="name-input", placeholder="John Doe")

            yield Static("Phone: [red]*[/red]")
            yield Input(id="phone-input", placeholder="1234567890")

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
        """Focus the first input field and populate form if in edit mode."""
        self.query_one("#form-error", Static).display = False

        if self.record_to_edit:

            self.query_one(".title", Static).update("Edit Contact")

            name_input = self.query_one("#name-input", Input)
            name_input.value = self.record_to_edit.name.value
            name_input.disabled = True

            if self.record_to_edit.phones:

                self.query_one("#phone-input", Input).value = (
                    self.record_to_edit.phones[0].value
                )

            if self.record_to_edit.birthday:
                self.query_one("#birthday-input", Input).value = (
                    self.record_to_edit.birthday.value.strftime("%d.%m.%Y")
                )

            if self.record_to_edit.email and self.record_to_edit.email.value:
                self.query_one("#email-input", Input).value = (
                    self.record_to_edit.email.value
                )

            if self.record_to_edit.address and self.record_to_edit.address.value:
                self.query_one("#address-input", Input).value = (
                    self.record_to_edit.address.value
                )

            self.query_one("#phone-input", Input).focus()

        else:

            self.query_one("#name-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle submit or cancel button presses."""
        if event.button.id == "cancel-form":

            self.dismiss((False, "Add/Edit contact cancelled."))

        elif event.button.id == "submit-form":
            error_widget = self.query_one("#form-error", Static)

            name = self.query_one("#name-input", Input).value
            phone = self.query_one("#phone-input", Input).value
            birthday_str = self.query_one("#birthday-input", Input).value

            try:
                if self.record_to_edit:
                    record = self.record_to_edit
                    message = "Contact updated."
                    validated_phone = Phone(phone)

                    if record.phones:
                        record.phones[0].value = validated_phone.value
                    else:
                        record.phones.append(validated_phone)

                    if birthday_str:
                        record.add_birthday(birthday_str)
                    else:
                        record.birthday = None

                else:

                    record = self.book.find(name)
                    message = "Contact updated."

                    if record is None:
                        record = Record(name)
                        self.book.add_record(record)
                        message = "Contact added."

                    record.add_phone(phone)

                    if birthday_str:
                        record.add_birthday(birthday_str)

                self.dismiss((True, f"{message} (Name: {record.name.value})"))

            except Exception as e:
                error_widget.update(f"[red]Error:[/red] {str(e)}")
                error_widget.display = True
