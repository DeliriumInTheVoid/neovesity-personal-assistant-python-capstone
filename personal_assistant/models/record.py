from typing import List

from personal_assistant.models.field import Email, Name, Phone, Birthday, Address
from personal_assistant.models.exceptions import (
    PhoneAlreadyExistsError,
    PhoneNotFoundError,
)


class Record:
    def __init__(self, name):
        self.uuid = None
        self.first_name = Name(name)
        self.last_name: Name | None = None
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        self.email: Email | None = None
        self.address: Address | None = None

    def add_phone(self, phone: str) -> None:
        if self.find_phone(phone):
            raise PhoneAlreadyExistsError(
                f"Phone {phone} already exists for {self.first_name}"
            )
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return
        raise PhoneNotFoundError(f"Phone {old_phone} not found for {self.first_name}")

    def find_phone(self, phone: str) -> str | None:
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def delete_phone(self, phone: str) -> None:
        for idx, p in enumerate(self.phones):
            if p.value == phone:
                del self.phones[idx]
                return
        raise PhoneNotFoundError(f"Phone {phone} not found for {self.first_name}")

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def add_email(self, email: str) -> None:
        if email:
            self.email = Email(email)
        else:
            self.email = None

    def add_address(self, address: str) -> None:
        self.address = Address(address)

    def __str__(self):
        return f"Contact name: {self.first_name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    @classmethod
    def from_dict(cls, contact_data):
        record = cls(contact_data["first_name"])
        record.uuid = contact_data.get("uuid")
        record.last_name = Name(contact_data.get("last_name"))
        record.phones = [Phone(phone) for phone in contact_data.get("phones", []) if phone]
        birthday = contact_data.get("birthday")
        if birthday:
            record.birthday = Birthday(birthday)
        emails: List[str] = contact_data.get("emails", [])
        if emails:
            record.email = Email(emails[0])  # Assuming only one email for simplicity
        elif contact_data.get("email"):
            record.email = Email(contact_data.get("email"))
        if contact_data.get("address"):
            record.address = Address(contact_data.get("address"))
        return record

    def to_dict(self):
        contact_data = {
            "uuid": self.uuid,
            "first_name": self.first_name.value,
            "last_name": self.last_name.value if self.last_name else None,
            "phones": [phone.value for phone in self.phones],
            "birthday": (
                self.birthday.value.strftime("%d.%m.%Y") if self.birthday else None
            ),
            "email": self.email.value if self.email else None,
            "address": self.address.value if self.address else None,
        }
        return contact_data
