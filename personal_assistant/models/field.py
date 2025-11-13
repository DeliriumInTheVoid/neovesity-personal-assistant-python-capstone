from datetime import datetime
import re
from personal_assistant.models.exceptions import (
    InvalidPhoneFormatError,
    InvalidBirthdayFormatError,
    BirthdayInFutureError,
    InvalidEmailFormatError
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
        normalized = self.normalize_ua_phone(value)
        if normalized is None:
            raise InvalidPhoneFormatError(f"Invalid phone number: {value}")
        super().__init__(normalized)
        
    @staticmethod                       
    def normalize_ua_phone(phone: str) -> str | None:
        digits = re.sub(r"\D", "", phone)

        UA_CODES = {
            "039", "050", "063", "066", "067", "068",
            "091", "092", "093", "094",
            "095", "096", "097", "098", "099"
        }

        # Case 1: 380XXXXXXXXX
        if digits.startswith("380") and len(digits) == 12:
            code = digits[3:6]
            if code in UA_CODES:
                return f"+{digits}"
            return None

        # Case 2: 0XXXXXXXXX
        if digits.startswith("0") and len(digits) == 10:
            code = digits[1:4]
            if code in UA_CODES:
                return "+38" + digits
            return None

        # Case 3: 80XXXXXXXXX
        if digits.startswith("80") and len(digits) == 11:
            code = digits[2:5]
            if code in UA_CODES:
                return "+3" + digits
            return None

        # Case 4: 9 digits only
        if len(digits) == 9:
            code = digits[0:3]
            if code in UA_CODES:
                return "+380" + digits
            return None

        return None
    
    def __str__(self):
        return str(self.value)
    

class Email(Field):
    EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    def __init__(self, value: str):
        if not re.fullmatch(self.EMAIL_PATTERN, value):
            raise InvalidEmailFormatError(value)
        super().__init__(value)



