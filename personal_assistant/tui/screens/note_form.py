from datetime import datetime
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Input,
    TextArea,
    Button,
    Label,
    Static,
)
from textual.message import Message

from personal_assistant.models.note import Note
from personal_assistant.models.notes_book import NotesBook
from personal_assistant.models.exceptions import (
    InvalidTitleFormatError,
    InvalidTagFormatError,
    TagAlreadyExistsError,
    ContactBotError,
)


class NoteFormScreen(Screen):
    """
    Modal screen for adding/updating notes.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    class NoteSaved(Message):
        """Message sent when a note is successfully saved."""
        def __init__(self, note: Note, is_update: bool):
            super().__init__()
            self.note = note
            self.is_update = is_update

    def __init__(self, notes_book: NotesBook, existing_note: Note | None = None, **kwargs):
        super().__init__(**kwargs)
        self.notes_book = notes_book
        self.existing_note = existing_note
        self.is_update = existing_note is not None

    def compose(self) -> ComposeResult:
        yield Header(name="📝 Add Note" if not self.is_update else "✏️ Edit Note")

        with Container(id="form-container"):
            with Vertical(id="form-fields"):
                yield Label("Title (must be > 5 symbols):", classes="field-label")
                yield Input(
                    id="title-input",
                    placeholder="Enter note title...",
                    value=self.existing_note.title.value if self.existing_note else "",
                )

                yield Label("Creation Date:", classes="field-label")
                creation_date_str = (
                    self.existing_note.creation_date.strftime("%d.%m.%Y %H:%M:%S")
                    if self.existing_note
                    else datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                )
                yield Static(
                    creation_date_str,
                    id="creation-date-display",
                    classes="readonly-field",
                )

                yield Label("Description:", classes="field-label")
                yield TextArea(
                    id="description-input",
                    text=self.existing_note.description if self.existing_note else "",
                )

                yield Label("Tags (comma-separated, each > 3 symbols, no % & special symbols):", classes="field-label")
                tags_value = (
                    ", ".join(t.value for t in self.existing_note.tags)
                    if self.existing_note and self.existing_note.tags
                    else ""
                )
                yield Input(
                    id="tags-input",
                    placeholder="tag1, tag2, tag3...",
                    value=tags_value,
                )

                yield Static("", id="error-message", classes="error-message")

            with Horizontal(id="form-buttons"):
                yield Button("Save", id="save-button", variant="primary")
                yield Button("Cancel", id="cancel-button", variant="default")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.query_one("#title-input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-button":
            self.action_save()
        elif event.button.id == "cancel-button":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the note."""
        error_widget = self.query_one("#error-message", Static)
        error_widget.update("")

        try:
            # Get form values
            title_input = self.query_one("#title-input", Input)
            description_input = self.query_one("#description-input", TextArea)
            tags_input = self.query_one("#tags-input", Input)

            title = title_input.value.strip()
            # TextArea uses .text property to get the content
            description = description_input.text.strip()
            tags_str = tags_input.value.strip()

            # Validate title
            if not title or len(title) <= 5:
                error_widget.update("[bold red]Error: Title must be more than 5 symbols.[/bold red]")
                title_input.focus()
                return

            # Create or update note
            if self.is_update and self.existing_note:
                # Update existing note
                note = self.existing_note
                # If title changed, we need to handle it specially
                if title != note.title.value:
                    # Remove old note and create new one with new title
                    del self.notes_book[note.title.value]
                    note = Note(title, description)
                    note.creation_date = self.existing_note.creation_date  # Preserve creation date
                else:
                    note.update_title(title)
                    note.update_description(description)
                    note.tags.clear()  # Clear existing tags
            else:
                # Create new note
                note = Note(title, description)

            # Add tags
            if tags_str:
                tag_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                for tag in tag_list:
                    try:
                        note.add_tag(tag)
                    except InvalidTagFormatError as e:
                        error_widget.update(f"[bold red]Error: {e}[/bold red]")
                        tags_input.focus()
                        return
                    except TagAlreadyExistsError:
                        # Skip duplicate tags
                        pass

            # Add note to book
            self.notes_book.add_note(note)

            # Send message and close
            self.post_message(self.NoteSaved(note, self.is_update))
            self.app.pop_screen()

        except InvalidTitleFormatError as e:
            error_widget.update(f"[bold red]Error: {e}[/bold red]")
            self.query_one("#title-input").focus()
        except ContactBotError as e:
            error_widget.update(f"[bold red]Error: {e}[/bold red]")
        except Exception as e:
            error_widget.update(f"[bold red]Unexpected error: {e}[/bold red]")

    def action_cancel(self) -> None:
        """Cancel and close the form."""
        self.app.pop_screen()

