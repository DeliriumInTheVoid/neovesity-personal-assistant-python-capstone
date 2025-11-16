"""
AddressBookStorage — high-level API for working with contacts.

Combines HeapStorage (file storage) and IndexManager (indexes for search).
Ensures consistency between data and indexes.
"""

from typing import Optional, List, Dict, Any
from personal_assistant.models.record import Record
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

    def add_record(self, record: Record) -> str:
        """
        Add a new contact.

        Args:
            record: contact record

        Returns:
            UUID of created contact
        """

        new_record = self.heap.create_contact(record.to_dict())
        self._add_to_indexes(new_record.get("uuid"), new_record)

        return record.uuid

    def get_record_by_id(self, contact_uuid: str) -> Optional[Record]:
        """
        Get contact by UUID.

        Returns:
            Record or None
        """
        return self.heap.read_contact(contact_uuid)

    def update_record(self, record: Record) -> bool:
        """
        Update contact.

        Args:
            record: contact record

        Returns:
            True if successful, False if contact not found
        """

        old_contact = self.heap.read_contact(record.uuid)
        if not old_contact:
            return False

        self._remove_from_indexes(record.uuid, old_contact)

        raw_record = record.to_dict()
        if self.heap.update_contact(record.uuid, raw_record):
            self._add_to_indexes(record.uuid, raw_record)
            return True


        return False

    def delete_record(self, contact_uuid: str) -> bool:
        """
        Delete contact.

        Returns:
            True if successful, False if contact not found
        """
        record = self.heap.read_contact(contact_uuid)
        if not record:
            return False

        self._remove_from_indexes(contact_uuid, record)

        return self.heap.delete_contact(contact_uuid)

    def get_all_records(self) -> List[Record]:
        """
        Get all contacts.

        Returns:a;;
            List of all contacts
        """
        return list(map(lambda record_data: Record.from_dict(record_data),  self.heap.list_all_contacts()))

    # ============================================================
    # Search
    # ============================================================

    def search_by_first_name(self, prefix: str) -> List[Record]:
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
                    contacts.append(Record.from_dict(contact))

        return contacts

    def search_by_last_name(self, prefix: str) -> List[Record]:
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
                    contacts.append(Record.from_dict(contact))

        return contacts

    def search_by_phone(self, phone: str) -> List[Record]:
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
                contacts.append(Record.from_dict(contact))

        return contacts

    def search_by_email(self, email: str) -> List[Record]:
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
                contacts.append(Record.from_dict(contact))

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

        # for email in contact_data.get('emails', []):
        #     self.index_manager.add_to_hash_index(INDEX_CONTACT_EMAIL, email, contact_uuid)
        if contact_data.get('email'):
            self.index_manager.add_to_hash_index(INDEX_CONTACT_EMAIL, contact_data['email'], contact_uuid)


    def _remove_from_indexes(self, contact_uuid: str, contact_data: Dict[str, Any]):
        """Remove contact from all indexes."""
        if contact_data.get('first_name'):
            self.index_manager.remove_from_trie_index(INDEX_CONTACT_FIRST_NAME, contact_data['first_name'], contact_uuid)

        if contact_data.get('last_name'):
            self.index_manager.remove_from_trie_index(INDEX_CONTACT_LAST_NAME, contact_data['last_name'], contact_uuid)

        for phone in contact_data.get('phones', []):
            self.index_manager.remove_from_hash_index(INDEX_CONTACT_PHONE, phone, contact_uuid)

        if contact_data.get('email'):
            self.index_manager.remove_from_hash_index(INDEX_CONTACT_EMAIL, contact_data['email'], contact_uuid)
        # for email in contact_data.get('emails', []):
        #     self.index_manager.remove_from_hash_index(INDEX_CONTACT_EMAIL, email, contact_uuid)
