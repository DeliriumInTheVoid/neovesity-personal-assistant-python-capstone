from personal_assistant.cli.contacts_bot import start_bot
from personal_assistant.utils.random_address_book import generate_address_book

def main():
    while True:
        print("\n************ MENU ************")
        print("1. Contacts Bot")
        print("2. Generate Address Book")
        print("0. Exit")

        choice = input("Select an option: ")
        if choice == "1":
            start_bot()
        elif choice == "2":
            num_contacts = input("Enter number of contacts to generate: ")
            try:
                num_contacts = int(num_contacts)
                if num_contacts <= 0:
                    raise ValueError("Number must be positive.")
            except ValueError as e:
                print(f"Invalid input: {e}")
                continue

            address_book = generate_address_book(num_contacts)
            start_bot(address_book)
        elif choice == "0":
            print("End")
            break


if __name__ == "__main__":
    main()
