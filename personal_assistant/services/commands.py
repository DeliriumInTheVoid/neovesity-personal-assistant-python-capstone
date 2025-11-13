from typing import Callable

from personal_assistant.cli.args_parsers import ArgsParser
from personal_assistant.models.address_book import AddressBook
from personal_assistant.models.record import Record
from personal_assistant.models.exceptions import ContactBotError


def input_error(expected_format: str):
    def decorator(func: Callable) -> Callable:
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ContactBotError as e:
                return f"Error: {e}"
            except IndexError:
                return f"Invalid arguments. Expected: {expected_format}"
            except ValueError:
                return f"Invalid value. Expected: {expected_format}"

        inner.usage = expected_format # attach usage info to the inner function for help command
        return inner
    return decorator


def handle_unknown_command(func: Callable) -> Callable:
    """
    Decorator to handle unknown commands by catching KeyError exceptions.
    When a KeyError is caught, it returns an error message and shows the help command.
    Returns a "Null Object" function that does nothing for unknown commands.
    """
    def inner(command_id: str):
        try:
            return func(command_id)
        except KeyError:
            err_msg = f"[bold red]🦥 Uhh... I looked everywhere. No such '{command_id}'.[/bold red]"
            err_msg += "\n" + show_help_command()
            return lambda args, book: err_msg
    return inner


@input_error("add [name] [phone]")
def add_contact_command(args:list[str], book: AddressBook) -> str:
    parser = ArgsParser(args)
    return add_contact(parser.get_next(), parser.get_next(), book)


def add_contact(name: str, phone: str, book: AddressBook) -> str:
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    else:
        record.add_phone(phone)

    return f"Contact '{name}' added with phone number {phone}."


@input_error("change [name] [old_phone] [new_phone]")
def change_contact_command(args: list[str], book: AddressBook) -> str:
    parser = ArgsParser(args)
    return change_contact(parser.get_next(), parser.get_next(), parser.get_next(), book)


def change_contact(name: str, old_phone: str, new_phone:str, book: AddressBook) -> str:
    record = book[name]
    record.edit_phone(old_phone, new_phone)
    return f"Contact '{name}' updated with new phone number {new_phone}."


@input_error("phone [name]")
def show_phone_command(args: list[str], book: AddressBook) -> str:
    parser = ArgsParser(args)
    return show_phone(parser.get_next(), book)


def show_phone(name: str, book: AddressBook) -> str:
    contacts = book[name].phones
    phones_list = ', '.join(str(phone) for phone in contacts)
    return f"Contact '{name}' has phone numbers: {phones_list}"


@input_error("add-birthday [name] [birthday]")
def add_birthday_command(args: list[str], book: AddressBook) -> str:
    parser = ArgsParser(args)
    return add_birthday(parser.get_next(), parser.get_next(), book)


def add_birthday(name: str, birthday: str, book: AddressBook):
    record = book[name]
    record.add_birthday(birthday)
    return f"Birthday {birthday} added to contact '{name}'."


@input_error("show-birthday [name]")
def show_birthday_command(args: list[str], book: AddressBook) -> str:
    parser = ArgsParser(args)
    return show_birthday(parser.get_next(), book)


def show_birthday(name: str, book: AddressBook) -> str:
    record = book[name]
    if record.birthday is not None:
        return f"Contact '{name}' has birthday on {record.birthday}."

    return f"Contact '{name}' does not have a birthday set."


@input_error("birthdays [days]=7")
def show_upcoming_birthdays_command(args: list[str], book: AddressBook) -> str:
    days: int = 7
    parse = ArgsParser(args)
    try:
        days = int(parse.get_next())
    except IndexError:
        pass
    return show_upcoming_birthdays(book, days)


def show_upcoming_birthdays(book: AddressBook, days: int = 7) -> str:
    upcoming_birthdays = book.get_upcoming_birthdays(warn_in_days=days)
    if not upcoming_birthdays:
        return f"No upcoming birthdays in the next {days} days."

    result_lines = [f"Upcoming birthdays in the next {days} days:"]
    for record, congratulation_date in upcoming_birthdays:
        congratulate_date_str = congratulation_date.strftime("%d.%m.%Y (%A)")
        result_lines.append(
            f" - {record.name}: "
            f"(Birthday: {record.birthday.value.strftime('%d.%m')}) -> Congratulate on {congratulate_date_str}"
        )
    return '\n'.join(result_lines)


def show_all_command(args: list[str], book: AddressBook) -> str:
    return show_all(book)


def show_all(book: AddressBook) -> str:
    if len(book) == 0:
        return "No contacts available."

    return f"All contacts:\n" + '\n'.join(str(record) for record in book.values())


def search_command(args: list[str], book: AddressBook) -> str:
    return search_contacts(args, book)


def search_contacts(args, book: AddressBook):
    """Search contacts by partial match in name or phone"""
    query = args[0].lower()
    results = []

    for record in book.data.values():
        if query in record.name.value.lower() or any(
            query in p.value for p in record.phones
        ):
            phones = ", ".join(p.value for p in record.phones)
            results.append(f"{record.name.value}: {phones}")

    if results:
        return "\n".join(results)
    return "No matches found."


def show_help_command(args: list[str] = None, book: AddressBook = None) -> str:
    """
    Show available commands and their usage.
    Gets usage information from the 'usage' attribute of each command handler function.
    """

    result_lines = ["Available commands:", "-------------------"]
    for name, func in COMMAND_HANDLERS.items():
        usage = getattr(func, 'usage', None)
        if usage:
            result_lines.append(f"  {usage}")
        else:
            result_lines.append(f"  {name}")
    return '\n'.join(result_lines)


def hello_command(args: list[str], book: AddressBook) -> str:
    return "How can I help you?"


COMMAND_HANDLERS: dict[str, Callable[[list[str], AddressBook], None]] = {
    "help": show_help_command,                                      # help
    "hello": hello_command,                                         # hello
    "add-contact": add_contact_command,                             # add [ім'я] [телефон]
    "change-contact": change_contact_command,                       # change [ім'я] [старий телефон] [новий телефон]
    "phone": show_phone_command,                                    # phone [ім'я]
    "all": show_all_command,                                        # all
    "add-birthday": add_birthday_command,                           # add-birthday [ім'я] [дата народження]
    "show-birthday": show_birthday_command,                         # show-birthday [ім'я]
    "birthdays": show_upcoming_birthdays_command,                   # birthdays [кількість днів]=7
    "search": search_command,                                       # search [query]
    # clear
    "exit": lambda args, contacts: print("Good bye!"),              # close або exit
}


@handle_unknown_command
def get_command(command_id: str) -> Callable[[list[str], AddressBook], None]:
    return COMMAND_HANDLERS[command_id]
