"""
ScratchOn Discord Bot - Main Entry Point

A Discord bot for the Scratch community, providing various utilities
for interacting with the Scratch API.
"""

from interactions.ext.prefixed_commands import setup as setup_prefixed
from config import bot

# Enable prefix command support with the "s " prefix
setup_prefixed(bot, default_prefix="s ")

# Load event handlers extension
bot.load_extension("events.bot_events")

# Load all slash-command extensions
bot.load_extension("commands.user_commands")
bot.load_extension("commands.project_commands")
bot.load_extension("commands.studio_forum_commands")
bot.load_extension("commands.search_commands")
bot.load_extension("commands.utility_commands")
bot.load_extension("commands.experimental_commands")
bot.load_extension("commands.prefix_commands")
bot.load_extension("commands.currency_commands")

# Attach Top.gg integration (registers its own listeners on `bot`)
# import topGG

# topGG.attach_to_bot(bot)


def main():
    """Run the bot."""
    with open("private/token.txt") as f:
        token = f.readlines()[0].strip()
    bot.start(token)


if __name__ == "__main__":
    main()
