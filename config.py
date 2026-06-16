"""
Bot configuration and constants.
"""

import interactions
from itertools import cycle
import sys
import io

# Ensures proper utf-8 encoding for prints
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Bot setup
bot = interactions.Client(intents=interactions.Intents.ALL)

# The statuses the bot will cycle through
bot_statuses = cycle(
    [
        "Scratch API",
        "Scratchattach",
        "Need help ? Do /help :)",
        "PFP by AJustEpic",
        "Check out Fluffygamer_ on Scratch !",
        "Watch Fluffyscratch on Youtube !",
    ]
)

# The bot's theme colours (plain hex integers — interactions.py accepts these directly)
scratch_orange = 0xF6AB3C
scratch_gold = 0xFFBE00
scratch_blue = 0x4E97FE

# Embed for experimental commands
betaembed = interactions.Embed(
    title="Sorry, this command is still in beta ! You cannot use it yet.",
    color=0xFF0000,
)

# Contributors and developers
contributors = ["EletrixTime", "TimMcCool", "AJustEpic"]
devs = ["Fluffygamer_", "kRxZy_kRxZy"]

# Global dictionary to store button states (for settings UI)
# Values are interactions.ButtonStyle members
button_states = {}

# Memory storage for pending verifications (user_id: Verificator)
pending_verifiers: dict = {}
