from datetime import datetime
from personal_assistant.models.exceptions import (
    InvalidPhoneFormatError,
    InvalidBirthdayFormatError,
    BirthdayInFutureError,
)

__all__ = ["Field", "Name", "Birthday", "Phone"]


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
