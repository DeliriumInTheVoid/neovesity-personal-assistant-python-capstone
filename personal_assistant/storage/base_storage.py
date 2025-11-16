"""
BaseStorage — abstract base class for storage with indexing.

Provides common functionality for managing entities (contacts, notes, etc.)
with automatic index synchronization.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from personal_assistant.storage.heap_storage import HeapStorage
from personal_assistant.storage.index_manager import IndexManager


class BaseStorage(ABC):
    """
    Abstract base class for storage with indexing.

    Provides:
    - Common CRUD operations pattern
    - Index synchronization helpers
    - Consistent API for derived classes
    """

    def __init__(self, data_root: str = "demo_data", index_root: str = "demo_index"):
        """
        Args:
            data_root: Directory for storing data
            index_root: Directory for storing indexes
        """
        self.heap = HeapStorage(data_root)
        self.index_manager = IndexManager(index_root)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """
        Create directories for all indexes returned by _get_entity_indexes.
        """
        for index_name in self._get_entity_indexes():
            (self.index_manager.index_root / index_name).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _add_to_indexes(self, entity_uuid: str, entity_data: Dict[str, Any]):
        """
        Add entity to all relevant indexes.

        Args:
            entity_uuid: Entity UUID
            entity_data: Entity data
        """
        pass

    @abstractmethod
    def _remove_from_indexes(self, entity_uuid: str, entity_data: Dict[str, Any]):
        """
        Remove entity from all relevant indexes.

        Args:
            entity_uuid: Entity UUID
            entity_data: Entity data
        """
        pass

    @abstractmethod
    def _get_entity_indexes(self) -> List[str]:
        """
        Get list of all indexes used by this storage.

        Returns:
            List of index names
        """
        pass

    @abstractmethod
    def _get_entity_type(self) -> str:
        """
        Get the entity type string (e.g., "contacts", "notes").

        Returns:
            Entity type string
        """
        pass

    def rebuild_indexes(self) -> int:
        """
        Rebuild all indexes from scratch.

        This method:
        1. Clears all indexes
        2. Reads all entities from storage
        3. Rebuilds indexes for all entities

        Returns:
            Number of entities reindexed
        """
        self.index_manager.rebuild_index_set(self._get_entity_indexes())

        all_entities = self._list_all_entities()

        for entity in all_entities:
            entity_uuid = entity.get('uuid')
            if entity_uuid:
                self._add_to_indexes(entity_uuid, entity)

        return len(all_entities)

    def _list_all_entities(self) -> List[Dict[str, Any]]:
        """
        Get all entities from heap storage.

        Returns:
            List of all entities
        """
        return self.heap.list_all(self._get_entity_type())
