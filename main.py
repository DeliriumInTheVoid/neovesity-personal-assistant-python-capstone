"""
Module for managing a simple address book.

Provides classes for contact fields, individual contact records,
and an address book that stores multiple records.
"""

from personal_assistant.tui.app import AddressBookApp

if __name__ == "__main__":
    app = AddressBookApp()
    app.run()
