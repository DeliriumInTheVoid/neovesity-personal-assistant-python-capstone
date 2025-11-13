"""
Module for managing a simple address book.

Provides classes for contact fields, individual contact records,
and an address book that stores multiple records.
"""

from collections import UserDict
import pickle
import re
from datetime import datetime, date, timedelta
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Vertical
from textual.widgets import (
    Header,
    Footer,
    RichLog,
    Input,
    MarkdownViewer,
    DataTable,
)
from textual.screen import Screen
from textual.suggester import SuggestFromList
import asyncio
from markdown.help_markdown import HELP_MARKDOWN


class CustomValueError(ValueError):
    """Class for handle custom errors"""

    def __init__(self, message="Something went wrong"):
        self.message = message
        super().__init__(self.message)


class Field:
    """Base class for contact fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Class for contact name."""

    def __init__(self, value):
        if not value or not value.strip():
            raise CustomValueError("Name cannot be empty")

        super().__init__(value)


class Birthday(Field):
    """Class for user birthday"""

    def __init__(self, value):
        try:
            if isinstance(value, date):
                data_object = value
            else:
                data_object = datetime.strptime(value, "%d.%m.%Y").date()

            super().__init__(data_object)
        except ValueError:
            raise CustomValueError("Invalid date format. Use DD.MM.YYYY")


class Phone(Field):
    """Class for phone number."""

    def __init__(self, value):
        validate_value = self.validate_number(value)

        super().__init__(validate_value)

    @staticmethod
    def validate_number(phone_number):
        """Validate phone number"""

        if not phone_number or not phone_number.strip():
            raise CustomValueError("Phone number cannot be empty")

        if not re.fullmatch(r"\d{10}", phone_number):
            raise CustomValueError(
                f"Number {phone_number} is invalid. Must be exactly 10 digits."
            )

        return phone_number


