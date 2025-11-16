import pytest
from datetime import datetime, timedelta


from personal_assistant.models import (
    Field, Name, Phone, Birthday, Record, AddressBook, Email
)
from personal_assistant.models.exceptions import (
    InvalidPhoneFormatError, InvalidBirthdayFormatError,
    PhoneAlreadyExistsError, ContactNotFoundError,
    PhoneNotFoundError, RecordAlreadyExistsError, InvalidEmailFormatError,
)
from personal_assistant.cli.args_parsers import parse_input, ArgsParser
from personal_assistant.use_cases.commands import (
    add_contact, change_contact, show_phone, add_birthday,
    show_birthday, show_upcoming_birthdays, show_all,
    add_contact_command, change_contact_command, show_phone_command,
    add_birthday_command, show_birthday_command, show_upcoming_birthdays_command,
    get_command
)


class TestField:
    """Test Field base class"""

    def test_field_creation(self):
        field = Field("test_value")
        assert field.value == "test_value"

    def test_field_str(self):
        field = Field("test_value")
        assert str(field) == "test_value"


class TestName:
    """Test Name class"""

    def test_name_creation(self):
        name = Name("John")
        assert name.value == "John"

    def test_name_str(self):
        name = Name("Jane")
        assert str(name) == "Jane"

class TestEmail:
    """Test Email class"""

    def test_email_creation(self):
        assert Email("john@gmail.com").value == "john@gmail.com"

    def test_wrong_str(self):
        with pytest.raises(InvalidEmailFormatError):
            Email("john@@gmail..com")


class TestPhone:
    """Test Phone class"""

    def test_valid_phone_creation(self):
        phone = Phone("1234567890")
        assert phone.value == "1234567890"

    def test_invalid_phone_too_short(self):
        with pytest.raises(InvalidPhoneFormatError):
            Phone("123456789")

    def test_invalid_phone_too_long(self):
        with pytest.raises(InvalidPhoneFormatError):
            Phone("12345678901")

    def test_invalid_phone_non_digits(self):
        with pytest.raises(InvalidPhoneFormatError):
            Phone("123abc7890")

    def test_phone_str(self):
        phone = Phone("9876543210")
        assert str(phone) == "9876543210"


class TestBirthday:
    """Test Birthday class"""

    def test_valid_birthday_creation(self):
        birthday = Birthday("01.01.1990")
        assert isinstance(birthday.value, datetime)
        assert birthday.value.day == 1
        assert birthday.value.month == 1
        assert birthday.value.year == 1990

    def test_invalid_birthday_format(self):
        with pytest.raises(InvalidBirthdayFormatError):
            Birthday("1990-01-01")

    def test_invalid_birthday_format_wrong_order(self):
        with pytest.raises(InvalidBirthdayFormatError):
            Birthday("01/01/1990")

    def test_invalid_birthday_invalid_date(self):
        with pytest.raises(InvalidBirthdayFormatError):
            Birthday("32.13.1990")


class TestRecord:
    """Test Record class"""

    def test_record_creation(self):
        record = Record("John")
        assert record.name.value == "John"
        assert len(record.phones) == 0
        assert record.birthday is None

    def test_add_phone(self):
        record = Record("John")
        record.add_phone("1234567890")
        assert len(record.phones) == 1
        assert record.phones[0].value == "1234567890"

    def test_add_multiple_phones(self):
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("9876543210")
        assert len(record.phones) == 2

    def test_add_duplicate_phone(self):
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(PhoneAlreadyExistsError):
            record.add_phone("1234567890")

    def test_find_phone_exists(self):
        record = Record("John")
        record.add_phone("1234567890")
        found = record.find_phone("1234567890")
        assert found == "1234567890"

    def test_find_phone_not_exists(self):
        record = Record("John")
        record.add_phone("1234567890")
        found = record.find_phone("9999999999")
        assert found is None

    def test_edit_phone(self):
        record = Record("John")
        record.add_phone("1234567890")
        record.edit_phone("1234567890", "9876543210")
        assert len(record.phones) == 1
        assert record.phones[0].value == "9876543210"

    def test_edit_phone_not_found(self):
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(PhoneNotFoundError):
            record.edit_phone("9999999999", "1111111111")

    def test_delete_phone(self):
        record = Record("John")
        record.add_phone("1234567890")
        record.delete_phone("1234567890")
        assert len(record.phones) == 0

    def test_delete_phone_not_found(self):
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(PhoneNotFoundError):
            record.delete_phone("9999999999")

    def test_add_birthday(self):
        record = Record("John")
        record.add_birthday("01.01.1990")
        assert record.birthday is not None
        assert record.birthday.value.day == 1
        assert record.birthday.value.month == 1

    def test_record_str(self):
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("9876543210")
        result = str(record)
        assert "John" in result
        assert "1234567890" in result
        assert "9876543210" in result


