from datetime import datetime
import re
from personal_assistant.models.exceptions import (
    InvalidPhoneFormatError,
    InvalidBirthdayFormatError,
    BirthdayInFutureError,
    InvalidTitleFormatError,
    InvalidTagFormatError,
)

__all__ = ["Field", "Name", "Birthday", "Phone", "Title", "Tag"]


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise InvalidBirthdayFormatError(value)

        if birthday.date() > datetime.today().date():
            raise BirthdayInFutureError(value)
        super().__init__(birthday)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise InvalidPhoneFormatError(value)
        super().__init__(value)

    def __str__(self):
        return str(self.value)


class Title(Field):
    def __init__(self, value):
        if not value or len(value.strip()) <= 5:
            raise InvalidTitleFormatError(value)
        super().__init__(value.strip())


class Tag(Field):
    def __init__(self, value):
        if not value or len(value.strip()) <= 3:
            raise InvalidTagFormatError(value)
        
        # Check for % and special symbols (allow alphanumeric, spaces, hyphens, underscores)
        if re.search(r'[%&<>"\'/\\]', value) or not re.match(r'^[a-zA-Z0-9\s\-_]+$', value.strip()):
            raise InvalidTagFormatError(value)
        
        super().__init__(value.strip())
