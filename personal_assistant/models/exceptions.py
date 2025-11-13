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
    def __init__(self, phone: str):
        super().__init__(f"Invalid phone format: '{phone}'. Phone must be 10 digits.")

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