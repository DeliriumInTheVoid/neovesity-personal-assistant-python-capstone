# Personal Assistant - Python Capstone Project

A feature-rich personal assistant application for managing contacts and notes with an elegant Terminal User Interface (TUI). Built with Python and Textual framework, featuring intelligent indexing for lightning-fast search operations.

## 🎯 Features

### Contact Management
- ✅ **Add Contacts** - Create contacts with first name, last name, multiple phone numbers, email, birthday, and address
- ✅ **Update Contacts** - Edit any contact information including phones, email, birthday, and address
- ✅ **Delete Contacts** - Remove contacts with confirmation
- ✅ **Search Contacts** - Find contacts by:
  - First name (prefix search)
  - Last name (prefix search)
  - Phone number (exact match)
  - Email address (exact match)
- ✅ **Birthday Tracking** - View upcoming birthdays within a specified timeframe
- ✅ **Phone Number Validation** - Automatic Ukrainian phone number normalization to MSISDN format (+380XXXXXXXXX)
- ✅ **Email Validation** - Built-in email format validation

### Note Management
- ✅ **Create Notes** - Add notes with title, description, and multiple tags
- ✅ **Update Notes** - Edit note title, description, and manage tags
- ✅ **Delete Notes** - Remove notes with confirmation
- ✅ **Search Notes** - Find notes by:
  - Title (partial match)
  - Tags (exact tag match)
- ✅ **Tag Management** - Add and remove tags from notes

### User Interface
- 🎨 **Beautiful TUI** - Rich terminal interface powered by Textual
- 🔍 **Auto-Suggestions** - Command input with intelligent suggestions
- 📊 **Data Tables** - View contacts and birthdays in sortable tables
- 🎹 **Keyboard Shortcuts** - Quick access with `Ctrl+Q` to quit, `F1` for help
- 📝 **Rich Logging** - Color-coded output with emojis for better UX

### Data Persistence & Indexing
- 💾 **JSON Storage** - Each record stored as individual JSON file with UUID
- 🚀 **High-Performance Indexing** - Trie and hash indexes for instant search
- 🔒 **Atomic Operations** - Safe file operations using atomic rename pattern
- 🔄 **Auto-Sync** - Indexes automatically synchronized with data changes
- 📁 **Dual Mode** - Separate test and production data directories

### Additional Features
- 🎲 **Demo Data Generator** - Generate random contacts and notes using Faker
- 🛡️ **Error Handling** - Comprehensive validation and error messages
- 🧪 **Test Mode** - Safe sandbox environment for testing
- 🏗️ **Extensible Architecture** - Presenter pattern for easy command addition

## 📋 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install in Development Mode

For development and testing (recommended):

```bash
pip install -e .
```

### Install in Production Mode

For regular use:

```bash
pip install .
```

### Install with Development Dependencies

To install with testing tools:

```bash
pip install -e ".[dev]"
```

## 🚀 Usage

### Starting the Application

After installation, run the personal assistant:

```bash
personal-assistant
```

### Application Modes

#### Test Mode (Default)
Uses `demo_data/` and `demo_index/` directories:
```bash
personal-assistant --test
```

#### Release Mode
Uses production directories (`~/.assistant/data` and `~/.assistant/index`):
```bash
personal-assistant --release
```

### Environment Variables

Set mode via environment variable:
```bash
ASSISTANT_MODE=test personal-assistant
ASSISTANT_MODE=release personal-assistant
```

### Alternative: Run Without Installation

Execute directly from source:
```bash
python -m personal_assistant.main
```

## 📖 Available Commands

### General Commands
| Command | Description |
|---------|-------------|
| `hello` | Display a greeting message |
| `help` | Show all available commands and their descriptions |
| `clear` | Clear the terminal output |
| `exit`, `quit`, `q`, `close` | Save and exit the application |

### Contact Commands
| Command | Arguments | Description |
|---------|-----------|-------------|
| `add-contact` | - | Open interactive form to add a new contact |
| `change-contact` | `<first_name>` | Open interactive form to edit contact details |
| `delete-contact` | `<first_name>` | Delete a contact (with confirmation) |
| `all` | - | Display all contacts in a table view |
| `phone` | `<first_name>` | Show all phone numbers for a contact |
| `search` | `<name_prefix>` | Search contacts by first or last name prefix |
| `search-phone` | `<phone_number>` | Find contact by phone number |
| `search-email` | `<email>` | Find contact by email address |
| `show-birthday` | `<first_name>` | Display birthday of a specific contact |
| `birthdays` | `[days]` | Show upcoming birthdays (default: 7 days) |

