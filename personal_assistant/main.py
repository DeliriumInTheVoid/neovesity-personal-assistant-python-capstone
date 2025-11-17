import os
import sys
from personal_assistant.tui.app import AddressBookApp


def main():
    """Main entry point for the personal assistant application."""
    # Determine mode: check environment variable first, then command-line argument
    mode = os.environ.get("ASSISTANT_MODE", "test")

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

