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
from personal_assistant.services.commands import get_command
from personal_assistant.tui.screens.help.help import HelpScreen


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

    #form-buttons {
        align: center;
        margin-top: 1;
        height: 3;
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
            css_path = None,
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

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when the user presses Enter the Input widget."""

        user_input = event.value

        self.query_one(Input).value = ""

        self.log_widget.write(f"> {user_input}")

        try:
            command_id, args = parse_input(user_input)

            if command_id == "exit":
                await self.action_quit()
                return

            self.log_widget.write(get_command(command_id)(args, self.book))
        except KeyboardInterrupt:
            self.log_widget.write("[bold red]🦥 Uhh... I looked everywhere. No such command_id.[/bold red]")
