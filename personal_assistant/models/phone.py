import re
from personal_assistant.models.field import Field


class Phone(Field):
    """Class for phone number."""

    def __init__(self, value):
        validate_value = self.validate_number(value)

        super().__init__(validate_value)

    @staticmethod
    def validate_number(phone_number):
        """Validate phone number"""

        if not phone_number or not phone_number.strip():
            raise ValueError("Phone number cannot be empty")

        if not re.fullmatch(r"\d{10}", phone_number):
            raise ValueError(
                f"Number {phone_number} is invalid. Must be exactly 10 digits."
            )

        return phone_number
