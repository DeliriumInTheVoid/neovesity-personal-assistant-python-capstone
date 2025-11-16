from datetime import datetime
import re
from personal_assistant.models.exceptions import (
    InvalidPhoneFormatError,
    InvalidBirthdayFormatError,
    BirthdayInFutureError,
    InvalidEmailFormatError,
    InvalidTitleFormatError,
    InvalidTagFormatError,
)

__all__ = ["Field", "Name", "Birthday", "Phone", "Title", "Tag", "Email", "Address"]


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
        # Remove extension part (x1234, ext1234, etc.) before processing
        phone_without_ext = re.split(r'[x]|ext', phone.lower())[0]

        # Extract only digits
        digits = re.sub(r"\D", "", phone_without_ext)

        # If empty after extraction, invalid
        if not digits:
            return None

        # Remove international dialing prefix '00' if present
        if digits.startswith("00"):
            digits = digits[2:]

        # First, check if it's already a valid MSISDN format (E.164)
        # MSISDN should be: country code (1-3 digits) + national number (10-15 digits total)
        if 10 <= len(digits) <= 15 and digits[0] != '0':
            # Looks like it's already in international MSISDN format
            return f"+{digits}"

        # If not valid MSISDN, try to convert to Ukrainian MSISDN
        UA_CODES = {
            "039", "050", "063", "066", "067", "068",
            "091", "092", "093", "094",
            "095", "096", "097", "098", "099"
        }

        code = None
        number_part = None

        # Case 1: 380XXXXXXXXX (12 digits) - already Ukrainian MSISDN without +
        if digits.startswith("380") and len(digits) == 12:
            code = digits[3:6]
            number_part = digits[3:]
        # Case 2: 0XXXXXXXXX (10 digits) - Ukrainian national format
        elif digits.startswith("0") and len(digits) == 10:
            code = digits[1:4]
            number_part = digits[1:]
        # Case 3: 80XXXXXXXXX (11 digits) - Ukrainian with 8 prefix
        elif digits.startswith("80") and len(digits) == 11:
            code = digits[2:5]
            number_part = digits[2:]
        # Case 4: XXXXXXXXX (9 digits) - just the number without prefix
        elif len(digits) == 9:
            code = digits[0:3]
            number_part = digits

        # Validate Ukrainian operator code and return formatted number
        if code and code in UA_CODES and number_part and len(number_part) == 9:
            return f"+380{number_part}"

        return None

    def __str__(self):
        return str(self.value)


class Email(Field):
    EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    def __init__(self, value: str):
        if not re.fullmatch(self.EMAIL_PATTERN, value):
            raise InvalidEmailFormatError(value)
        super().__init__(value)


class Address(Field):
    """
    Stores a postal address.
    Minimal validation:
        - at least 5 visible chars
        - no forbidden symbols
        - trims extra spaces
    """

    FORBIDDEN = r'[%<&>"\']'

    def __init__(self, value: str):
        cleaned = value.strip()

        if len(cleaned) < 5:
            raise InvalidTagFormatError(f"Invalid address (too short): {value}")

        if re.search(self.FORBIDDEN, cleaned):
            raise InvalidTagFormatError(f"Address contains forbidden symbols: {value}")

        super().__init__(cleaned)


class Title(Field):
    def __init__(self, value):
        if not value or len(value.strip()) <= 5:
            raise InvalidTitleFormatError(value)
        super().__init__(value.strip())


class Tag(Field):
    def __init__(self, value):
        tag_len = len(value.strip()) if value else 0
        if not value or tag_len < 3 or tag_len > 10:
            raise InvalidTagFormatError(value)

        # Check for % and special symbols (allow alphanumeric, spaces, hyphens, underscores)
        if re.search(r'[%&<>"\'/\\]', value) or not re.match(
            r"^[a-zA-Z0-9\s\-_]+$", value.strip()
        ):
            raise InvalidTagFormatError(value)

        super().__init__(value.strip())