### Note Commands
| Command | Arguments | Description |
|---------|-----------|-------------|
| `add-note` | - | Open interactive form to create a new note |
| `change-note` | `<title>` | Open interactive form to edit a note |
| `delete-note` | `<title>` | Delete a note (with confirmation) |
| `all-notes` | - | Display all notes |
| `search-notes` | `<query>` | Search notes by title (partial match) |
| `search-tag` | `<tag>` | Find all notes with a specific tag |

### Utility Commands
| Command | Arguments | Description |
|---------|-----------|-------------|
| `generate-data` | `[num_contacts] [num_notes]` | Generate random demo data |

## 🏗️ Architecture

The application follows a clean, modular architecture with clear separation of concerns:

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     TUI Layer (Textual)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Main Screen  │  │ Form Screens │  │ Table Views  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                   Presenter Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Contact    │  │     Note     │  │    Search    │ │
│  │  Presenters  │  │  Presenters  │  │  Presenters  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                     Model Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ AddressBook  │  │  NotesBook   │  │   Record     │ │
│  │              │  │              │  │   & Note     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                   Storage Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ AddressBook  │  │    Notes     │  │    Index     │ │
│  │   Storage    │  │   Storage    │  │   Manager    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │ HeapStorage  │  │ BaseStorage  │                   │
│  └──────────────┘  └──────────────┘                   │
└───────────────────────────────────────────────────────┘
```

### Directory Structure

```
personal_assistant/
├── __init__.py
├── main.py                 # Application entry point
├── config.py               # Configuration management (modes, paths)
├── cli/
│   ├── args_parsers.py    # Command-line argument parsing
│   └── __init__.py
├── models/
│   ├── address_book.py    # AddressBook collection
│   ├── notes_book.py      # NotesBook collection
│   ├── record.py          # Contact record model
│   ├── note.py            # Note model
│   ├── field.py           # Field validators (Name, Phone, Email, etc.)
│   ├── exceptions.py      # Custom exceptions
│   └── __init__.py
├── storage/
│   ├── base_storage.py    # Abstract base storage class
│   ├── address_book.py    # Contact storage implementation
│   ├── notes_storage.py   # Note storage implementation
│   ├── heap_storage.py    # File-based JSON storage
│   ├── index_manager.py   # Indexing system (Trie & Hash indexes)
│   ├── constants.py       # Storage constants
│   └── __init__.py
├── presenters/
│   ├── presenter.py       # Abstract presenter base class
│   ├── presenters_registry.py  # Command registry
│   ├── hello_presenter.py
│   ├── add_contact_presenter.py
│   ├── change_contact_presenter.py
│   ├── delete_contact_presenter.py
│   ├── search_contacts_presenter.py
│   ├── search_contacts_by_phone_presenter.py
│   ├── search_contacts_by_email_presenter.py
│   ├── show_all_presenter.py
│   ├── show_phone_presenter.py
│   ├── show_birthday_presenter.py
│   ├── show_upcoming_birthdays_presenter.py
│   ├── add_note_presenter.py
│   ├── change_note_presenter.py
│   ├── delete_note_presenter.py
│   ├── search_notes_presenter.py
│   ├── search_notes_by_tag_presenter.py
│   ├── show_all_notes_presenter.py
│   ├── generate_data_presenter.py
│   ├── show_help_presenter.py
│   └── __init__.py
├── tui/
│   ├── app.py             # Main Textual application
│   ├── screens/
│   │   ├── add_contact.py      # Contact form screen
│   │   ├── note_form.py        # Note form screen
│   │   ├── all_contacts.py     # Contact table screen
│   │   ├── birthday.py         # Birthday table screen
│   │   ├── confirmation_screen.py  # Confirmation dialog
│   │   ├── help/
│   │   │   └── help.py         # Help screen
│   │   └── __init__.py
│   └── __init__.py
└── utils/
    ├── random_address_book.py  # Demo data generator
    └── __init__.py
