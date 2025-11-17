"""
Configuration module for the personal assistant application.

Manages storage paths based on application mode (test or release).
"""

from pathlib import Path
from typing import Tuple


class AppConfig:
    """
    Application configuration manager.

    Handles storage paths for different modes:
    - Test mode: uses demo_data/ and demo_index/ in the project directory
    - Release mode: uses ~/.assistant/data and ~/.assistant/index in user's home directory
    """

    _mode = "test"  # Default mode

    @classmethod
    def set_mode(cls, mode: str) -> None:
        """
        Set the application mode.

        Args:
            mode: "test" or "release"

        Raises:
            ValueError: if mode is not "test" or "release"
        """
        if mode not in ("test", "release"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'test' or 'release'")
        cls._mode = mode

    @classmethod
    def get_mode(cls) -> str:
        """
        Get the current application mode.

        Returns:
            Current mode ("test" or "release")
        """
        return cls._mode

    @classmethod
    def is_release_mode(cls) -> bool:
        """
        Check if the application is in release mode.

        Returns:
            True if in release mode, False otherwise
        """
        return cls._mode == "release"

    @classmethod
    def is_test_mode(cls) -> bool:
        """
        Check if the application is in test mode.

        Returns:
            True if in test mode, False otherwise
        """
        return cls._mode == "test"

    @classmethod
    def get_storage_paths(cls) -> Tuple[str, str]:
        """
        Get the storage paths for the current mode.

        Returns:
            Tuple of (data_path, index_path)
        """
        if cls._mode == "release":
            home = Path.home()
            assistant_dir = home / ".assistant"
            data_path = str(assistant_dir / "data")
            index_path = str(assistant_dir / "index")

            # Ensure directories exist in release mode
            assistant_dir.mkdir(exist_ok=True)
            Path(data_path).mkdir(parents=True, exist_ok=True)
            Path(index_path).mkdir(parents=True, exist_ok=True)

            return data_path, index_path
        else:
            # Test mode: use demo directories in project root
            return "demo_data", "demo_index"

    @classmethod
    def get_data_path(cls) -> str:
        """
        Get the data storage path for the current mode.

        Returns:
            Data storage path
        """
        return cls.get_storage_paths()[0]

    @classmethod
    def get_index_path(cls) -> str:
        """
        Get the index storage path for the current mode.

        Returns:
            Index storage path
        """
        return cls.get_storage_paths()[1]

