"""
Constants for storage indexes.

This module contains all index names used in the storage system.
Using constants instead of string literals makes it easier to:
- Avoid typos
- Rename indexes in the future
- Maintain consistency across the codebase
"""

INDEX_CONTACT_FIRST_NAME = "contact_first_name"
INDEX_CONTACT_LAST_NAME = "contact_last_name"
INDEX_CONTACT_PHONE = "contact_phone"
INDEX_CONTACT_EMAIL = "contact_email"

INDEX_NOTE_TITLE = "note_title"
INDEX_NOTE_TAG = "note_tag"
INDEX_NOTE_CREATION_DATE = "note_creation_date"

CONTACT_INDEXES = [
    INDEX_CONTACT_FIRST_NAME,
    INDEX_CONTACT_LAST_NAME,
    INDEX_CONTACT_PHONE,
    INDEX_CONTACT_EMAIL,
]

NOTE_INDEXES = [
    INDEX_NOTE_TITLE,
    INDEX_NOTE_TAG,
    INDEX_NOTE_CREATION_DATE,
]

ALL_INDEXES = CONTACT_INDEXES + NOTE_INDEXES