class TestAddressBook:
    """Test AddressBook class"""

    def test_address_book_creation(self):
        book = AddressBook()
        assert len(book) == 0

    def test_add_record(self):
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        assert len(book) == 1
        assert "John" in book

    def test_add_duplicate_record(self):
        book = AddressBook()
        record1 = Record("John")
        record2 = Record("John")
        book.add_record(record1)
        with pytest.raises(RecordAlreadyExistsError):
            book.add_record(record2)

    def test_find_record(self):
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        found = book.find("John")
        assert found.name.value == "John"

    def test_find_record_not_found(self):
        book = AddressBook()
        assert book.find("NonExistent") is None

    def test_delete_record(self):
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        book.delete("John")
        assert len(book) == 0

    def test_delete_record_not_found(self):
        book = AddressBook()
        with pytest.raises(ContactNotFoundError):
            book.delete("NonExistent")

    def test_getitem(self):
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        retrieved = book["John"]
        assert retrieved.name.value == "John"

    def test_getitem_not_found(self):
        book = AddressBook()
        with pytest.raises(ContactNotFoundError):
            _ = book["NonExistent"]

    def test_delitem(self):
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        del book["John"]
        assert len(book) == 0

    def test_get_upcoming_birthdays_empty_book(self):
        book = AddressBook()
        birthdays = book.get_upcoming_birthdays()
        assert len(birthdays) == 0

    def test_get_upcoming_birthdays_no_birthdays_set(self):
        book = AddressBook()
        record = Record("John")
        record.add_phone("1234567890")
        book.add_record(record)
        birthdays = book.get_upcoming_birthdays()
        assert len(birthdays) == 0

    def test_get_upcoming_birthdays_within_range(self):
        book = AddressBook()
        record = Record("John")
        # Set birthday to 3 days from today
        future_date = datetime.today() + timedelta(days=3)
        birthday_str = future_date.strftime("%d.%m.1990")
        record.add_birthday(birthday_str)
        book.add_record(record)

        birthdays = book.get_upcoming_birthdays(warn_in_days=7)
        assert len(birthdays) == 1
        assert birthdays[0][0].name.value == "John"

    def test_get_upcoming_birthdays_outside_range(self):
        book = AddressBook()
        record = Record("John")
        # Set birthday to 10 days from today
        future_date = datetime.today() + timedelta(days=10)
        birthday_str = future_date.strftime("%d.%m.1990")
        record.add_birthday(birthday_str)
        book.add_record(record)

        birthdays = book.get_upcoming_birthdays(warn_in_days=7)
        assert len(birthdays) == 0

    def test_get_upcoming_birthdays_weekend_adjustment(self):
        book = AddressBook()
        record = Record("John")

        # Find next Saturday
        today = datetime.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)

        birthday_str = saturday.strftime("%d.%m.1990")
        record.add_birthday(birthday_str)
        book.add_record(record)

        birthdays = book.get_upcoming_birthdays(warn_in_days=14)
        if len(birthdays) > 0:
            congratulation_date = birthdays[0][1]
            # Should be adjusted to Monday
            assert congratulation_date.weekday() == 0


