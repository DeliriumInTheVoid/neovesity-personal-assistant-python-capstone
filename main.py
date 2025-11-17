"""
Module for managing a simple address book.

Provides classes for contact fields, individual contact records,
and an address book that stores multiple records.
"""

import os
import sys
from personal_assistant.tui.app import AddressBookApp

if __name__ == "__main__":
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
