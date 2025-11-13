from textual.screen import Screen

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, MarkdownViewer

from personal_assistant.tui.screens.help.markdown import HELP_MARKDOWN


class HelpScreen(Screen):
    """
    Modal screen showing help.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Close Help"),
        ("f1", "show_help", None),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            MarkdownViewer(HELP_MARKDOWN, show_table_of_contents=True),
            id="help_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus on the scroll widget"""
        self.query_one(MarkdownViewer).focus()
