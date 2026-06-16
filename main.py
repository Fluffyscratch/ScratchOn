"""
ScratchOn Discord Bot — Main Entry Point

A Discord bot for the Scratch community, providing various utilities
for interacting with the Scratch API.
"""

import os

from dotenv import load_dotenv
from interactions.ext.prefixed_commands import setup as setup_prefixed

from config import bot

load_dotenv()


def main() -> None:
    """Run the bot."""
    setup_prefixed(bot, default_prefix="s ")

    bot.load_extension("events.bot_events")

    bot.load_extension("commands.user_commands")
    bot.load_extension("commands.project_commands")
    bot.load_extension("commands.studio_forum_commands")
    bot.load_extension("commands.search_commands")
    bot.load_extension("commands.utility_commands")
    # bot.load_extension("commands.experimental_commands")
    bot.load_extension("commands.prefix_commands")
    bot.load_extension("commands.currency_commands")

    import topGG

    topGG.attach_to_bot(bot)

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")
    bot.start(token)


if __name__ == "__main__":
    main()
