import faker
import random
from typing import Generator, List

from personal_assistant.models import Name
from personal_assistant.models.record import Record
from personal_assistant.models.note import Note, Tag


def generate_contacts(num_contacts: int = 10) -> Generator[Record, None, None]:
    """
    Generate random contact records.

    Args:
        num_contacts: The number of contacts to generate.

    Yields:
        A Record object with fake data.
    """
    fake = faker.Faker()
    for _ in range(num_contacts):
        full_name = fake.name()
        full_name_lst = full_name.split(" ")
        first_name = full_name_lst[0]
        last_name = full_name_lst[1] if len(full_name_lst) > 1 else None
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime(
            "%d.%m.%Y"
        )
        email = fake.email()

        record = Record(first_name)
        record.last_name = Name(last_name)
        record.add_birthday(birthday)
        record.add_email(email)

        for _ in range(fake.random_int(min=1, max=3)):
            record.add_phone(fake.phone_number())

        yield record


def generate_notes(
    num_notes: int = 10, contact_uuids: List[str] = None
) -> Generator[Note, None, None]:
    """
    Generate random note records.

    Args:
        num_notes: The number of notes to generate.
        contact_uuids: A list of contact UUIDs to optionally link to notes.

    Yields:
        A Note object with fake data.
    """
    fake = faker.Faker()
    if contact_uuids is None:
        contact_uuids = []

    for _ in range(num_notes):
        title = fake.sentence(nb_words=4)
        description = fake.paragraph(nb_sentences=3)

        num_tags = random.randint(1, 5)
        tags = [
            Tag(fake.pystr(min_chars=3, max_chars=10)) for _ in range(num_tags)
        ]

        note = Note(title, description, tags)

        # Optionally link note to a random contact
        if contact_uuids and random.choice([True, False]):
            note.contact_ids.add(random.choice(contact_uuids))

        yield note
