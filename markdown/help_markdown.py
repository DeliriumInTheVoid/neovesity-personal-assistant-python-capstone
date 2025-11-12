HELP_MARKDOWN = """
# 📖 Address Book — Command Reference

Welcome to your friendly terminal assistant!  
Use the commands below to manage contacts, birthdays, and search your records.

---

## 🧩 Basic Commands

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`hello`** | Greet the bot and start interaction. | – |
| **`add-contact [name] [phone]`** | Add a new contact. If the name exists, adds another phone. | `name`: string <br>`phone`: 10 digits |
| **`change-contact [name] [old_value] [new_value]`** | Replace an old phone number with a new one. | `old_value`, `new_value`: 10 digits |
| **`phone [name]`** | Show all phone numbers for the specified contact. | `name`: string |
| **`all`** | Display all saved contacts in the book. | – |

---

## 🎂 Birthday Management

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`add-birthday [name] [DD.MM.YYYY]`** | Add or update a contact’s birthday. | `birthday`: date |
| **`show-birthday [name]`** | Show the birthday of a specific contact. | `name`: string |
| **`birthdays`** | List birthdays that occur within the next 7 days. | – |

---

## 🔍 Search & Utilities

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`search [query]`** | Search by part of name or phone number. | `query`: text |
| **`clear`** | Clear the log window. | – |
| **`help` / `F1`** | Show this help window. | – |
| **`escape`** | Close the help window. | – |
| **`close` / `exit` ** | Save all data and exit the program. | – |

---

💡 **Tips:**
- All commands are **case-insensitive**.  
- Press **F1** anytime to reopen this help window.  
- Don’t forget to **save** before exiting — but don’t worry, the bot does it automatically 😉  
"""
