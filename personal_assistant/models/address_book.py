from collections import UserDict
from datetime import datetime, timedelta
from personal_assistant.models.record import Record
from personal_assistant.models.exceptions import RecordAlreadyExistsError, ContactNotFoundError


class AddressBook(UserDict):
    def __setitem__(self, key, value):
        if not isinstance(value, Record):
            raise ValueError("Value must be an instance of Record.")
        if key != value.first_name.value:
            raise ValueError("Key must match the Record's name.")
        if key in self.data:
            raise RecordAlreadyExistsError(f"Contact '{key}' already exists.")
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if key not in self.data:
            raise ContactNotFoundError(f"Contact '{key}' not found.")
        return super().__getitem__(key)

    def __delitem__(self, key):
        if key not in self.data:
            raise ContactNotFoundError(f"Contact '{key}' not found.")
        super().__delitem__(key)

    def add_record(self, record: Record):
        self[record.first_name.value] = record

    def find(self, name:str) -> Record | None:
        if name not in self:
            return None
        return self[name]

    def delete(self, name: str) -> None:
        del self[name]

    def get_upcoming_birthdays(self, warn_in_days: int = 7) -> list[tuple[Record, datetime]]:
        today = datetime.today().date()
        warn_delta = timedelta(days=warn_in_days)
        current_year = today.year
        end_date = today + warn_delta
        upcoming_birthdays_users: list[tuple[Record, datetime]] = []
        for record in self.data.values():
            if not record.birthday:
                continue
            birthday = record.birthday.value
            birthday_this_year = birthday.replace(year=current_year).date()
            user_congratulation_date = None
            if today <= birthday_this_year <= end_date:
                user_congratulation_date = birthday_this_year
            elif birthday_this_year < today:
                birthday_next_year = birthday.replace(year=current_year + 1).date()
                if today <= birthday_next_year <= end_date:
                    user_congratulation_date = birthday_next_year
            if user_congratulation_date:
                if user_congratulation_date.weekday() in (5, 6):
                    user_congratulation_date += timedelta(days=(7 - user_congratulation_date.weekday()))
            if user_congratulation_date:
                upcoming_birthdays_users.append((record, user_congratulation_date))

        return upcoming_birthdays_users

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

__all__ = ["AddressBook"]
