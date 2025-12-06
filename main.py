"""
ScratchOn Discord Bot - Main Entry Point

A Discord bot for the Scratch community, providing various utilities
for interacting with the Scratch API.
"""

# Import configuration (sets up bot instance)
from config import bot

# Import and setup events
from events import setup_events

# Import all commands (this registers them with the bot)
import commands

# Setup event handlers
setup_events()

# Attach Top.gg integration (uses the existing `bot` instance)
import topGG

topGG.attach_to_bot(bot)


def main():
    """Run the bot."""
    with open("ScratchOn_private/token.txt") as f:
        token = f.readlines()[0].strip()
    bot.run(token)


if __name__ == "__main__":
    main()
