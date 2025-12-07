"""
Thanks To OpenAI for Comments

Scratch cloud → Discord bridge commands.

Handles communication with a BlockBit server using cloud variables.
"""

import asyncio
import scratchattach as sa
from scratchattach import Encoding

import websockets
import json

import discord
from discord import app_commands

from config import bot, scratch_orange

# Login to Scratch
session = sa.login("USERNAME", "PASSWORD")

# Connect to the Scratch project's cloud variables
cloud = session.connect_cloud(669020072)
latest_value = 1
def request_search(username: str):
    """
    Send a request to Scratch asking for a user's balance or data.

    The Scratch project listens for messages in the TO_HOST variable.
    """
    cloud.set_var("TO_HOST", Encoding.encode(f"search&{username}"))

async def get_response():
    global latest_value
    async with websockets.connect('wss://clouddata.scratch.mit.edu') as ws:
        await ws.send(json.dumps({"method": "handshake", "project_id": 669020072}))
        while True:
            message = json.loads(await ws.recv())
            if message.get("method") == "variables":
                variables = Encoding.decode(message.get("variables", {}))
                if variables:
                    # Get the last variable value received
                    last_var = list(variables.values())[-1]
                    latest_value = last_var

def get_latest_response() -> int | str | None:
    """
    Get the most recent response sent back by the Scratch project.

    If the response is a number, return it as an int. Otherwise, return it as a string.
    """
    await get_response()
    return float(latest_value) if latest_value is not None else None


@bot.tree.command(
    name="blockbit_search",
    description="Search a Scratch user via Scratch cloud variables."
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

@search.error
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
