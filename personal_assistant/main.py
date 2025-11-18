import os
import sys
from personal_assistant.tui.app import AddressBookApp
from personal_assistant.config import AppConfig


def main():
    """Main entry point for the personal assistant application."""
    # Auto-detect mode based on installation (release) vs source (test)
    # Can be overridden via environment variable or command-line argument
    mode = os.environ.get("ASSISTANT_MODE", AppConfig.get_mode())

    # Allow override via command-line: --release or --test
    if "--release" in sys.argv:
        mode = "release"
        sys.argv.remove("--release")
    elif "--test" in sys.argv:
        mode = "test"
        sys.argv.remove("--test")

    app = AddressBookApp(mode=mode)
    app.run()


if __name__ == "__main__":
    main()

