import pickle
from pathlib import Path
from personal_assistant.cli.args_parsers import parse_input
from personal_assistant.services.commands import get_command
from personal_assistant.models.address_book import AddressBook


def start_bot(book: AddressBook = None):
    """
    Starts the assistant bot, loading data from file if provided,
    and saving data on exit.
    Args:
        book: Optional AddressBook instance to use. If None, loads from file.
        Test purpose, allows injecting a pre-populated AddressBook.
    """
    is_running: bool = True

    save_on_exit = False
    if book is None:
        book = load_data()
        save_on_exit = True

    print("Welcome to the assistant bot!")

    try:
        while is_running:
            user_input = input("Enter command: ")
            command_id, args = parse_input(user_input)

            get_command(command_id)(args, book)

            if command_id == "exit":
                is_running = False
            else:
                # auto-save after each command, not loosing data on unexpected exit
                save_data(book, save_on_exit)
    except KeyboardInterrupt:
        print("\nExiting the bot. Goodbye!")
        save_data(book, save_on_exit)


def save_data(book:AddressBook, save:bool, filename:str= "addressbook.pkl"):
    if not save:
        return

    filepath = Path(filename)
    backup = filepath.with_suffix(".pkl.bak")

    if filepath.exists():
        if backup.exists():
            backup.unlink()
        filepath.rename(backup)

    try:
        with open(filepath, "wb") as f:
            pickle.dump(book, f)
    except Exception as e:
        if backup.exists():
            backup.rename(filepath)
        raise e


def load_data(filename="addressbook.pkl"):
    filepath = Path(filename)

    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        backup = filepath.with_suffix(".pkl.bak")
        if backup.exists():
            try:
                with open(backup, "rb") as f:
                    return pickle.load(f)
            except:
                print("Failed to load backup data. Starting with an empty address book.")
        return AddressBook()


if __name__ == "__main__":
    start_bot()
