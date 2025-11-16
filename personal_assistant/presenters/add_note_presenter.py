from typing import TYPE_CHECKING
from personal_assistant.models.note import Note
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.notes_storage import NotesStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class AddNotePresenter(Presenter):
    def __init__(self, storage: NotesStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "add-note"

    @property
    def description(self) -> str:
        return "Adds a new note"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        app.run_worker(self._handle_add_note(app))

    async def _handle_add_note(self, app: "AddressBookApp") -> None:
        from personal_assistant.tui.screens.note_form import NoteFormScreen

        app.log_widget.write("[dim]Opening note form...[/dim]")
        result = await app.push_screen_wait(NoteFormScreen())
        app.log_widget.write(f"[dim]Form returned result: {result}[/dim]")

        if result and result[0]:
            success, message, note_data = result

            try:
                note = Note.from_dict(note_data)
                note_uuid = self.storage.add_note(note)
                app.log_widget.write(f"[bold green]✅ {message} (ID: {note_uuid})[/bold green]")
            except Exception as e:
                app.log_widget.write(f"[bold red]Failed to save note: {e}[/bold red]")
                import traceback
                app.log_widget.write(f"[red]{traceback.format_exc()}[/red]")
        elif result:
            app.log_widget.write(f"[bold yellow]{result[1]}[/bold yellow]")
        else:
            app.log_widget.write("[yellow]No result returned from form[/yellow]")
