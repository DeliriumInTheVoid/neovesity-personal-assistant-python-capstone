import asyncio
from typing import Type

from textual.driver import Driver
from textual.suggester import SuggestFromList
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    RichLog,
    Input,
)

from personal_assistant.cli.contacts_bot import save_data, load_data, parse_input
from personal_assistant.use_cases.commands import get_command
from personal_assistant.tui.screens.help.help import HelpScreen
from personal_assistant.tui.screens.all_contacts import AllContactsScreen
from personal_assistant.tui.screens.add_contact import AddContactScreen
from personal_assistant.tui.screens.birthday import BirthdaysScreen
from personal_assistant.use_cases.commands import add_contact


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


    AddContactScreen {
        align: center middle;
    }

    #add-contact-form {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 1 2;
    }
    
    #add-contact-form .title {
        width: 100%;
        text-align: center;
        padding-bottom: 1;
    }

    #add-contact-form Static {
        margin-top: 1;
        width: 100%;
    }
    
    #add-contact-form Input {
        width: 100%;
    }
    
    #add-contact-form Input:disabled {
        background: $boost;
        color: $text-muted;
        border: solid $panel;
    }
    
    #form-error {
        height: auto;
        margin-top: 1;
        color: red;
        display: none;
    }

    #form-buttons {
        width: 100%;
        align: center middle;
        margin-top: 2;
    }

    #form-buttons Button {
        margin: 0 1;
    }

    NoteFormScreen {
        layout: vertical;
    }

    #form-container {
        margin: 1;
        padding: 1;
    }

    #form-fields {
        height: auto;
        margin: 1;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
        text-style: bold;
    }

    #title-input {
        width: 100%;
        margin-bottom: 1;
    }

    #creation-date-display {
        width: 100%;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
        border: solid $primary;
    }

    .readonly-field {
        color: $text-muted;
    }

    #description-input {
        width: 100%;
        height: 10;
        margin-bottom: 1;
    }

    #tags-input {
        width: 100%;
        margin-bottom: 1;
    }

    #error-message {
        margin-top: 1;
        margin-bottom: 1;
        min-height: 1;
    }

    #save-button {
        margin-right: 2;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("f1", "show_help", "Help"),
    ]

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path=None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)
        self.log_widget = None
        self.book = None

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
        save_data(self.book, True)
        await asyncio.sleep(2)
        self.exit()

    def action_show_help(self) -> None:
        """Show help screen when F1 is pressed."""
        self.push_screen(HelpScreen())

    def log_operation_result(self, result: tuple) -> None:
        """Callback to log the result of a modal screen operation."""
        if result:
            success, message = result
            if success:
                self.log_widget.write(f"[bold green]✅ {message}[/bold green]")
            else:
                if "cancelled" not in message.lower():
                    self.log_widget.write(f"[bold yellow]ℹ️ {message}[/bold yellow]")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when the user presses Enter the Input widget."""

        user_input = event.value

        self.query_one(Input).value = ""

        self.log_widget.write(f"> {user_input}")

        command, args = parse_input(user_input)

        #     if command_id == "exit":
        #         await self.action_quit()
        #         return

        #     self.log_widget.write(get_command(command_id)(args, self.book))
        # except KeyboardInterrupt:
        #     self.log_widget.write(
        #         "[bold red]🦥 Uhh... I looked everywhere. No such command_id.[/bold red]"
        #     )

        match command:
            case "hello":
                self.log_widget.write("How can I help you?")

            case "help":
                self.push_screen(HelpScreen())

            case "add-contact":
                if not args:

                    self.push_screen(
                        AddContactScreen(self.book), self.log_operation_result
                    )
                else:
                    self.log_widget.write(add_contact(args, self.book))

            case "change-contact":
                if not args:
                    self.log_widget.write(
                        "[bold red]Please provide a name to edit. (e.g., 'change-contact Yura')[/bold red]"
                    )
                    return

                name_to_edit = args[0]

                found_record = None
                name_to_edit_lower = name_to_edit.lower()

                for record_name in self.book.data.keys():
                    if record_name.lower() == name_to_edit_lower:
                        found_record = self.book.data[record_name]
                        break

                if found_record:

                    self.push_screen(
                        AddContactScreen(self.book, record_to_edit=found_record),
                        self.log_operation_result,
                    )
                else:
                    self.log_widget.write(
                        f"[bold red]Contact '{name_to_edit}' not found.[/bold red]"
                    )

            case "all":
                if not self.book.data:
                    self.log_widget.write("Contacts list is empty")
                else:
                    self.push_screen(AllContactsScreen(self.book))

            case "birthdays":
                self.push_screen(BirthdaysScreen(self.book))

            case "clear":
                self.log_widget.clear()

            case "exit" | "close":
                await self.action_quit()

            case _:
                self.log_widget.write(
                    "[bold red]🦥 Uhh... I looked everywhere. No such command.[/bold red]"
                )
