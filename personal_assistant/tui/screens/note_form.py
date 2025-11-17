from datetime import datetime
from textual.app import ComposeResult
from textual.screen import ModalScreen
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


class NoteFormScreen(ModalScreen):

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    class NoteSaved(Message):
        def __init__(self, note: Note, is_update: bool):
            super().__init__()
            self.note = note
            self.is_update = is_update

    def __init__(self, existing_note: Note | None = None, **kwargs):
        super().__init__(**kwargs)
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
                    ", ".join(tag.value for tag in self.existing_note.tags)
                    if self.existing_note
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
            title_input = self.query_one("#title-input", Input)
            description_input = self.query_one("#description-input", TextArea)
            tags_input = self.query_one("#tags-input", Input)

            title = title_input.value.strip()
            description = description_input.text.strip()
            tags_str = tags_input.value.strip()

            if not title or len(title) <= 5:
                error_widget.update("[bold red]Error: Title must be more than 5 symbols.[/bold red]")
                title_input.focus()
                return

            tags_list = []
            if tags_str:
                tags_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                for tag in tags_list:
                    if len(tag) <= 3:
                        error_widget.update(f"[bold red]Error: Tag '{tag}' must be more than 3 symbols.[/bold red]")
                        tags_input.focus()
                        return
                    if any(char in tag for char in '%&'):
                        error_widget.update(f"[bold red]Error: Tag '{tag}' contains invalid characters.[/bold red]")
                        tags_input.focus()
                        return

            note_data = {
                "title": title,
                "content": description,
                "tags": tags_list,
            }

            if self.is_update and self.existing_note:
                note_data["uuid"] = self.existing_note.uuid
                note_data["created_at"] = self.existing_note.creation_date.isoformat()

            self.dismiss((True, f"Note '{title}' saved", note_data))

        except Exception as e:
            error_widget.update(f"[bold red]Unexpected error: {e}[/bold red]")

    def action_cancel(self) -> None:
        self.dismiss((False, "Operation cancelled", None))
