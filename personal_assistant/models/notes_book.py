from collections import UserDict
from personal_assistant.models.note import Note
from personal_assistant.models.exceptions import NoteAlreadyExistsError, NoteNotFoundError


class NotesBook(UserDict):
    def __setitem__(self, key, value):
        if not isinstance(value, Note):
            raise ValueError("Value must be an instance of Note.")
        if key != value.title.value:
            raise ValueError("Key must match the Note's title.")
        if key in self.data:
            raise NoteAlreadyExistsError(f"Note '{key}' already exists.")
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if key not in self.data:
            raise NoteNotFoundError(f"Note '{key}' not found.")
        return super().__getitem__(key)

    def __delitem__(self, key):
        if key not in self.data:
            raise NoteNotFoundError(f"Note '{key}' not found.")
        super().__delitem__(key)

    def add_note(self, note: Note):
        """Add a note to the notes book."""
        self[note.title.value] = note

    def find(self, title: str) -> Note | None:
        """Find a note by title."""
        if title not in self:
            return None
        return self[title]

    def delete(self, title: str) -> None:
        """Delete a note by title."""
        del self[title]

    def search_by_tag(self, tag: str) -> list[Note]:
        """Search for notes containing a specific tag."""
        results = []
        tag_lower = tag.lower()
        for note in self.data.values():
            if any(t.value.lower() == tag_lower for t in note.tags):
                results.append(note)
        return results

    def search_by_title(self, query: str) -> list[Note]:
        """Search for notes by partial title match."""
        results = []
        query_lower = query.lower()
        for note in self.data.values():
            if query_lower in note.title.value.lower():
                results.append(note)
        return results

    def __str__(self):
        return '\n'.join(str(note) for note in self.data.values())


__all__ = ["NotesBook"]