class Record:
    """Class representing a single contact with a name and a list of phones."""

    def __init__(self, name=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        """Validate and add phone number to contact book"""

        validated_number = Phone(phone_number)
        self.phones.append(validated_number)

    def find_phone(self, phone_number):
        """Find phone number in contact book"""

        for number in self.phones:
            if number.value == phone_number:
                return number

        return None

    def remove_phone(self, phone_number):
        """Remove phone number from contact book"""

        phone = self.find_phone(phone_number)

        if phone:
            self.phones.remove(phone)

    def edit_phone(self, old_phone_number, new_phone_number):
        """Edit phone number in contact book"""

        phone_to_edit = self.find_phone(old_phone_number)

        if phone_to_edit:
            validated_new_phone = Phone(new_phone_number)
            phone_to_edit.value = validated_new_phone.value

    def add_birthday(self, data_of_birth):
        """Add birthday"""
        self.birthday = Birthday(data_of_birth)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    """Class representing an address book, where keys are names and values are Record instances."""

    def add_record(self, record):
        """Add recort to contact book"""

        self.data[record.name.value] = record

    def find(self, name):
        """Find contact in contact book"""

        return self.data.get(name)

    def delete(self, name):
        """Delete contact from contact book"""

        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        """Returns a list of users to be congratulated by day of the week."""

        today = datetime.today().date()
        date_format = "%d.%m.%Y"
        user_birthdays = []

        for user in self.data.values():
            if not user.birthday:
                continue

            user_birthday = user.birthday.value
            birthday_this_year = user_birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = user_birthday.replace(year=today.year + 1)

            days_to_birthday = (birthday_this_year - today).days

            if 0 <= days_to_birthday <= 7:
                if birthday_this_year.weekday() == 5:
                    congratulation_date = birthday_this_year + timedelta(days=2)

                elif birthday_this_year.weekday() == 6:
                    congratulation_date = birthday_this_year + timedelta(days=1)

                else:
                    congratulation_date = birthday_this_year

                user_birthdays.append(
                    {
                        "name": user.name.value,
                        "birthday": user.birthday.value.strftime(date_format),
                        "congratulation_date": congratulation_date.strftime(
                            date_format
                        ),
                    }
                )

        return user_birthdays


def input_error(func):
    """
    Decorator to handle common input-related errors for functions.
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomValueError as e:
            return str(e)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Enter correct name."
        except IndexError:
            return "Not enough arguments. Please provide required data."
        except AttributeError:
            return "Contact not found."

    return inner


@input_error
def parse_input(user_input: str):
    """Parse user input into a command and its arguments."""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()

    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    """Add contact to contact book"""
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args, book: AddressBook):
    """Change the phone number of an existing contact."""

    name, old_phone_number, new_phone_number, *_ = args
    record = book.find(name)

    record.edit_phone(old_phone_number, new_phone_number)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    """Return the phone number of a contact."""

    name = args[0]
    record = book.find(name)
    if record:
        phones = ", ".join(p.value for p in record.phones)
        return f"{name}'s phone number is {phones}"


def show_all(book: AddressBook) -> str:
    """Return all contacts as a formatted string."""

    if not book.data:
        return "Contacts list are empty"

    result = []
    for record in book.data.values():
        phones = ", ".join(p.value for p in record.phones) or "No phones"
        birthday = (
            record.birthday.value.strftime("%d.%m.%Y")
            if record.birthday
            else "No birthday"
        )
        result.append(
            f"Contact name: {record.name.value}, phones: {phones}, birthday: {birthday}"
        )
    return "\n".join(result)


@input_error
def add_birthday(args, book: AddressBook):
    """Add birthday for user"""
    name, birthday, *_ = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)

    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    """Show birthday function"""
    name = args[0]
    record = book.find(name)

    if record and record.birthday:
        return f"{name}'s birthday is in {record.birthday.value.strftime('%d.%m.%Y')}"

    return "Birthday not found"


@input_error
def birthdays(book: AddressBook):
    """Show upcoming birthday function"""
    upcoming = book.get_upcoming_birthdays()
    result = ""

    if not upcoming:
        return "No birthdays"

    for user_birthday in upcoming:
        result += f"name: {user_birthday['name']}, congratulate on: {user_birthday['congratulation_date']}\n"

    return result


def save_data(book, filename="addressbook.pkl"):
    """Save contacts"""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """Load contacts"""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


@input_error
def search_contacts(args, book: AddressBook):
    """Search contacts by partial match in name or phone"""
    query = args[0].lower()
    results = []

    for record in book.data.values():
        if query in record.name.value.lower() or any(
            query in p.value for p in record.phones
        ):
            phones = ", ".join(p.value for p in record.phones)
            results.append(f"{record.name.value}: {phones}")

    if results:
        return "\n".join(results)
    return "No matches found."


class AddressBookApp(App):
    """Textual interface for the address book."""

    INPUT_SUGGESTIONS = [
        "help",
        "add-contact",
        "change-contact",
        "phone",
        "all",
        "hello",
        "add-birthday",
        "show-birthday",
        "birthdays",
        "search",
        "clear",
        "exit",
        "close",
    ]

    CSS = """
    #main-log-container {
        height: 80%; 
        border: solid white;
        margin: 1;
    }
    #command-input {
        dock: bottom;
        margin: 0 1 1 1;
    }
    AllContactsScreen {
        layout: vertical;
    }
    
    #all-contacts-table {
        height: 100%;
        width: 100%;
    }

    BirthdaysScreen {
        layout: vertical;
    }
    
    #birthdays-table {
        height: 100%;
        width: 100%;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("f1", "show_help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(name="📖 Address Book TUI")

        with VerticalScroll(id="main-log-container"):
            yield RichLog(id="main-log", highlight=True, markup=True)

        command_suggester = SuggestFromList(
            self.INPUT_SUGGESTIONS, case_sensitive=False
        )

        yield Input(
            id="command-input",
            placeholder="Enter command (e.g., 'all', 'add Bob 123...')",
            suggester=command_suggester,
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is first mounted."""
        self.book = load_data()

        self.log_widget = self.query_one(RichLog)

        self.log_widget.write("[bold green]Welcome to the assistant bot![/bold green]")
        self.log_widget.write(
            "Type commands below and press Enter. (Write close or exit to save and quit)"
        )

        self.query_one(Input).focus()

    async def action_quit(self) -> None:
        """Called when the user write exit."""

        self.log_widget.write("[bold red]Saving data... Good bye!👋[/bold red]")
        save_data(self.book)
        await asyncio.sleep(2)
        self.exit()

    def action_show_help(self) -> None:
        """Show help screen when F1 is pressed."""
        self.push_screen(HelpScreen())

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when the user presses Enter in the Input widget."""

        user_input = event.value

        self.query_one(Input).value = ""

        self.log_widget.write(f"> {user_input}")

        try:
            command, *args = parse_input(user_input)
        except ValueError:
            self.log_widget.write("[bold red]Invalid command (empty)[/bold red]")
            return

        match command:
            case "hello":
                self.log_widget.write("How can I help you?")
            case "help":
                self.push_screen(HelpScreen())
            case "add-contact":
                self.log_widget.write(add_contact(args, self.book))
            case "change-contact":
                self.log_widget.write(change_contact(args, self.book))
            case "phone":
                self.log_widget.write(show_phone(args, self.book))
            case "all":
                if not self.book.data:
                    self.log_widget.write("Contacts list is empty")
                else:
                    self.push_screen(AllContactsScreen(self.book))
            case "add-birthday":
                self.log_widget.write(add_birthday(args, self.book))
            case "show-birthday":
                self.log_widget.write(show_birthday(args, self.book))
            case "birthdays":
                self.push_screen(BirthdaysScreen(self.book))
            case "search":
                self.log_widget.write(search_contacts(args, self.book))
            case "clear":
                self.log_widget.clear()
            case "exit" | "close":
                await self.action_quit()
            case _:
                self.log_widget.write(
                    "[bold red]🦥 Uhh... I looked everywhere. No such command.[/bold red]"
                )


class HelpScreen(Screen):
    """
    Modal screen showing help.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Close Help"),
        ("f1", "show_help", None),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            MarkdownViewer(HELP_MARKDOWN, show_table_of_contents=True),
            id="help_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus on the scroll widget"""
        self.query_one(MarkdownViewer).focus()


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

        for i, user in enumerate(upcoming, start=1):
            table.add_row(str(i), user["name"], user["congratulation_date"])


if __name__ == "__main__":
    app = AddressBookApp()
    app.run()
