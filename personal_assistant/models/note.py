from datetime import datetime
from personal_assistant.models.field import Title, Tag
from personal_assistant.models.exceptions import TagAlreadyExistsError


class Note:
    def __init__(self, title: str, description: str = ""):
        self.title = Title(title)
        self.creation_date = datetime.now()
        self.description = description
        self.tags: list[Tag] = []

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

