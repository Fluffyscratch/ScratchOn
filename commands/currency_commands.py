"""
Thanks To OpenAI for Comments

Scratch cloud → Discord bridge commands.

Handles communication with a BlockBit server using cloud variables.
"""

import asyncio

import discord
from discord import app_commands

from config import bot, scratch_orange
from services import request_search, get_latest_response

@bot.tree.command(
    name="blockbit_search",
    description="Search a Scratch user and get their BlockBit balance.",
)
@app_commands.describe(username="Scratch username to get BlockBit balance")
async def blockbit_search(interact: discord.Interaction, username: str):
    """
    Discord slash command that communicates with the Scratch cloud project.
    """
    await interact.response.defer()

    # Send request to Scratch
    request_search(username)

    # Wait briefly to allow Scratch to process the request
    await asyncio.sleep(1.2)

    # Fetch the response
    response = get_latest_response()

    if response is None:
        await interact.followup.send(
            embed=discord.Embed(
                title="❌ No response",
                description="Scratch did not respond in time. Try again.",
                color=discord.Color.red(),
            )
        )
        return

    await interact.followup.send(
        embed=discord.Embed(
            title="✅ Scratch Response",
            description=f"```{username}``` has ```{response}``` Bits",
            color=scratch_orange,
        )
    )

"""
Error Handling During Search 
"""
@blockbit_search.error
async def search_error(
    interact: discord.Interaction, error: app_commands.AppCommandError
):
    await interact.response.send_message(
        embed=discord.Embed(
            title="⚠️ Error",
            description=str(error),
            color=discord.Color.red(),
        ),
        ephemeral=True,
    )
