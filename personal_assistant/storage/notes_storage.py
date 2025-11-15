"""
NotesStorage — high-level API for working with notes.

Uses HeapStorage for file storage and IndexManager for fast search.
"""

from typing import List, Optional, Set, Dict, Any

from personal_assistant.models.note import Note
from personal_assistant.storage.base_storage import BaseStorage
from personal_assistant.storage.constants import (
    INDEX_NOTE_TITLE,
    INDEX_NOTE_CREATION_DATE,
    NOTE_INDEXES,
)


class NotesStorage(BaseStorage):
    """
    High-level API for managing notes with indexing.
    """

    # ============================================================
    # Overrides from BaseStorage
    # ============================================================

    def _get_entity_type(self) -> str:
        """Get the entity type for notes."""
        return "notes"

    def _get_entity_indexes(self) -> List[str]:
        """Get list of all note indexes."""
        return NOTE_INDEXES

    def _add_to_indexes(self, note_uuid: str, note_data: Dict[str, Any]):
        """Add note to all indexes."""
        if note_data.get('title'):
            self.index_manager.add_to_trie_index(INDEX_NOTE_TITLE, note_data['title'], note_uuid)

        if note_data.get('created_at'):
            self.index_manager.add_to_date_index(INDEX_NOTE_CREATION_DATE, note_data['created_at'], note_uuid)

    def _remove_from_indexes(self, note_uuid: str, note_data: Dict[str, Any]):
        """Remove note from all indexes."""
        if note_data.get('title'):
            self.index_manager.remove_from_trie_index(INDEX_NOTE_TITLE, note_data['title'], note_uuid)

        if note_data.get('created_at'):
            self.index_manager.remove_from_date_index(INDEX_NOTE_CREATION_DATE, note_data['created_at'], note_uuid)

    # ============================================================
    # CRUD operations with indexing
    # ============================================================

    def add_note(self, note: Note) -> str:
        """
        Add a new note and update indexes.

        Args:
            note: note with data

        Returns:
            UUID of created note
        """

        new_note = self.heap.create_note(note.to_dict())
        uuid = new_note.get("uuid")
        self._add_to_indexes(uuid, new_note)

        return uuid

    def get_note_by_id(self, note_uuid: str) -> Optional[Note]:
        """
        Get note by UUID.

        Returns:
            Note with note data or None
        """
        return self.heap.read_note(note_uuid)

    def update_record(self, record: Note) -> bool:
        """
        Update note and its indexes.

        Args:
            record: note with data

        Returns:
            True if successful, False if note not found
        """
        old_note = self.heap.read_note(record.uuid)
        if not old_note:
            return False

        self._remove_from_indexes(old_note.uuid, old_note)

        raw_note = record.to_dict()
        if self.heap.update_note(record.uuid, raw_note):
            self._add_to_indexes(record.uuid, raw_note)
            return True
        return False

    def delete_record(self, note_uuid: str) -> bool:
        """
        Delete note and remove it from indexes.

        Returns:
            True if successful, False if note not found
        """
        note = self.heap.read_note(note_uuid)
        if not note:
            return False

        self._remove_from_indexes(note_uuid, note)

        return self.heap.delete_note(note_uuid)

    def get_all_records(self) -> List[Note]:
        """
        Get all notes.

        Returns:
            List of all notes
        """
        return list(map(Note.from_dict, self.heap.list_all_notes()))

    # ============================================================
    # search using indexes
    # ============================================================

    def search_by_title(self, prefix: str) -> List[Note]:
        """
        Search notes by title prefix using the index.

        Args:
            prefix: Title prefix to search for

        Returns:
            List of found notes
        """
        search_results = self.index_manager.search_by_prefix(INDEX_NOTE_TITLE, prefix)

        all_uuids: Set[str] = set()
        for uuids in search_results.values():
            all_uuids.update(uuids)

        notes = []
        for uuid in all_uuids:
            note = self.get_note_by_id(uuid)
            if note:
                notes.append(Note.from_dict(note))
        return notes

    def search_by_date(self, year: int, month: Optional[int] = None, day: Optional[int] = None) -> List[Note]:
        """
        Search notes by date using the index.

        Args:
            year: Year of the note
            month: Month of the note (optional)
            day: Day of the note (optional)

        Returns:
            List of found notes
        """
        uuids = self.index_manager.search_by_date(INDEX_NOTE_CREATION_DATE, year, month, day)

        notes = []
        for uuid in uuids:
            note = self.get_note_by_id(uuid)
            if note:
                notes.append(note)
        return notes

    def search_by_content(self, query: str) -> List[Note]:
        """
        Search notes by content (simple search, without index).

        Args:
            query: Search string

        Returns:
            List of found notes
        """
        all_notes = self.heap.list_all_notes()
        query_lower = query.lower()

        return [
            Note.from_dict(note) for note in all_notes
            if query_lower in note.get("content", "").lower()
        ]

    def search_by_tag(self, tag: str) -> List[Note]:
        """
        Search notes by tag.

        Args:
            tag: Tag to search for

        Returns:
            List of found notes
        """
        all_notes = self.heap.list_all_notes()
        tag_lower = tag.lower()

        return [
            note for note in all_notes
            if tag_lower in [t.value.lower() for t in note.tags]
        ]

    def get_notes_by_contact(self, contact_uuid: str) -> List[Note]:
        """
        Get all notes related to a contact.

        Args:
            contact_uuid: Contact UUID

        Returns:
            List of notes
        """
        all_notes = self.heap.list_all_notes()

        return [
            note for note in all_notes
            if contact_uuid in note.get('contact_ids', [])
        ]
