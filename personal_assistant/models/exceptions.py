class ContactBotError(Exception):
    """General exception for Contact Bot application."""
    pass

class ContactNotFoundError(ContactBotError):
    """Raised when a specific contact is not found in AddressBook."""
    pass

class PhoneNotFoundError(ContactBotError):
    """Raised when a specific phone number is not found in a Record."""
    pass

class InvalidPhoneFormatError(ValueError, ContactBotError):
    """Raised when a phone number has an invalid format."""
    def __init__(self, message: str):
        super().__init__(message)

class InvalidBirthdayFormatError(ValueError, ContactBotError):
    """Raised when a birthday has an invalid format."""
    def __init__(self, birthday: str):
        super().__init__(f"Invalid date format: '{birthday}'. Use DD.MM.YYYY.")

class BirthdayInFutureError(ValueError, ContactBotError):
    """Raised when a birthday date is set in the future."""
    def __init__(self, birthday: str):
        super().__init__(f"Birthday '{birthday}' cannot be in the future.")

class PhoneAlreadyExistsError(ContactBotError):
    """Raised when trying to add a phone number that already exists in a Record."""
    pass

class RecordAlreadyExistsError(ContactBotError):
    """Raised when trying to add a Record that already exists in AddressBook."""
    pass

class InvalidEmailFormatError(ValueError, ContactBotError):
    """Raised when trying to add an email in wrong format xxx@xxx.com"""
    def __init__(self, *args: object) -> None:
        super().__init__(f"User email should be in the right format xxx@xxx.xxx")

class InvalidTitleFormatError(ValueError, ContactBotError):
    """Raised when a title has an invalid format."""
    def __init__(self, title: str):
        super().__init__(f"Invalid title format: '{title}'. Title must be more than 5 symbols.")

class InvalidTagFormatError(ValueError, ContactBotError):
    """Raised when a tag has an invalid format."""
    def __init__(self, tag: str):
        super().__init__(f"Invalid tag format: '{tag}'. Tag must be more than 3 symbols and cannot contain % or special symbols.")

class NoteNotFoundError(ContactBotError):
    """Raised when a specific note is not found in NotesBook."""
    pass

class NoteAlreadyExistsError(ContactBotError):
    """Raised when trying to add a Note that already exists in NotesBook."""
    pass

class TagAlreadyExistsError(ContactBotError):
    """Raised when trying to add a tag that already exists in a Note."""
    pass