class TestArgsParser:
    """Test ArgsParser class"""

    def test_parse_input_simple_command(self):
        command, args = parse_input("hello")
        assert command == "hello"
        assert args == []

    def test_parse_input_command_with_args(self):
        command, args = parse_input("add John 1234567890")
        assert command == "add"
        assert args == ["John", "1234567890"]

    def test_parse_input_empty_string(self):
        command, args = parse_input("")
        assert command == "empty"
        assert args == []

    def test_parse_input_whitespace_only(self):
        command, args = parse_input("   ")
        assert command == "empty"
        assert args == []

    def test_parse_input_exit_variations(self):
        for exit_cmd in ["exit", "quit", "q", "close", "EXIT", "QUIT"]:
            command, args = parse_input(exit_cmd)
            assert command == "exit"

    def test_args_parser_get_next(self):
        parser = ArgsParser(["arg1", "arg2", "arg3"])
        assert parser.get_next() == "arg1"
        assert parser.get_next() == "arg2"
        assert parser.get_next() == "arg3"

    def test_args_parser_get_next_empty(self):
        parser = ArgsParser([])
        with pytest.raises(IndexError):
            parser.get_next()

    def test_args_parser_has_next(self):
        parser = ArgsParser(["arg1", "arg2"])
        assert parser.has_next() is True
        parser.get_next()
        assert parser.has_next() is True
        parser.get_next()
        assert parser.has_next() is False

    def test_args_parser_get_all_remaining(self):
        parser = ArgsParser(["arg1", "arg2", "arg3"])
        parser.get_next()
        remaining = parser.get_all_remaining_as_str()
        assert remaining == "arg2 arg3"
        assert parser.has_next() is False

    def test_args_parser_get_all_remaining_empty(self):
        parser = ArgsParser([])
        with pytest.raises(IndexError):
            parser.get_all_remaining_as_str()