```

### Core Components

#### 1. **Configuration Layer** (`config.py`)
- `AppConfig`: Manages application mode (test/release) and storage paths
- Automatically creates necessary directories
- Test mode: `demo_data/`, `demo_index/`
- Release mode: `~/.assistant/data`, `~/.assistant/index`

#### 2. **Model Layer**
- **AddressBook**: Collection of contact records (UserDict-based)
- **NotesBook**: Collection of notes (UserDict-based)
- **Record**: Contact model with fields (name, phones, email, birthday, address)
- **Note**: Note model with title, description, tags, creation date
- **Field Classes**: Validators for Name, Phone, Email, Birthday, Address, Title, Tag

#### 3. **Storage Layer**

##### HeapStorage
- File-based storage where each entity is a separate JSON file
- UUID-based filenames for uniqueness
- Atomic write operations using temporary files and rename
- Structure: `data/contacts/{uuid}.json`, `data/notes/{uuid}.json`

##### IndexManager
Implements two types of indexes for high-performance search:

**Trie Indexes** (for prefix search):
- `contact_first_name/`: Two-level directory structure (first letter / second letter)
- `contact_last_name/`: Same structure
- Enables fast prefix searches (e.g., "Jo" finds "John", "Joan", "Joseph")
- Example: `index/contact_first_name/j/o.json` contains all names starting with "jo"

**Hash Indexes** (for exact search):
- `contact_phone/`: Phone number lookups
- `contact_email/`: Email address lookups
- `note_tag/`: Tag-based note search
- `note_title/`: Title-based note search
- Uses hash partitioning for balanced distribution

##### BaseStorage
- Abstract base class for storage operations
- Provides common CRUD operations
- Automatically manages index synchronization
- Template method pattern for entity-specific logic

##### AddressBookStorage & NotesStorage
- High-level APIs for managing contacts and notes
- Extend BaseStorage with specific search methods
- Ensure data-index consistency

#### 4. **Presenter Layer**
- **Presenter Pattern**: Separates business logic from UI
- Each command has a dedicated presenter class
- Async execution for non-blocking UI
- Registry pattern for command discovery
- Easy to extend with new commands

#### 5. **TUI Layer** (Textual Framework)
- **Main App** (`AddressBookApp`): Central application controller
- **Screens**: Modal screens for forms and tables
  - `AddContactScreen`: Contact creation/editing form
  - `NoteFormScreen`: Note creation/editing form
  - `AllContactsScreen`: Sortable contact table
  - `BirthdaysScreen`: Upcoming birthdays table
  - `ConfirmationScreen`: Yes/No dialog
  - `HelpScreen`: Command reference
- **Widgets**: Input, RichLog, DataTable, Header, Footer
- **CSS Styling**: Custom styling for professional appearance

### Key Design Patterns

1. **Repository Pattern**: Storage layer abstracts data access
2. **Presenter Pattern**: Separates presentation logic from UI
3. **Template Method**: BaseStorage provides algorithm skeleton
4. **Strategy Pattern**: Different index strategies (Trie vs Hash)
5. **Factory Pattern**: Record/Note creation from dictionaries
6. **Singleton Pattern**: AppConfig class-level state
7. **Registry Pattern**: Command registration and lookup

### Data Flow

1. **User Input** → TUI receives command
2. **Parsing** → Command parser extracts command and arguments
3. **Presenter** → Registry finds and executes appropriate presenter
4. **Model** → Presenter creates/updates model objects
5. **Storage** → Model persisted to HeapStorage
6. **Indexing** → IndexManager updates relevant indexes
7. **Response** → TUI displays result to user

### Indexing Strategy

#### Why Indexing?
Without indexes, searching requires scanning all files (O(n) complexity). With indexes:
- Prefix search: O(1) to find the right index file, then O(k) for matching entries
- Exact search: O(1) hash lookup
- Dramatic performance improvement for large datasets

#### Index Synchronization
- Indexes updated atomically with data changes
- Add operation: Update data file → Add to indexes
- Update operation: Remove from old indexes → Update data → Add to new indexes
- Delete operation: Remove from indexes → Delete data file
- Ensures consistency even if operation interrupted

### Error Handling

- **Custom Exceptions**: Domain-specific errors (PhoneAlreadyExistsError, NoteNotFoundError, etc.)
- **Validation**: Input validation at field level (Phone, Email, Birthday)
- **User-Friendly Messages**: Clear error messages in TUI
- **Graceful Degradation**: Corrupted index files recreated on demand

## 🧪 Development

### Running Tests

Execute the test suite:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_contacts_bot.py
```

### Adding New Commands

1. Create a new presenter in `personal_assistant/presenters/`:
   ```python
   from personal_assistant.presenters.presenter import Presenter
   
   class MyCommandPresenter(Presenter):
       @property
       def name(self) -> str:
           return "my-command"
       
       @property
       def description(self) -> str:
           return "Description of what it does"
       
       async def execute_tui(self, app, args):
           # Implementation
           pass
   ```

2. Register in `presenters_registry.py`:
   ```python
   self.commands['my-command'] = MyCommandPresenter(storage)
   ```

3. Add to suggestions in `tui/app.py`:
   ```python
   INPUT_SUGGESTIONS = [
       # ... existing commands
       "my-command",
   ]
   ```

### Project Dependencies

- **textual==6.6.0**: Terminal UI framework
- **faker>=18.9.0**: Demo data generation
- **pytest>=8.4.2**: Testing framework (dev)

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

This is a capstone project for NeoVersity. For educational purposes.

## 📚 Additional Documentation

- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [LICENSE](LICENSE) - License information

---

**Built with ❤️ using Python and Textual**

