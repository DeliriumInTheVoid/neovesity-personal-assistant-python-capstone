from collections import UserDict
from datetime import datetime, timedelta
import re
         

class Field:                     # Базовий клас для полів запису
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
class Birthday(Field):                                        # Step 1 - adding Birthday Classes
    def __init__(self, value):
        pattern = r'\b(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})\b'
        if not re.match(pattern, value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        try:
            date_value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date_value)


class Name(Field):               # Клас для зберігання імені контакту. Обов'язкове поле.
    def __init__(self, name:str):
         if not name:            # Обов'язкове поле. Перевірка
              raise ValueError("Поле імʼя не може бути порожнім")
         super().__init__(name)

class Phone(Field):              # Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
    def __init__(self, phone_number: str):
         ph = str(phone_number).strip()               # приводимо до єдиного формату
         if len(ph) != 10 or not ph.isdigit():        # check fot 10 and for digits
              raise ValueError("Номер має бути у форматі 10 цифр")
         else:
             super().__init__(ph)
         
    def __eq__(self, other):
        return isinstance(other, Phone) and self.value == other.value     # To be able to compare two phone obj in Record dd change remove phone

# Adding birthday to record with None as defult
class Record:                    # Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    def __str__(self):
        return f"Name: {self.name} Phone: {self.phones} Birthday: {self.birthday}"   
    
    def add_phone(self, phone: Phone):
        if phone not in self.phones:
            self.phones.append(phone)
        else:
            print(f"Такий номер вже є")
         
    def remove_phone(self, phone: Phone):
        self.phones = [p for p in self.phones if p != phone]  # New list withou phone to delete
        print(f"Видалено номер {phone}")

    def edit_phone(self, old_phone:Phone, new_phone:Phone):
        for p in range(len(self.phones)):
            if self.phones[p] == old_phone:
                self.phones[p] = new_phone
                print(f"{old_phone} замінено на {new_phone}")
                break        # заміна першого знайденого
            else:
                print(f"{old_phone} не знайдено")

    def find_phone(self, phone: str):
        phone_obj = Phone(phone)
        for p in self.phones:
            if p == phone_obj:
                return p.value
        return None
        

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "—"
        bday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "—"
        return f"{self.name.value}: {phones} | Birthday: {bday}"

class AddressBook(UserDict):     # Клас для зберігання та управління записами.

    def add_record(self, record: Record):
          self.data[record.name.value] = record

    def find(self, name_to_find: str):
        return self.data.get(name_to_find)    # To get the record by name
    
    def find_phone(self, phone_to_find: str):  # To find a record by a phone number
        for rec in self:
            if phone in rec.phones:
                return rec
            else:
                return None
               
    def delete(self, name: str):
        record = self.data.pop(name, None)    # Deleting or returning a message of not found
        if record:
            print(f"Запис {name} видалено")
        else:
            print(f"Запис {name} не знайдено")  

def parse_input(user_input):
    """
    Parsing input to a command and arguments
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            # Show the actual reason (e.g., "Номер має бути у форматі 10 цифр")
            return str(e)
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        phone_obj = Phone(phone) 
        record.add_phone(phone_obj)
    return message

@input_error
def change(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record is None:
        return f"Contact {name} phone {old_phone} - not found"
    old_phone_obj = Phone(old_phone)
    new_phone_obj = Phone(new_phone)

    if old_phone_obj in record.phones:
        record.edit_phone(old_phone_obj, new_phone_obj)
        return f"Phone for {name} changed from {old_phone} to {new_phone}."
    else:
        return f"Phone {old_phone} not found for contact '{name}'."

@input_error
def phone (args, book: AddressBook):    # Returns a contact by Name
    name, *_ = args           # returns a list of persons phone numbers
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found"
    phone_list = "; ".join(p.value for p in record.phones)
    return f"{name}: {phone_list}"

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    
    lines = []
    for record in book.data.values():
        lines.append(str(record))             #  Using Record.__str__ method we already have in Record Class
    return "\n".join(lines)
  
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."  # Contact not found check

    try:
        birthday_obj = Birthday(birthday_str) # Birthday format validation
    except ValueError as e:
        return str(e)

    record.birthday = birthday_obj
    return f"Birthday for '{name}' set to {birthday_str}."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."

    if record.birthday:                                          # If there is a birthday - return it
        date_str = record.birthday.value.strftime("%d.%m.%Y")
        return f"{name}'s birthday is on {date_str}."
    else:
        return f"No birthday information for '{name}'."
    
def get_upcoming_birthdays(book: AddressBook):
    today = datetime.today().date()
    upcoming = []

    for record in book.data.values():
        if not record.birthday:
            continue
        
        bday_date = record.birthday.value.date()
        bday_this_year = bday_date.replace(year=today.year) # birthday have passed or not

        # If birthday already passed this year → take next year's date
        if bday_this_year < today:
            bday_this_year = bday_this_year.replace(year=today.year + 1)

        days_until_birthday = (bday_this_year - today).days

        if 0 <= days_until_birthday < 7:
            date_str = bday_this_year.strftime("%d.%m.%Y")
            upcoming.append(f"On {date_str} is {record.name.value} birthday")  # add birthday date and name to list 

    return upcoming
    
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        
        elif command == "hello":
            print("How can I help you?")
        elif command in ["help", "?"]:
            print("Place for ReadMe")
        
        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))     # Add record

        elif command == "change":
            print(change(args, book))    # Add contact also changes number for a given name

        elif command == "phone":
            print(phone(args, book))           # Returns a Phone info by name

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(get_upcoming_birthdays(book))

        else:
            print("Invalid command.")
        

if __name__ == "__main__":
    main()