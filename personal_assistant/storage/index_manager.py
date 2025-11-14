"""
IndexManager — indexing system for fast contact search.

Implements:
- Trie indexes for contact_first_name and contact_last_name (prefix search)
- Hash indexes for contact_phone and contact_email (exact search)
- Atomic write through atomic rename pattern
"""

import os
import json
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from threading import Lock
from personal_assistant.storage.constants import (
    INDEX_CONTACT_FIRST_NAME,
    INDEX_CONTACT_LAST_NAME,
    INDEX_CONTACT_PHONE,
    INDEX_CONTACT_EMAIL,
)


class IndexManager:
    """
    Manages all indexes for fast search.

    Index structure:
    index_store/
    ├── contact_first_name/     # Trie index (2 levels: first/second letter)
    │   ├── a/
    │   │   ├── a.json
    │   │   └── b.json
    │   └── j/
    │       └── o.json
    ├── contact_last_name/      # Trie index
    ├── contact_phone/          # Hash index (partitioned by hash)
    │   ├── a1/
    │   │   └── b2.json
    │   └── e4/
    │       └── f5.json
    └── contact_email/          # Hash index
    """

    def __init__(self, index_root: str = "index_store"):
        """
        Args:
            index_root: Root directory for all indexes
        """
        self.index_root = Path(index_root)
        self._locks: Dict[str, Lock] = {}  # locks for atomicity
        self._ensure_directories()

    def _ensure_directories(self):
        """Creates directory structure for indexes."""
        # trie indexes
        (self.index_root / INDEX_CONTACT_FIRST_NAME).mkdir(parents=True, exist_ok=True)
        (self.index_root / INDEX_CONTACT_LAST_NAME).mkdir(parents=True, exist_ok=True)

        # hash indexes
        (self.index_root / INDEX_CONTACT_PHONE).mkdir(parents=True, exist_ok=True)
        (self.index_root / INDEX_CONTACT_EMAIL).mkdir(parents=True, exist_ok=True)

    def _get_lock(self, file_path: str) -> Lock:
        """Get or create lock for file."""
        if file_path not in self._locks:
            self._locks[file_path] = Lock()
        return self._locks[file_path]

    def _atomic_write_json(self, file_path: Path, data: Dict[str, Any]):
        """
        Atomically save JSON data using atomic rename pattern.

        Args:
            file_path: Path to the file
            data: Data to save as JSON
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

    # ============================================================
    # TRIE INDEX
    # ============================================================

    def _get_trie_path(self, index_type: str, value: str) -> Optional[Path]:
        """
        Get path to file in Trie index.

        Args:
            index_type: INDEX_CONTACT_FIRST_NAME or INDEX_CONTACT_LAST_NAME
            value: Value to index (e.g., "John")

        Returns:
            Path to index file or None if value is too short
        """
        normalized = value.lower().strip()
        if len(normalized) < 2:
            # for names shorter than 2 characters use special file
            return self.index_root / index_type / "_short" / f"{normalized[0] if normalized else '_'}.json"

        first_char = normalized[0]
        second_char = normalized[1]

        first_dir = self.index_root / index_type / first_char
        first_dir.mkdir(parents=True, exist_ok=True)

        return first_dir / f"{second_char}.json"

    def _load_trie_index(self, file_path: Path) -> Dict[str, List[str]]:
        """
        Load Trie index from file.

        Returns:
            Dict[full_name -> list_of_uuids]
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            return {}

    def _save_trie_index_atomic(self, file_path: Path, data: Dict[str, List[str]]):
        """
        Atomically save Trie index (atomic rename pattern).

        Args:
            file_path: Path to index file
            data: Data to save
        """
        self._atomic_write_json(file_path, data)

    def add_to_trie_index(self, index_type: str, value: str, uuid: str):
        """
        Add record to Trie index.

        Args:
            index_type: "first_name" or "last_name"
            value: Value (e.g., "John")
            uuid: Record UUID
        """
        if not value or not value.strip():
            return

        file_path = self._get_trie_path(index_type, value)
        if not file_path:
            return

        normalized = value.lower().strip()
        lock = self._get_lock(str(file_path))

        with lock:
            index_data = self._load_trie_index(file_path)

            if normalized not in index_data:
                index_data[normalized] = []

            if uuid not in index_data[normalized]:
                index_data[normalized].append(uuid)

            self._save_trie_index_atomic(file_path, index_data)

    def remove_from_trie_index(self, index_type: str, value: str, uuid: str):
        """
        Remove record from Trie index.

        Args:
            index_type: "first_name" or "last_name"
            value: Value
            uuid: Record UUID
        """
        if not value or not value.strip():
            return

        file_path = self._get_trie_path(index_type, value)
        if not file_path or not file_path.exists():
            return

        normalized = value.lower().strip()
        lock = self._get_lock(str(file_path))

        with lock:
            index_data = self._load_trie_index(file_path)

            if normalized in index_data:
                if uuid in index_data[normalized]:
                    index_data[normalized].remove(uuid)

                if not index_data[normalized]:
                    del index_data[normalized]

            self._save_trie_index_atomic(file_path, index_data)

    def search_by_prefix(self, index_type: str, prefix: str) -> Dict[str, List[str]]:
        """
        Search by prefix in Trie index.

        Args:
            index_type: INDEX_CONTACT_FIRST_NAME or INDEX_CONTACT_LAST_NAME
            prefix: Search prefix (e.g., "Jo")

        Returns:
            Dict {value: [uuid1, uuid2, ...]}
        """
        normalized_prefix = prefix.lower().strip()
        if not normalized_prefix:
            return {}

        results = {}

        if len(normalized_prefix) < 2:
            # search in file for short names
            file_path = self.index_root / index_type / "_short" / f"{normalized_prefix[0]}.json"
            if file_path.exists():
                index_data = self._load_trie_index(file_path)
                for key, uuids in index_data.items():
                    if key.startswith(normalized_prefix):
                        results[key] = uuids

            first_char = normalized_prefix[0]
            first_dir = self.index_root / index_type / first_char
            if first_dir.exists():
                for file_path in first_dir.glob("*.json"):
                    index_data = self._load_trie_index(file_path)
                    for key, uuids in index_data.items():
                        if key.startswith(normalized_prefix):
                            results[key] = uuids
        else:
            first_char = normalized_prefix[0]
            second_char = normalized_prefix[1]

            file_path = self.index_root / index_type / first_char / f"{second_char}.json"
            if file_path.exists():
                index_data = self._load_trie_index(file_path)
                for key, uuids in index_data.items():
                    if key.startswith(normalized_prefix):
                        results[key] = uuids

        return results

    # ============================================================
    # HASH INDEX
    # ============================================================

    # def _normalize_phone(self, phone: str) -> str:
    #     """Normalize phone number."""
    #     normalized = ''.join(c for c in phone if c.isdigit() or c == '+')
    #     return normalized
    #
    # def _normalize_email(self, email: str) -> str:
    #     """Normalize email."""
    #     return email.lower().strip()

    def _get_hash_path(self, index_type: str, value: str) -> tuple[Path, str]:
        """
        Get path to file in Hash index and full hash.

        Args:
            index_type: INDEX_CONTACT_PHONE or INDEX_CONTACT_EMAIL
            value: Value to hash

        Returns:
            (Path to file, full hash)
        """
        # normalization. should be already done in the models
        # if index_type == INDEX_CONTACT_PHONE:
        #     normalized = self._normalize_phone(value)
        # else:  # email
        #     normalized = self._normalize_email(value)

        hash_obj = hashlib.sha1(value.encode('utf-8'))
        full_hash = hash_obj.hexdigest()

        bucket1 = full_hash[:2]
        bucket2 = full_hash[2:4]

        bucket_dir = self.index_root / index_type / bucket1
        bucket_dir.mkdir(parents=True, exist_ok=True)

        file_path = bucket_dir / f"{bucket2}.json"

        return file_path, full_hash

    def _load_hash_index(self, file_path: Path) -> Dict[str, List[str]]:
        """
        Load Hash index from file.

        Returns:
            Dict[full_hash -> list_of_uuids]
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            return {}

    def _save_hash_index_atomic(self, file_path: Path, data: Dict[str, List[str]]):
        """
        Atomically save Hash index (atomic rename pattern).

        Args:
            file_path: Path to index file
            data: Data to save
        """
        self._atomic_write_json(file_path, data)

    def add_to_hash_index(self, index_type: str, value: str, uuid: str):
        """
        Add record to Hash index.

        Args:
            index_type: index for hashing indexes e.g. INDEX_CONTACT_PHONE or INDEX_CONTACT_EMAIL
            value: Value to hash
            uuid: Record UUID
        """
        if not value or not value.strip():
            return

        file_path, full_hash = self._get_hash_path(index_type, value)
        lock = self._get_lock(str(file_path))

        with lock:
            index_data = self._load_hash_index(file_path)

            if full_hash not in index_data:
                index_data[full_hash] = []

            if uuid not in index_data[full_hash]:
                index_data[full_hash].append(uuid)

            self._save_hash_index_atomic(file_path, index_data)

    def remove_from_hash_index(self, index_type: str, value: str, uuid: str):
        """
        Remove record from Hash index.

        Args:
            index_type: INDEX_CONTACT_PHONE or INDEX_CONTACT_EMAIL
            value: Value
            uuid: Record UUID
        """
        if not value or not value.strip():
            return

        file_path, full_hash = self._get_hash_path(index_type, value)

        if not file_path.exists():
            return

        lock = self._get_lock(str(file_path))

        with lock:
            index_data = self._load_hash_index(file_path)

            if full_hash in index_data:
                if uuid in index_data[full_hash]:
                    index_data[full_hash].remove(uuid)

                if not index_data[full_hash]:
                    del index_data[full_hash]

            self._save_hash_index_atomic(file_path, index_data)

    def search_by_exact_match(self, index_name: str, value: str) -> List[str]:
        """
        Search a Hash index for an exact match.
        """
        if not value or not value.strip():
            return []

        file_path, full_hash = self._get_hash_path(index_name, value)

        if not file_path.exists():
            return []

        index_data = self._load_hash_index(file_path)
        return index_data.get(full_hash, [])

    # ============================================================
    # Date Index (for notes)
    # ============================================================

    def _get_date_path(self, index_name: str, date_iso: str) -> Optional[Path]:
        """
        Get path to a Date index file.
        Partitioning by year/month.
        File name is day.
        """
        try:
            year = date_iso[:4]
            month = date_iso[5:7]
            day = date_iso[8:10]
            return self.index_root / index_name / year / month / f"{day}.json"
        except (IndexError, TypeError):
            return None

    def add_to_date_index(self, index_name: str, date_iso: str, uuid: str):
        """
        Add a UUID to a Date index.
        Date should be in ISO format (YYYY-MM-DD...).
        """
        file_path = self._get_date_path(index_name, date_iso)
        if not file_path:
            return

        lock = self._get_lock(str(file_path))

        with lock:
            # in date index, the key is the day, but we store all UUIDs for that day in a list.
            # For simplicity, we'll use a structure where the file itself represents the day
            # and contains a list of UUIDs.
            data = self._read_index_file(file_path)
            if 'uuids' not in data:
                data['uuids'] = []

            if uuid not in data['uuids']:
                data['uuids'].append(uuid)
                self._write_index_file(file_path, data)

    def remove_from_date_index(self, index_name: str, date_iso: str, uuid: str):
        """
        Remove a UUID from a Date index.
        """
        file_path = self._get_date_path(index_name, date_iso)
        if not file_path or not file_path.exists():
            return

        lock = self._get_lock(str(file_path))

        with lock:
            data = self._read_index_file(file_path)
            if 'uuids' in data and uuid in data['uuids']:
                data['uuids'].remove(uuid)
                if not data['uuids']:
                    del data['uuids']
                self._write_index_file(file_path, data)

    def search_by_date(self, index_name: str, year: int, month: Optional[int] = None, day: Optional[int] = None) -> Set[str]:
        """
        Search for UUIDs by year, month, or day.
        """
        uuids = set()
        base_path = self.index_root / index_name / str(year)

        if month:
            base_path = base_path / f"{month:02d}"
        if day:
            base_path = base_path / f"{day:02d}.json"

        if day and base_path.is_file():
            data = self._read_index_file(base_path)
            uuids.update(data.get('uuids', []))
        elif not day and base_path.is_dir():
            for json_file in base_path.rglob("*.json"):
                data = self._read_index_file(json_file)
                uuids.update(data.get('uuids', []))

        return uuids

    def _read_index_file(self, file_path: Path) -> dict:
        """
        Read index file, return as dictionary.
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            return {}

    def _write_index_file(self, file_path: Path, data: dict):
        """
        Write dictionary data to index file.
        """
        self._atomic_write_json(file_path, data)

    # ============================================================
    # rebuild Indexes
    # ============================================================

    def rebuild_index_set(self, index_names: List[str]) -> None:
        """
        Clear specific indexes by removing their directories.

        Args:
            index_names: List of index names to clear (e.g., ['contact_first_name', 'contact_last_name'])
        """
        import shutil

        for index_name in index_names:
            index_path = self.index_root / index_name
            if index_path.exists():
                shutil.rmtree(index_path)
            # Recreate empty directory
            index_path.mkdir(parents=True, exist_ok=True)

