HELP_MARKDOWN = """
# 📖 Address Book — Command Reference

Welcome to your friendly terminal assistant!  
Use the commands below to manage contacts, notes, birthdays, and search your records.

---

## 🧩 Contact Management

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`hello`** | Greet the bot and start interaction. | – |
| **`add-contact`** | Add a new contact using a form interface. | Interactive form |
| **`change-contact [name/UUID]`** | Edit an existing contact's information. | `name` or `UUID`: string |
| **`delete-contact [first_name] [last_name]`** | Delete a contact by name or UUID. | `first_name`: string <br>`last_name`: optional |
| **`phone [name]`** | Show all phone numbers for the specified contact. | `name`: string |
| **`all`** | Display all saved contacts in a table. | – |

---

## 🔍 Contact Search

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`search [query]`** | Search contacts by name. | `query`: text |
| **`search-phone [phone]`** | Search contacts by phone number. | `phone`: text |
| **`search-email [email]`** | Search contacts by email address. | `email`: text |

---

## 🎂 Birthday Management

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`show-birthday [name]`** | Show the birthday of a specific contact. | `name`: string |
| **`birthdays`** | List birthdays that occur within the next 7 days. | – |

---

## 📝 Notes Management

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`add-note`** | Create a new note using a form interface. | Interactive form |
| **`change-note [title/UUID]`** | Edit an existing note. | `title` or `UUID`: string |
| **`delete-note [title/UUID]`** | Delete a note by title or UUID. | `title` or `UUID`: string |
| **`all-notes`** | Display all saved notes in a table. | – |

---

## 🔎 Notes Search

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`search-notes [query]`** | Search notes by title or content. | `query`: text |
| **`search-tag [tag]`** | Search notes by tag. | `tag`: text |

---

## 🛠️ Utilities

| Command | Description | Attributes |
|----------|--------------|-------------|
| **`generate-data`** | Generate random demo contacts and notes. | – |
| **`clear`** | Clear the log window. | – |
| **`help` / `F1`** | Show this help window. | – |
| **`escape`** | Close the help window. | – |
| **`close` / `exit`** | Save all data and exit the program. | – |

---

💡 **Tips:**
- All commands are **case-insensitive**.  
- Press **F1** anytime to reopen this help window.  
- Use **Tab** for command auto-completion.  
- When multiple items match your search, you'll be prompted for more specific criteria.  
- Don't forget to **save** before exiting — but don't worry, the bot does it automatically 😉  
"""

