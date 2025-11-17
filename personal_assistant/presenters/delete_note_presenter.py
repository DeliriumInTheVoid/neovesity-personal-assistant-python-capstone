from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.notes_storage import NotesStorage
from personal_assistant.tui.screens.confirmation_screen import ConfirmationScreen

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class DeleteNotePresenter(Presenter):
    def __init__(self, storage: NotesStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "delete-note"

    @property
    def description(self) -> str:
        return "Deletes a note by title or UUID"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        app.run_worker(self._handle_delete_note(app, args))

    async def _handle_delete_note(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a note title or UUID.[/bold red]")
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
                "[bold yellow]Multiple notes found. Please be more specific by providing a UUID.[/bold yellow]"
            )
            for note in notes:
                app.log_widget.write(
                    f"- {note.title.value} (UUID: {note.uuid})"
                )
            return

        note_to_delete = notes[0]

        confirmed = await app.push_screen_wait(
            ConfirmationScreen(
                f"Are you sure you want to delete note '{note_to_delete.title.value}'?"
            )
        )

        if confirmed:
            if self.storage.delete_note(note_to_delete.uuid):
                app.log_widget.write(
                    f"[bold green]✅ Note '{note_to_delete.title.value}' deleted.[/bold green]"
                )
            else:
                app.log_widget.write(
                    f"[bold red]Failed to delete note '{note_to_delete.title.value}'.[/bold red]"
                )
        else:
            app.log_widget.write("[bold yellow]Deletion cancelled.[/bold yellow]")

