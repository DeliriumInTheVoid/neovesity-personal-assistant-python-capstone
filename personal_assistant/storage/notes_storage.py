"""
NotesStorage — high-level API for working with notes.

Uses HeapStorage for file storage and IndexManager for fast search.
"""

from typing import Dict, Any, Optional, List, Set
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
        if 'title' in note_data:
            self.index_manager.add_to_trie_index(INDEX_NOTE_TITLE, note_data['title'], note_uuid)

        if 'created_at' in note_data:
            self.index_manager.add_to_date_index(INDEX_NOTE_CREATION_DATE, note_data['created_at'], note_uuid)

    def _remove_from_indexes(self, note_uuid: str, note_data: Dict[str, Any]):
        """Remove note from all indexes."""
        if 'title' in note_data:
            self.index_manager.remove_from_trie_index(INDEX_NOTE_TITLE, note_data['title'], note_uuid)

        if 'created_at' in note_data:
            self.index_manager.remove_from_date_index(INDEX_NOTE_CREATION_DATE, note_data['created_at'], note_uuid)

    # ============================================================
    # CRUD operations with indexing
    # ============================================================

    def add_note(self, title: str, content: str, tags: List[str] = None,
                 contact_ids: List[str] = None, **extra_fields) -> str:
        """
        Add a new note and update indexes.

        Args:
            title: Note title
            content: Note content
            tags: List of tags
            contact_ids: List of UUIDs of related contacts
            **extra_fields: Additional fields

        Returns:
            UUID of created note
        """
        if tags is None:
            tags = []
        if contact_ids is None:
            contact_ids = []

        note_data = {
            'title': title,
            'content': content,
            'tags': tags,
            'contact_ids': contact_ids,
            **extra_fields
        }

        created_note = self.heap.create_note(note_data)
        note_uuid = created_note['uuid']

        self._add_to_indexes(note_uuid, created_note)

        return note_uuid

    def get_note(self, note_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get note by UUID.

        Returns:
            Dict with note data or None
        """
        return self.heap.read_note(note_uuid)

    def update_note(self, note_uuid: str, title: str = None, content: str = None,
                    tags: List[str] = None, contact_ids: List[str] = None,
                    **extra_fields) -> bool:
        """
        Update note and its indexes.

        Args:
            note_uuid: Note UUID
            title: New title (None = don't change)
            content: New content (None = don't change)
            tags: New tags (None = don't change)
            contact_ids: New contact links (None = don't change)
            **extra_fields: Additional fields

        Returns:
            True if successful, False if note not found
        """
        old_note = self.heap.read_note(note_uuid)
        if not old_note:
            return False

        new_note = old_note.copy()
        if title is not None:
            new_note['title'] = title
        if content is not None:
            new_note['content'] = content
        if tags is not None:
            new_note['tags'] = tags
        if contact_ids is not None:
            new_note['contact_ids'] = contact_ids
        new_note.update(extra_fields)

        old_title = old_note.get('title')
        new_title = new_note.get('title')
        if old_title != new_title:
            if old_title:
                self.index_manager.remove_from_trie_index(INDEX_NOTE_TITLE, old_title, note_uuid)
            if new_title:
                self.index_manager.add_to_trie_index(INDEX_NOTE_TITLE, new_title, note_uuid)

        if self.heap.update_note(note_uuid, new_note):
            return True
        return False

    def delete_note(self, note_uuid: str) -> bool:
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

    def list_notes(self) -> List[Dict[str, Any]]:
        """
        Get all notes.

        Returns:
            List of all notes
        """
        return self.heap.list_all_notes()

    # ============================================================
    # search using indexes
    # ============================================================

    def search_by_title(self, prefix: str) -> List[Dict[str, Any]]:
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
            note = self.get_note(uuid)
            if note:
                notes.append(note)
        return notes

    def search_by_date(self, year: int, month: Optional[int] = None, day: Optional[int] = None) -> List[Dict[str, Any]]:
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
            note = self.get_note(uuid)
            if note:
                notes.append(note)
        return notes

    def search_by_content(self, query: str) -> List[Dict[str, Any]]:
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
            note for note in all_notes
            if query_lower in note.get('content', '').lower()
        ]

    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
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
            if tag_lower in [t.lower() for t in note.get('tags', [])]
        ]

    def get_notes_by_contact(self, contact_uuid: str) -> List[Dict[str, Any]]:
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
