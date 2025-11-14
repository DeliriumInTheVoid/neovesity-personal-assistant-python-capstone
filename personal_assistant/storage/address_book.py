"""
AddressBookStorage — high-level API for working with contacts.

Combines HeapStorage (file storage) and IndexManager (indexes for search).
Ensures consistency between data and indexes.
"""

from typing import Dict, Any, Optional, List
from personal_assistant.storage.base_storage import BaseStorage
from personal_assistant.storage.constants import (
    INDEX_CONTACT_FIRST_NAME,
    INDEX_CONTACT_LAST_NAME,
    INDEX_CONTACT_PHONE,
    INDEX_CONTACT_EMAIL,
    CONTACT_INDEXES,
)


class AddressBookStorage(BaseStorage):
    """
    High-level API for managing contacts.

    Automatically maintains synchronization between:
    - Heap (file-based data storage)
    - Indexes (for fast search)
    """

    # ============================================================
    # Overrides from BaseStorage
    # ============================================================
    def _get_entity_type(self) -> str:
        """Get the entity type for contacts."""
        return "contacts"

    def _get_entity_indexes(self) -> List[str]:
        """Get list of all contact indexes."""
        return CONTACT_INDEXES

    # ============================================================
    # CRUD operations
    # ============================================================

    def add_contact(self, first_name: str, last_name: str = "",
                    phones: List[str] = None, emails: List[str] = None,
                    note_ids: List[str] = None, **extra_fields) -> str:
        """
        Add a new contact.

        Args:
            first_name: First name (required)
            last_name: Last name
            phones: List of phone numbers
            emails: List of email addresses
            note_ids: List of note UUIDs
            **extra_fields: Additional fields (birthday, address, etc.)

        Returns:
            UUID of created contact
        """
        if phones is None:
            phones = []
        if emails is None:
            emails = []
        if note_ids is None:
            note_ids = []

        contact_data = {
            'first_name': first_name,
            'last_name': last_name,
            'phones': phones,
            'emails': emails,
            'note_ids': note_ids,
            **extra_fields
        }

        created_contact = self.heap.create_contact(contact_data)
        contact_uuid = created_contact['uuid']

        self._add_to_indexes(contact_uuid, created_contact)

        return contact_uuid

    def get_contact(self, contact_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get contact by UUID.

        Returns:
            Dict with contact data or None
        """
        return self.heap.read_contact(contact_uuid)

    def update_contact(self, contact_uuid: str, first_name: str = None,
                       last_name: str = None, phones: List[str] = None,
                       emails: List[str] = None, note_ids: List[str] = None,
                       **extra_fields) -> bool:
        """
        Update contact.

        Args:
            contact_uuid: Contact UUID
            first_name: New first name (None = don't change)
            last_name: New last name (None = don't change)
            phones: New list of phones (None = don't change)
            emails: New list of emails (None = don't change)
            note_ids: New list of notes (None = don't change)
            **extra_fields: Additional fields

        Returns:
            True if successful, False if contact not found
        """

        old_contact = self.heap.read_contact(contact_uuid)
        if not old_contact:
            return False

        self._remove_from_indexes(contact_uuid, old_contact)

        new_contact = old_contact.copy()
        if first_name is not None:
            new_contact['first_name'] = first_name
        if last_name is not None:
            new_contact['last_name'] = last_name
        if phones is not None:
            new_contact['phones'] = phones
        if emails is not None:
            new_contact['emails'] = emails
        if note_ids is not None:
            new_contact['note_ids'] = note_ids

        new_contact.update(extra_fields)

        success = self.heap.update_contact(contact_uuid, new_contact)

        if success:
            self._add_to_indexes(contact_uuid, new_contact)

        return success

    def remove_contact(self, contact_uuid: str) -> bool:
        """
        Delete contact.

        Returns:
            True if successful, False if contact not found
        """
        contact = self.heap.read_contact(contact_uuid)
        if not contact:
            return False

        self._remove_from_indexes(contact_uuid, contact)

        return self.heap.delete_contact(contact_uuid)

    def list_contacts(self) -> List[Dict[str, Any]]:
        """
        Get all contacts.

        Returns:
            List of all contacts
        """
        return self.heap.list_all_contacts()

    # ============================================================
    # Search
    # ============================================================

    def search_by_first_name(self, prefix: str) -> List[Dict[str, Any]]:
        """
        Search contacts by first name prefix.

        Args:
            prefix: Prefix to search for (e.g., "Jo")

        Returns:
            List of found contacts
        """
        results = self.index_manager.search_by_prefix(INDEX_CONTACT_FIRST_NAME, prefix)

        contacts = []
        for name, uuids in results.items():
            for uuid in uuids:
                contact = self.heap.read_contact(uuid)
                if contact:
                    contacts.append(contact)

        return contacts

    def search_by_last_name(self, prefix: str) -> List[Dict[str, Any]]:
        """
        Search contacts by last name prefix.

        Args:
            prefix: Last name prefix to search for

        Returns:
            List of found contacts
        """
        results = self.index_manager.search_by_prefix(INDEX_CONTACT_LAST_NAME, prefix)

        contacts = []
        for name, uuids in results.items():
            for uuid in uuids:
                contact = self.heap.read_contact(uuid)
                if contact:
                    contacts.append(contact)

        return contacts

    def search_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """
        Exact search for contacts by phone.

        Args:
            phone: Phone number (will be normalized)

        Returns:
            List of found contacts
        """
        uuids = self.index_manager.search_by_exact_match(INDEX_CONTACT_PHONE, phone)

        contacts = []
        for uuid in uuids:
            contact = self.heap.read_contact(uuid)
            if contact:
                contacts.append(contact)

        return contacts

    def search_by_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Exact search for contacts by email.

        Args:
            email: Email address (will be normalized)

        Returns:
            List of found contacts
        """
        uuids = self.index_manager.search_by_exact_match(INDEX_CONTACT_EMAIL, email)

        contacts = []
        for uuid in uuids:
            contact = self.heap.read_contact(uuid)
            if contact:
                contacts.append(contact)

        return contacts

    # ============================================================
    # index synchronization
    # ============================================================

    def _add_to_indexes(self, contact_uuid: str, contact_data: Dict[str, Any]):
        """Add contact to all indexes."""

        if contact_data.get('first_name'):
            self.index_manager.add_to_trie_index(INDEX_CONTACT_FIRST_NAME, contact_data['first_name'], contact_uuid)

        if contact_data.get('last_name'):
            self.index_manager.add_to_trie_index(INDEX_CONTACT_LAST_NAME, contact_data['last_name'], contact_uuid)

        for phone in contact_data.get('phones', []):
            self.index_manager.add_to_hash_index(INDEX_CONTACT_PHONE, phone, contact_uuid)

        for email in contact_data.get('emails', []):
            self.index_manager.add_to_hash_index(INDEX_CONTACT_EMAIL, email, contact_uuid)

    def _remove_from_indexes(self, contact_uuid: str, contact_data: Dict[str, Any]):
        """Remove contact from all indexes."""
        if contact_data.get('first_name'):
            self.index_manager.remove_from_trie_index(INDEX_CONTACT_FIRST_NAME, contact_data['first_name'], contact_uuid)

        if contact_data.get('last_name'):
            self.index_manager.remove_from_trie_index(INDEX_CONTACT_LAST_NAME, contact_data['last_name'], contact_uuid)

        for phone in contact_data.get('phones', []):
            self.index_manager.remove_from_hash_index(INDEX_CONTACT_PHONE, phone, contact_uuid)

        for email in contact_data.get('emails', []):
            self.index_manager.remove_from_hash_index(INDEX_CONTACT_EMAIL, email, contact_uuid)
