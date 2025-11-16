from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.notes_storage import NotesStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class SearchNotesPresenter(Presenter):
    def __init__(self, storage: NotesStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "search-notes"

    @property
    def description(self) -> str:
        return "Searches for notes"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a search term[/bold red]")
            return

        search_term = args[0]
        notes = self.storage.search_by_title(search_term)

        if not notes:
            notes = self.storage.search_by_content(search_term)

        if not notes:
            app.log_widget.write(f"[bold yellow]No notes found for '{search_term}'[/bold yellow]")
            return

        output = f"[bold green]Found {len(notes)} note(s):[/bold green]\n"
        for note in notes:
            output += f"\n[bold cyan]{note.title.value}[/bold cyan]\n"
            output += f"{note.description}\n"
            if note.tags:
                output += f"Tags: {', '.join(tag.value for tag in note.tags)}\n"

        app.log_widget.write(output)
