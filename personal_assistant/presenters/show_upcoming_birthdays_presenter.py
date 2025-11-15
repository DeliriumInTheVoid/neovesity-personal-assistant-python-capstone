from typing import TYPE_CHECKING
from datetime import datetime
from personal_assistant.presenters.presenter import Presenter
from personal_assistant.storage.address_book import AddressBookStorage

if TYPE_CHECKING:
    from personal_assistant.tui.app import AddressBookApp


class ShowUpcomingBirthdaysPresenter(Presenter):
    def __init__(self, storage: AddressBookStorage):
        self.storage = storage

    @property
    def name(self) -> str:
        return "birthdays"

    @property
    def description(self) -> str:
        return "Shows upcoming birthdays (next 7 days)"

    async def execute_tui(self, app: "AddressBookApp", args: list[str]) -> None:
        from personal_assistant.tui.screens.birthday import BirthdaysScreen
        from datetime import timedelta

        try:
            warn_in_days = int(args[0]) if args else 7
        except (ValueError, IndexError):
            warn_in_days = 7

        contacts = self.storage.get_all_records()
        today = datetime.now().date()
        warn_delta = timedelta(days=warn_in_days)
        end_date = today + warn_delta
        upcoming = []

        for contact in contacts:
            if not contact.birthday:
                continue

            bday = contact.birthday.value.date()
            this_year_bday = bday.replace(year=today.year)
            user_congratulation_date = None

            if today <= this_year_bday <= end_date:
                user_congratulation_date = this_year_bday
            elif this_year_bday < today:
                next_year_bday = bday.replace(year=today.year + 1)
                if today <= next_year_bday <= end_date:
                    user_congratulation_date = next_year_bday

            if user_congratulation_date:
                # Adjust for weekends
                if user_congratulation_date.weekday() in (5, 6):
                    user_congratulation_date += timedelta(days=(7 - user_congratulation_date.weekday()))

                # Recalculate days_until after potential weekend adjustment
                days_until = (user_congratulation_date - today).days

                # Ensure the adjusted date is still within the warning period
                if 0 <= days_until <= warn_in_days:
                    name = f"{contact.first_name.value} {contact.last_name.value if contact.last_name else ''}".strip()
                    birthday_str = user_congratulation_date.strftime("%d.%m.%Y")
                    upcoming.append((name, birthday_str, days_until))

        upcoming.sort(key=lambda x: x[2])

        await app.push_screen(BirthdaysScreen(upcoming))
