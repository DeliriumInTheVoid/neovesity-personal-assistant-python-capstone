"""
HeapStorage — file-based storage for contacts and notes.

Each record is stored in a separate JSON file named with its UUID.
Structure:
data/
├── contacts/
│   ├── 1a6f334a-601a-4e2a-b0f3-9b8f2c6a0b1d.json
│   └── ...
└── notes/
    ├── 3c1a...d3f.json
    └── ...
"""

import os
import json
import uuid
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class HeapStorage:
    """
    File-based data storage (Heap).

    Each record is a separate JSON file with UUID as the filename.
    """

    def __init__(self, data_root: str = "data"):
        """
        Args:
            data_root: Root directory for data
        """
        self.data_root = Path(data_root)
        self._ensure_directories()

    def _ensure_directories(self):
        """Creates directory structure for storage."""
        (self.data_root / "contacts").mkdir(parents=True, exist_ok=True)
        (self.data_root / "notes").mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, entity_type: str, entity_uuid: str) -> Path:
        """
        Get path to a record file.

        Args:
            entity_type: "contacts" or "notes"
            entity_uuid: UUID of the record

        Returns:
            Path to the file
        """
        return self.data_root / entity_type / f"{entity_uuid}.json"

    def _save_atomic(self, file_path: Path, data: Dict[str, Any]):
        """
        Atomically save data (atomic rename pattern).

        Args:
            file_path: Path to the file
            data: Data to save
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix='.tmp_',
            suffix='.json'
        )

        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            os.replace(tmp_path, file_path)
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise e

    def _load(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load data from file.

        Returns:
            Dict with data or None if file doesn't exist or is corrupted
        """
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            return None

    # ============================================================
    # CRUD operations for contacts
    # ============================================================

    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new contact.

        Args:
            contact_data: Contact data (without uuid, it will be generated)

        Returns:
            Full contact data including generated UUID and timestamps
        """

        contact_uuid = str(uuid.uuid4())

        contact_data['uuid'] = contact_uuid
        contact_data['created_at'] = datetime.now().isoformat()
        contact_data['updated_at'] = datetime.now().isoformat()

        file_path = self._get_file_path("contacts", contact_uuid)
        self._save_atomic(file_path, contact_data)

        return contact_data

    def read_contact(self, contact_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Read contact by UUID.

        Returns:
            Dict with contact data or None
        """
        file_path = self._get_file_path("contacts", contact_uuid)
        return self._load(file_path)

    def update_contact(self, contact_uuid: str, contact_data: Dict[str, Any]) -> bool:
        """
        Update existing contact.

        Args:
            contact_uuid: Contact UUID
            contact_data: New data (uuid is ignored)

        Returns:
            True if successful, False if contact not found
        """
        file_path = self._get_file_path("contacts", contact_uuid)

        if not file_path.exists():
            return False

        existing = self._load(file_path)
        contact_data = self._add_metadata(existing, contact_data)
        # contact_data['uuid'] = contact_uuid
        # contact_data['created_at'] = existing.get('created_at', datetime.now().isoformat())
        # contact_data['updated_at'] = datetime.now().isoformat()
        #
        self._save_atomic(file_path, contact_data)
        return True

    def delete_contact(self, contact_uuid: str) -> bool:
        """
        Delete contact.

        Returns:
            True if successful, False if contact not found
        """
        file_path = self._get_file_path("contacts", contact_uuid)

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except OSError:
            return False

    def list_all_contacts(self) -> List[Dict[str, Any]]:
        """
        Get all contacts.

        Returns:
            List of all contacts
        """
        return self.list_all("contacts")

    def list_all(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all entities of a given type.

        Args:
            entity_type: "contacts" or "notes"

        Returns:
            List of all entities
        """
        entity_dir = self.data_root / entity_type
        entities = []

        if not entity_dir.exists():
            return entities

        for file_path in entity_dir.glob("*.json"):
            # ignore macOS hidden files and temp files
            if file_path.name.startswith('.'):
                continue

            entity = self._load(file_path)
            if entity:
                entities.append(entity)

        return entities

    # ============================================================
    # CRUD operations for notes
    # ============================================================

    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new note.

        Args:
            note_data: Note data (without uuid)

        Returns:
            Full note data including generated UUID and timestamps
        """
        note_uuid = str(uuid.uuid4())

        note_data['uuid'] = note_uuid
        if 'created_at' not in note_data:
            note_data['created_at'] = datetime.now().isoformat()
        note_data['updated_at'] = datetime.now().isoformat()

        file_path = self._get_file_path("notes", note_uuid)
        self._save_atomic(file_path, note_data)

        return note_data

    def read_note(self, note_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Read note by UUID.

        Returns:
            Dict with note data or None
        """
        file_path = self._get_file_path("notes", note_uuid)
        return self._load(file_path)

    def update_note(self, note_uuid: str, note_data: Dict[str, Any]) -> bool:
        """
        Update existing note.

        Args:
            note_uuid: Note UUID
            note_data: New data

        Returns:
            True if successful, False if note not found
        """
        file_path = self._get_file_path("notes", note_uuid)

        if not file_path.exists():
            return False


        existing = self._load(file_path)
        note_data = self._add_metadata(existing, note_data)
        # existing = self._load(file_path)
        # note_data['uuid'] = note_uuid
        # note_data['created_at'] = existing.get('created_at', datetime.now().isoformat())
        # note_data['updated_at'] = datetime.now().isoformat()

        self._save_atomic(file_path, note_data)
        return True

    def delete_note(self, note_uuid: str) -> bool:
        """
        Delete note.

        Returns:
            True if successful, False if note not found
        """
        file_path = self._get_file_path("notes", note_uuid)

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except OSError:
            return False

    def list_all_notes(self) -> List[Dict[str, Any]]:
        """
        Get all notes.

        Returns:
            List of all notes
        """
        return self.list_all("notes")

    def _add_metadata(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preserve UUID and creation timestamp in new data.

        Args:
            existing: Existing record data
            new_data: New record data

        Returns:
            Merged data with preserved fields
        """
        new_data['uuid'] = existing.get('uuid')
        new_data['created_at'] = existing.get('created_at', datetime.now().isoformat())
        new_data['updated_at'] = datetime.now().isoformat()
        return new_data