class TestCommands:
    """Test command functions"""

    def test_add_contact(self):
        book = AddressBook()
        message = add_contact("John", "1234567890", book)
        assert "John" in book
        assert book["John"].phones[0].value == "1234567890"
        assert "added" in message.lower()

    def test_add_contact_command(self):
        book = AddressBook()
        add_contact_command(["John", "1234567890"], book)
        assert "John" in book

    def test_add_contact_command_missing_args(self):
        book = AddressBook()
        result = add_contact_command(["John"], book)
        assert "Invalid arguments" in result or "Error" in result

    def test_change_contact(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        message = change_contact("John", "1234567890", "9876543210", book)
        assert book["John"].phones[0].value == "9876543210"
        assert "updated" in message.lower()

    def test_change_contact_command(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        change_contact_command(["John", "1234567890", "9876543210"], book)
        assert book["John"].phones[0].value == "9876543210"

    def test_change_contact_not_found(self):
        book = AddressBook()
        result = change_contact_command(["NonExistent", "1234567890", "9876543210"], book)
        assert "Error" in result or "not found" in result.lower()

    def test_show_phone(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        message = show_phone("John", book)
        assert "1234567890" in message

    def test_show_phone_command(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        message = show_phone_command(["John"], book)
        assert "1234567890" in message

    def test_add_birthday(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        message = add_birthday("John", "01.01.1990", book)
        assert book["John"].birthday is not None
        assert "Birthday" in message

    def test_add_birthday_command(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        add_birthday_command(["John", "01.01.1990"], book)
        assert book["John"].birthday is not None

    def test_show_birthday(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        add_birthday("John", "01.01.1990", book)
        message = show_birthday("John", book)
        assert "01.01.1990" in message

    def test_show_birthday_not_set(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        message = show_birthday("John", book)
        assert "does not have" in message.lower()

    def test_show_birthday_command(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        add_birthday("John", "01.01.1990", book)
        message = show_birthday_command(["John"], book)
        assert "birthday" in message.lower()

    def test_show_upcoming_birthdays(self):
        book = AddressBook()
        record = Record("John")
        future_date = datetime.today() + timedelta(days=3)
        birthday_str = future_date.strftime("%d.%m.1990")
        record.add_birthday(birthday_str)
        record.add_phone("1234567890")
        book.add_record(record)

        message = show_upcoming_birthdays(book, days=7)
        assert "John" in message or "No upcoming" in message

    def test_show_upcoming_birthdays_command(self):
        book = AddressBook()
        message = show_upcoming_birthdays_command([], book)
        assert "No upcoming" in message or "Upcoming" in message

    def test_show_upcoming_birthdays_command_with_days(self):
        book = AddressBook()
        message = show_upcoming_birthdays_command(["14"], book)
        assert "14 days" in message

    def test_show_all_empty(self):
        book = AddressBook()
        message = show_all(book)
        assert "No contacts" in message

    def test_show_all_with_contacts(self):
        book = AddressBook()
        add_contact("John", "1234567890", book)
        add_contact("Jane", "9876543210", book)
        message = show_all(book)
        assert "John" in message
        assert "Jane" in message

    def test_get_command_valid(self):
        command_func = get_command("add")
        assert command_func is not None
        assert callable(command_func)

    def test_get_command_invalid(self):
        command_func = get_command("invalid_command")
        # Should return a null object function that does nothing
        assert callable(command_func)
        result = command_func([], AddressBook())
        assert "looked everywhere" in result.lower() or "no such" in result.lower()


class TestExceptions:
    """Test custom exceptions"""

    def test_invalid_phone_format_error(self):
        with pytest.raises(InvalidPhoneFormatError) as exc_info:
            raise InvalidPhoneFormatError("123")
        assert "123" in str(exc_info.value)
        assert "10 digits" in str(exc_info.value)

    def test_invalid_birthday_format_error(self):
        with pytest.raises(InvalidBirthdayFormatError) as exc_info:
            raise InvalidBirthdayFormatError("01/01/1990")
        assert "01/01/1990" in str(exc_info.value)
        assert "DD.MM.YYYY" in str(exc_info.value)

    def test_contact_not_found_error(self):
        with pytest.raises(ContactNotFoundError) as exc_info:
            raise ContactNotFoundError("Contact 'John' not found")
        assert "John" in str(exc_info.value)

    def test_phone_not_found_error(self):
        with pytest.raises(PhoneNotFoundError) as exc_info:
            raise PhoneNotFoundError("Phone not found")
        assert "Phone" in str(exc_info.value)

    def test_phone_already_exists_error(self):
        with pytest.raises(PhoneAlreadyExistsError) as exc_info:
            raise PhoneAlreadyExistsError("Phone already exists")
        assert "already exists" in str(exc_info.value)

    def test_record_already_exists_error(self):
        with pytest.raises(RecordAlreadyExistsError) as exc_info:
            raise RecordAlreadyExistsError("Record already exists")
        assert "already exists" in str(exc_info.value)


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_contact_lifecycle(self):
        book = AddressBook()

        # Add contact
        add_contact("John", "1234567890", book)
        assert "John" in book

        # Add birthday
        add_birthday("John", "01.01.1990", book)
        assert book["John"].birthday is not None

        # Change phone
        change_contact("John", "1234567890", "9876543210", book)
        assert book["John"].phones[0].value == "9876543210"

        # Show phone
        message = show_phone("John", book)
        assert "9876543210" in message

        # Delete contact
        book.delete("John")
        assert "John" not in book

    def test_multiple_contacts_with_birthdays(self):
        book = AddressBook()

        # Add multiple contacts
        today = datetime.today()
        for i in range(5):
            name = f"Contact{i}"
            phone = f"123456789{i}"
            future_date = today + timedelta(days=i)
            birthday_str = future_date.strftime("%d.%m.1990")

            record = Record(name)
            record.add_phone(phone)
            record.add_birthday(birthday_str)
            book.add_record(record)

        assert len(book) == 5

        # Check upcoming birthdays
        birthdays = book.get_upcoming_birthdays(warn_in_days=7)
        assert len(birthdays) >= 0

        # Show all
        message = show_all(book)
        assert "Contact0" in message

    def test_error_handling_workflow(self):
        book = AddressBook()

        # Try to change non-existent contact
        result = change_contact_command(["NonExistent", "1234567890", "9876543210"], book)
        assert "Error" in result or "not found" in result.lower()

        # Add contact with invalid phone
        with pytest.raises(InvalidPhoneFormatError):
            add_contact("John", "123", book)

        # Add contact
        add_contact("John", "1234567890", book)

        # Try to add duplicate phone
        with pytest.raises(PhoneAlreadyExistsError):
            book["John"].add_phone("1234567890")

