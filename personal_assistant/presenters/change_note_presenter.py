from typing import TYPE_CHECKING
from personal_assistant.models.note import Note
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.notes_storage import NotesStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ChangeNotePresenter(Presenter):
    def __init__(self, storage: NotesStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "change-note"

    @property
    def description(self) -> str:
        return "Changes a note's information"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide note title or UUID[/bold red]")
            return

        search_term = " ".join(args)
        notes = self.storage.search_by_title(search_term)

        if not notes:
            note = self.storage.get_note_by_id(search_term)
            notes = [note] if note else []

        if not notes:
            app.log_widget.write(f"[bold red]Note '{search_term}' not found[/bold red]")
            return

        if len(notes) > 1:
            app.log_widget.write(
                "[bold yellow]Multiple notes found. Please be more specific.[/bold yellow]"
            )
            for note in notes:
                app.log_widget.write(
                    f"- {note.title.value} (UUID: {note.uuid})"
                )
            return

        existing_note = notes[0]

        app.run_worker(self._handle_change_note(app, existing_note))

    async def _handle_change_note(self, app: "AddressBookApp", existing_note: Note) -> None:
        from personal_assistant.tui.screens.note_form import NoteFormScreen

        result = await app.push_screen_wait(NoteFormScreen(existing_note=existing_note))

        if result and result[0]:
            success, message, note_data = result

            try:
                note = Note.from_dict(note_data)
                self.storage.update_record(note)
                app.log_widget.write(f"[bold green]✅ {message}[/bold green]")
            except Exception as e:
                app.log_widget.write(f"[bold red]Failed to update note: {e}[/bold red]")
        elif result:
            app.log_widget.write(f"[bold yellow]{result[1]}[/bold yellow]")

