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
    ShowBirthdayPresenter,
    ShowUpcomingBirthdaysPresenter,
    SearchContactsPresenter,
    SearchContactsByPhonePresenter,
    SearchContactsByEmailPresenter,
    AddNotePresenter,
    SearchNotesPresenter,
    SearchNotesByTagPresenter,
    ShowAllNotesPresenter,
    ShowHelpPresenter,
    GenerateDataPresenter,
    ChangeNotePresenter,
    DeleteContactPresenter,
    DeleteNotePresenter
)


class PresentersRegistry:
    def __init__(self, address_book_storage: AddressBookStorage, notes_storage: NotesStorage):
        self.commands: Dict[str, Presenter] = {}

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
        self.commands['search-phone'] = SearchContactsByPhonePresenter(address_book_storage) #
        self.commands['search-email'] = SearchContactsByEmailPresenter(address_book_storage) #
        self.commands['add-note'] = AddNotePresenter(notes_storage)                         #
        self.commands['change-note'] = ChangeNotePresenter(notes_storage)      #
        self.commands['search-notes'] = SearchNotesPresenter(notes_storage)                 #
        self.commands['search-tag'] = SearchNotesByTagPresenter(notes_storage)              #
        self.commands['delete-contact'] = DeleteContactPresenter(address_book_storage)      #
        self.commands['delete-note'] = DeleteNotePresenter(notes_storage)                   #
        self.commands['all-notes'] = ShowAllNotesPresenter(notes_storage)                   #
        self.commands['generate-data'] = GenerateDataPresenter(address_book_storage, notes_storage) #

        self.commands['help'] = ShowHelpPresenter(self.commands)

    def get(self, command_name: str) -> Presenter:
        return self.commands.get(command_name)

    def list_all(self) -> Dict[str, Presenter]:
        return self.commands

