from typing import Tuple, Deque
from collections import deque


def parse_input(user_input: str) -> (Tuple[str, list[str]]):
    user_input_strip = user_input.strip()
    if not user_input_strip:
        return "empty", []

    command, *args = user_input_strip.split()
    command = command.lower()

    if not command:
        command = "empty"

    if not args:
        args = []

    if command in ["exit", "quit", "q", "close"]:
        command = "exit"

    return command, args


class ArgsParser:
    """
    A simple argument parser that allows sequential access to command arguments.
    It supports getting the next argument, checking if more arguments are available,
    and retrieving all remaining arguments as a single string.
    """

    def __init__(self, args: list[str]):
        self.args:Deque[str] = deque(args)

    def get_next(self) -> str:
        """
        Get the next argument from the list.
        Raises IndexError if there are no more arguments.
        """
        if not self.args:
            # @input_error decorator in commands.py will catch this
            raise IndexError("Not enough arguments provided")

        return self.args.popleft()

    def get_all_remaining_as_str(self) -> str:
        """
        Get all remaining arguments as a single string.
        Raises IndexError if there are no more arguments.
        """
        if not self.args:
            raise IndexError("Not enough arguments provided")

        remaining = " ".join(self.args)
        self.args.clear()
        return remaining

    def has_next(self) -> bool:
        """
        Check if there are more arguments available.
        Returns True if there are more arguments, False otherwise.
        """
        return len(self.args) > 0
