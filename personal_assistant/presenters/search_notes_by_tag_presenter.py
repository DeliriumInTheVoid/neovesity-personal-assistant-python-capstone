from typing import TYPE_CHECKING
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.notes_storage import NotesStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class SearchNotesByTagPresenter(Presenter):
    def __init__(self, storage: NotesStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "search-tag"

    @property
    def description(self) -> str:
        return "Search notes by tag"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        if not args:
            app.log_widget.write("[bold red]Please provide a tag to search for.[/bold red]")
            return

        tag = " ".join(args)

        notes = self.storage.search_by_tag(tag)

        if not notes:
            app.log_widget.write(f"[bold yellow]No notes found with tag '{tag}'[/bold yellow]")
            return

        app.log_widget.write(f"[bold green]Found {len(notes)} note(s) with tag '{tag}':[/bold green]\n")

        for note in notes:
            tags_str = ", ".join([tag.value for tag in note.tags]) if note.tags else "No tags"
            description_preview = note.description[:100] + "..." if len(note.description) > 100 else note.description
            app.log_widget.write(f"[bold cyan]Title:[/bold cyan] {note.title.value}")
            app.log_widget.write(f"[bold cyan]Tags:[/bold cyan] {tags_str}")
            app.log_widget.write(f"[bold cyan]UUID:[/bold cyan] {note.uuid}")
            app.log_widget.write(f"[bold cyan]Description:[/bold cyan] {description_preview}")

