from textual import events
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Static
from textual.screen import ModalScreen


class ConfirmationScreen(ModalScreen[bool]):
    """Screen to confirm an action."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Grid(
            Static(self.message, id="question"),
            Button("Yes", variant="error", id="yes"),
            Button("No", variant="primary", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_key(self, event: "events.Key") -> None:
        if event.key == "escape":
            self.dismiss(False)

