import faker
from personal_assistant.models.address_book import AddressBook
from personal_assistant.models.record import Record


def generate_address_book(contacts: int = 10) -> AddressBook:
    """
    Generate a random address book with the specified number of contacts.
    Args:
        contacts:
            The number of contacts to generate. Default is 10.
    Returns:
        An AddressBook instance populated with random contacts.
    """

    fake = faker.Faker()

    book = AddressBook()

    for _ in range(contacts):
        name = fake.name()
        birthday = fake.date_of_birth().strftime("%d.%m.%Y")

        record = Record(name)
        for _ in range(fake.random_int(min=0, max=3)):
            record.add_phone(fake.msisdn()[3:13])
        record.add_birthday(birthday)

        book.add_record(record)

    return book
