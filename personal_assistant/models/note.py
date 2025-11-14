from datetime import datetime
from typing import List


class Note:
    def __init__(self, caption: str, description: str = "", tags: List[str] = None):
        self.caption = caption.strip()
        self.creation_date = datetime.now()
        self.description = description.strip()
        self.tags = [tag.strip().lower()
                     for tag in (tags or []) if tag.strip()]

    def add_tag(self, tag: str):
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def matches(self, query: str) -> bool:
        query = query.lower()
        return (
            query in self.caption.lower() or
            query in self.description.lower() or
            any(query in tag for tag in self.tags)
        )

    def __str__(self) -> str:
        tags_str = ", ".join(self.tags) if self.tags else "no tags"
        return (
            f"Caption: {self.caption}\n"
            f"Created: {self.creation_date.strftime('%d.%m.%Y %H:%M')}\n"
            f"Description: {self.description or '—'}\n"
            f"Tags: {tags_str}"
        )
