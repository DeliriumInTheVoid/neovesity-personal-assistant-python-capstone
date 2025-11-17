"""
Storage package — File-based storage system for Personal Assistant application.

This package provides a file-based storage system with indexing capabilities:
- heap_storage: Base file storage (Heap)
- index_manager: Index management for fast search
- base_storage: Abstract base class for storage with indexing
- address_book: High-level API for address book
- notes_storage: High-level API for notes management
- constants: Index name constants
"""

from personal_assistant.storage.heap_storage import HeapStorage
from personal_assistant.storage.index_manager import IndexManager
from personal_assistant.storage.base_storage import BaseStorage
from personal_assistant.storage.address_book import AddressBookStorage
from personal_assistant.storage.notes_storage import NotesStorage
from personal_assistant.storage.constants import (
    INDEX_CONTACT_FIRST_NAME,
    INDEX_CONTACT_LAST_NAME,
    INDEX_CONTACT_PHONE,
    INDEX_CONTACT_EMAIL,
    INDEX_NOTE_TITLE,
    INDEX_NOTE_CREATION_DATE,
    CONTACT_INDEXES,
    NOTE_INDEXES,
    ALL_INDEXES,
)


__all__ = [
    'HeapStorage',
    'IndexManager',
    'BaseStorage',
    'AddressBookStorage',
    'NotesStorage',
    # Index constants
    'INDEX_CONTACT_FIRST_NAME',
    'INDEX_CONTACT_LAST_NAME',
    'INDEX_CONTACT_PHONE',
    'INDEX_CONTACT_EMAIL',
    'INDEX_NOTE_TITLE',
    'INDEX_NOTE_CREATION_DATE',
    'CONTACT_INDEXES',
    'NOTE_INDEXES',
    'ALL_INDEXES',
]

