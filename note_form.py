"""
Simple test script for the NoteFormScreen.

Run this script to test the note form:
    python test_note_form.py
"""

from personal_assistant.models.notes_book import NotesBook
from personal_assistant.tui.screens.note_form import NoteFormScreen
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Header, Footer, RichLog, Button, Static


class TestNoteFormApp(App):
    """Simple test app to test the note form."""

    CSS = """
    Screen {
        layout: vertical;
    }
    
    #main-container {
        margin: 1;
        padding: 1;
    }
    
    #notes-log {
        height: 70%;
        border: solid white;
        margin: 1;
    }
    
    #buttons-container {
        height: auto;
        margin: 1;
        align: center middle;
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
        align: center middle;
        margin-top: 1;
        height: 3;
    }

    #save-button {
        margin-right: 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_note", "Add Note"),
    ]

    def __init__(self):
        super().__init__()
        self.notes_book = NotesBook()
        self.log_widget = None

    def compose(self) -> ComposeResult:
        """Create the main screen."""
        yield Header(name="📝 Notes Test App")
        
        with VerticalScroll(id="main-container"):
            yield RichLog(id="notes-log", markup=True)
            yield Static("", id="status")
            
            with Horizontal(id="buttons-container"):
                yield Button("Add Note (or press 'a')", id="add-button", variant="primary")
                yield Button("Quit (or press 'q')", id="quit-button", variant="default")

        yield Footer()

    def on_mount(self):
        """Called when app is mounted."""
        self.log_widget = self.query_one("#notes-log", RichLog)
        self.log_widget.write("[bold green]Welcome to Notes Test App![/bold green]")
        self.log_widget.write("Press 'a' or click 'Add Note' to create a new note.")
        self.log_widget.write("Press 'q' or click 'Quit' to exit.\n")
        self.update_notes_display()

    def update_notes_display(self):
        """Update the status display with current notes count."""
        status = self.query_one("#status", Static)
        
        if len(self.notes_book) == 0:
            status.update("[yellow]No notes yet. Add your first note![/yellow]")
        else:
            status.update(f"[green]Total notes: {len(self.notes_book)}[/green]")

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        if event.button.id == "add-button":
            self.action_add_note()
        elif event.button.id == "quit-button":
            self.action_quit()

    def action_add_note(self):
        """Open the note form to add a new note."""
        self.push_screen(NoteFormScreen(self.notes_book))

    def action_quit(self):
        """Quit the application."""
        self.exit()

    def on_note_form_screen_note_saved(self, event: NoteFormScreen.NoteSaved) -> None:
        """Handle note saved event."""
        self.log_widget = self.query_one("#notes-log", RichLog)
        if event.is_update:
            self.log_widget.write(f"[green]✓ Note '{event.note.title.value}' updated successfully![/green]")
        else:
            self.log_widget.write(f"[green]✓ Note '{event.note.title.value}' added successfully![/green]")
        
        # Display the saved note details
        tags_str = ", ".join(t.value for t in event.note.tags) if event.note.tags else "No tags"
        self.log_widget.write(
            f"  [bold]{event.note.title.value}[/bold]\n"
            f"  Created: {event.note.creation_date.strftime('%d.%m.%Y %H:%M')}\n"
            f"  Description: {event.note.description[:50]}{'...' if len(event.note.description) > 50 else ''}\n"
            f"  Tags: {tags_str}\n"
        )
        self.update_notes_display()


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Note Form")
    print("=" * 50)
    print("\nInstructions:")
    print("1. Fill in the form fields")
    print("2. Title must be > 5 symbols")
    print("3. Tags must be > 3 symbols each, comma-separated")
    print("4. Tags cannot contain % & or special symbols")
    print("5. Press Ctrl+S to save or Escape to cancel")
    print("6. After saving, check the terminal for confirmation")
    print("\n" + "=" * 50 + "\n")
    
    app = TestNoteFormApp()
    app.run()

