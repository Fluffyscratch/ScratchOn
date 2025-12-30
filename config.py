"""
Bot configuration and constants.
"""

import discord
from discord.ext import commands
from itertools import cycle
import sys
import io

# Ensures proper utf-8 encoding for prints
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Bot setup
bot = commands.Bot(command_prefix="s ", intents=discord.Intents.all())

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

# The bot's theme colours
scratch_orange = discord.Color(0xF6AB3C)
scratch_gold = discord.Color(0xFFBE00)
scratch_blue = discord.Color(0x4E97FE)

# Embed for experimental commands
betaembed = discord.Embed(
    title="Sorry, this command is still in beta ! You cannot use it yet.",
    color=discord.Color.red(),
)

# Contributors and developers
contributors = ["EletrixTime", "TimMcCool", "AJustEpic"]
devs = ["Fluffygamer_", "kRxZy_kRxZy"]

# Global dictionary to store button states (for settings UI)
button_states = {}

# Memory storage for pending verifications (user_id: Verificator)
pending_verifiers: dict = {}
