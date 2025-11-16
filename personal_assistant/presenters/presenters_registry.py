from typing import Dict
from personal_assistant.storage.address_book import AddressBookStorage
from personal_assistant.storage.notes_storage import NotesStorage
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.presenters import (
    HelloPresenter,
    AddContactPresenter,
    ChangeContactPresenter,
    ShowPhonePresenter,
    ShowAllContactsPresenter,
    AddBirthdayPresenter,
    ShowBirthdayPresenter,
    ShowUpcomingBirthdaysPresenter,
    SearchContactsPresenter,
    AddNotePresenter,
    SearchNotesPresenter,
    ShowAllNotesPresenter,
    ShowHelpPresenter,
)


class PresentersRegistry:
    def __init__(self, address_book_storage: AddressBookStorage, notes_storage: NotesStorage):
        self.commands: Dict[str, Presenter] = {}

        # delete-contact {first_name} {user last_name}
        # delete-note {note title}
        # change-note
        # search note-tags
        # search by phone number

        self.commands['hello'] = HelloPresenter()                                           #
        self.commands['add-contact'] = AddContactPresenter(address_book_storage)            #
        self.commands['change-contact'] = ChangeContactPresenter(address_book_storage)      #   # email: change, delete, add, # phone: change delete, add, # birthday: change, delete
        self.commands['phone'] = ShowPhonePresenter(address_book_storage)                   #
        self.commands['all'] = ShowAllContactsPresenter(address_book_storage)               #
        #self.commands['add-birthday'] = AddBirthdayPresenter(address_book_storage) # no need to use directly will be used in change-contact
        self.commands['show-birthday'] = ShowBirthdayPresenter(address_book_storage)        #
        self.commands['birthdays'] = ShowUpcomingBirthdaysPresenter(address_book_storage)   #
        self.commands['search'] = SearchContactsPresenter(address_book_storage)             #
        self.commands['add-note'] = AddNotePresenter(notes_storage)                         #
        self.commands['search-notes'] = SearchNotesPresenter(notes_storage)                 #
        self.commands['all-notes'] = ShowAllNotesPresenter(notes_storage)                   #

        self.commands['help'] = ShowHelpPresenter(self.commands)

    def get(self, command_name: str) -> Presenter:
        return self.commands.get(command_name)

    def list_all(self) -> Dict[str, Presenter]:
        return self.commands

