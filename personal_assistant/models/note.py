from datetime import datetime
from personal_assistant.models.field import Title, Tag
from personal_assistant.models.exceptions import TagAlreadyExistsError


class Note:
    def __init__(self, title: str, description: str = "", tags: list[Tag] = None):
        self.uuid = None
        self.title = Title(title)
        self.creation_date = datetime.now()
        self.description = description
        self.tags: list[Tag] = tags if tags is not None else []
        self.contact_ids: set[str] = set()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note if it doesn't already exist."""
        tag_obj = Tag(tag)
        # Check if tag already exists (case-insensitive)
        if any(t.value.lower() == tag_obj.value.lower() for t in self.tags):
            raise TagAlreadyExistsError(f"Tag '{tag}' already exists for this note")
        self.tags.append(tag_obj)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        for idx, t in enumerate(self.tags):
            if t.value.lower() == tag.lower():
                del self.tags[idx]
                return
        raise ValueError(f"Tag '{tag}' not found in this note")

    def update_title(self, new_title: str) -> None:
        """Update the note's title."""
        self.title = Title(new_title)

    def update_description(self, new_description: str) -> None:
        """Update the note's description."""
        self.description = new_description

    def __str__(self):
        tags_str = ", ".join(t.value for t in self.tags) if self.tags else "No tags"
        return f"Note: {self.title.value}\nCreated: {self.creation_date.strftime('%d.%m.%Y %H:%M')}\nDescription: {self.description}\nTags: {tags_str}"

    @classmethod
    def from_dict(cls, note_data):
        content = note_data.get("content") or note_data.get("description", "")
        tags = [Tag(tag) for tag in note_data.get("tags", []) if tag]
        note = cls(note_data["title"], content, tags)
        note.uuid = note_data.get("uuid")
        # note.creation_date = datetime.fromisoformat(note_data["creation_date"])
        note.contact_ids = set(note_data.get("contact_ids", []))
        return note

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "title": self.title.value,
            "creation_date": self.creation_date.isoformat(),
            # will be stored as 'content' in storage, may be will add 'description' as well
            "content": self.description,
            "tags": [tag.value for tag in self.tags],
            "contact_ids": list(self.contact_ids),
        }
