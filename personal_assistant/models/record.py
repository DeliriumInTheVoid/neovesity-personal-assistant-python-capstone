from personal_assistant.models.field import Email, Name, Phone, Birthday, Address
from personal_assistant.models.exceptions import (
    PhoneAlreadyExistsError,
    PhoneNotFoundError,
)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = None
        self.email = None
        self.address = None

    def add_phone(self, phone: str) -> None:
        if self.find_phone(phone):
            raise PhoneAlreadyExistsError(
                f"Phone {phone} already exists for {self.name}"
            )
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return
        raise PhoneNotFoundError(f"Phone {old_phone} not found for {self.name}")

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
        raise PhoneNotFoundError(f"Phone {phone} not found for {self.name}")

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
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
