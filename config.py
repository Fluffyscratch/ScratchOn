"""
Bot configuration and constants.
"""

import io
import sys
from itertools import cycle

import interactions

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------------------------------------------------------------------------
# Bot instance
# ---------------------------------------------------------------------------

bot = interactions.Client(intents=interactions.Intents.ALL)

# ---------------------------------------------------------------------------
# Statuses the bot cycles through
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Theme colours (plain hex integers — interactions.py accepts these directly)
# ---------------------------------------------------------------------------

scratch_orange: int = 0xF6AB3C
scratch_gold: int = 0xFFBE00
scratch_blue: int = 0x4E97FE

# ---------------------------------------------------------------------------
# Reusable embeds
# ---------------------------------------------------------------------------

betaembed = interactions.Embed(
    title="Sorry, this command is still in beta ! You cannot use it yet.",
    color=0xFF0000,
)

# ---------------------------------------------------------------------------
# Contributors / developers
# ---------------------------------------------------------------------------

contributors: list[str] = ["EletrixTime", "TimMcCool", "AJustEpic"]
devs: list[str] = ["Fluffygamer_", "kRxZy_kRxZy"]

# ---------------------------------------------------------------------------
# Shared mutable state (settings UI button styles)
# ---------------------------------------------------------------------------

button_states: dict[str, interactions.ButtonStyle] = {}
pending_verifiers: dict[int, object] = {}
