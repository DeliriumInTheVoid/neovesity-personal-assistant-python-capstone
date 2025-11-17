from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.notes_storage import NotesStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ShowAllNotesPresenter(Presenter):
    def __init__(self, storage: NotesStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "all-notes"

    @property
    def description(self) -> str:
        return "Shows all notes"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        notes = self.storage.get_all_notes()

        if not notes:
            app.log_widget.write("[bold yellow]No notes found[/bold yellow]")
            return

        output = "[bold green]All Notes:[/bold green]\n"
        for note in notes:
            output += f"\n[bold cyan]{note.title.value}[/bold cyan]\n"
            output += f"{note.description}\n"
            if note.tags:
                output += f"Tags: {', '.join(tag.value for tag in note.tags)}\n"

        app.log_widget.write(output)
