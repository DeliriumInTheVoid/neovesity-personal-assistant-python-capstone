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

from personal_assistant.cli.args_parsers import parse_input
from personal_assistant.presenters.presenters_registry import PresentersRegistry
from personal_assistant.tui.screens.help.help import HelpScreen
from personal_assistant.storage.address_book import AddressBookStorage
from personal_assistant.storage.notes_storage import NotesStorage
from personal_assistant.config import AppConfig


class AddressBookApp(App):
    """Textual interface for the address book."""

    INPUT_SUGGESTIONS = [
        "hello",
        "help",
        "add-contact",
        "search",
        "search-phone",
        "search-email",
        "search-notes",
        "search-tag",
        "all",
        "all-notes",
        "add-note",
        "change-contact",
        "change-note",
        "delete-contact",
        "delete-note",
        "phone",
        #"add-birthday",
        "show-birthday",
        "birthdays",
        "generate-data",
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

    ConfirmationScreen {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $primary;
        background: $surface;
    }

    #question {
        column-span: 2;
        height: 100%;
        width: 100%;
        content-align: center middle;
    }

    #yes {
        width: 100%;
    }

    #no {
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
        mode: str = "test",
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        # Set application mode
        AppConfig.set_mode(mode)

        self.log_widget = None
        self.address_book_storage = AddressBookStorage()
        self.notes_storage = NotesStorage()
        self.command_registry = PresentersRegistry(
            self.address_book_storage, self.notes_storage
        )

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
        self.log_widget = self.query_one(RichLog)

        self.log_widget.write("[bold green]Welcome to the assistant bot![/bold green]")
        self.log_widget.write(
            "Type commands below and press Enter. (Write close or exit to save and quit)"
        )

        self.query_one(Input).focus()

    async def action_quit(self) -> None:
        """Called when the user write exit."""

        self.log_widget.write("[bold red]Good bye!👋[/bold red]")
        await asyncio.sleep(1)
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

        command_id, args = parse_input(user_input)

        if command_id == "exit" or command_id == "close":
            await self.action_quit()
            return

        if command_id == "clear":
            self.log_widget.clear()
            return

        command = self.command_registry.get(command_id)

        if not command:
            self.show_inline_help(command_id)
            return

        try:
            await command.execute_tui(self, args)
        except Exception as e:
            self.log_widget.write(f"[bold red]An error occurred: {e}[/bold red]")

    def show_inline_help(self, command_id:str) -> None:
        """Show inline help in the log widget."""
        self.log_widget.write(
            f"[bold red]🦥 Uhh... I looked everywhere. No such '{command_id}'.[/bold red]"
        )

        output = "[bold green]Available commands:[/bold green]\n\n"

        for cmd_name, presenter in sorted(self.command_registry.commands.items()):
            if cmd_name != "exit":
                output += f"[bold cyan]{cmd_name:20}[/bold cyan] - {presenter.description}\n"

        output += f"[bold cyan]{'exit':20}[/bold cyan] - Exit the application\n"

        self.log_widget.write(output)
