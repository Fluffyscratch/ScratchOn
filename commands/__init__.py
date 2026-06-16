"""
Command modules.

All command modules are loaded as Extensions from main.py via:
    bot.load_extension("commands.<module_name>")
"""

__all__: list[str] = [
    "user_commands",
    "project_commands",
    "studio_forum_commands",
    "search_commands",
    "utility_commands",
    "experimental_commands",
    "prefix_commands",
    "currency_commands",
]
