"""
Scratch cloud → Discord bridge commands.

Handles communication with a BlockBit server using cloud variables.
"""

import asyncio

import interactions

from config import scratch_orange
from services import request_search, get_latest_response


class CurrencyCommands(interactions.Extension):
    """Currency / BlockBit commands."""

    @interactions.slash_command(
        name="blockbit_search",
        description="Search a Scratch user and get their BlockBit balance.",
    )
    @interactions.slash_option(
        name="username",
        description="Scratch username to get BlockBit balance",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def blockbit_search(self, ctx: interactions.SlashContext, username: str):
        """Communicates with the Scratch cloud project to retrieve a balance."""
        await ctx.defer()

        try:
            # Send request to Scratch
            request_search(username)

            # Wait briefly to allow Scratch to process the request
            await asyncio.sleep(1.2)

            # Fetch the response
            response = get_latest_response()

            if response is None:
                await ctx.send(
                    embed=interactions.Embed(
                        title="❌ No response",
                        description="Scratch did not respond in time. Try again.",
                        color=0xFF0000,
                    )
                )
                return

            await ctx.send(
                embed=interactions.Embed(
                    title="✅ Scratch Response",
                    description=f"```{username}``` has ```{response}``` Bits",
                    color=scratch_orange,
                )
            )

        except Exception as error:
            await ctx.send(
                embed=interactions.Embed(
                    title="⚠️ Error",
                    description=str(error),
                    color=0xFF0000,
                ),
                ephemeral=True,
            )


def setup(bot: interactions.Client):
    CurrencyCommands(bot)
