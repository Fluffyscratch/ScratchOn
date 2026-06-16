"""
Traditional prefix commands (non-slash).
"""

import interactions
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext


class PrefixCommands(interactions.Extension):
    """Prefix command extension (triggered with the 's ' prefix)."""

    @prefixed_command(name="ping")
    async def ping(self, ctx: PrefixedContext) -> None:
        """Return the bot's current latency."""
        latency_ms = round(self.bot.latency * 1000)

        embed = interactions.Embed(
            title="Pong !",
            description="Latency in ms :",
            color=0xA84300,
        )
        embed.add_field(
            name=f"{self.bot.user.username}'s Latency (ms): ",
            value=f"{latency_ms}ms.",
            inline=False,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.username}",
            icon_url=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)


def setup(bot: interactions.Client) -> None:
    PrefixCommands(bot)
