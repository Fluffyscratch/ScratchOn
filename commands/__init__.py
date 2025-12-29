"""
Command modules - imports all commands to register them with the bot.
"""

# Import all command modules to register their commands
from . import user_commands
from . import project_commands
from . import studio_forum_commands
from . import search_commands
from . import utility_commands
from . import experimental_commands
from . import prefix_commands
from . import currency_commands

__all__ = [
    "user_commands",
    "project_commands",
    "studio_forum_commands",
    "search_commands",
    "utility_commands",
    "experimental_commands",
    "prefix_commands",
    "currency_commands",
]
