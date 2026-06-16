"""
Traditional prefix commands (non-slash).
"""

import interactions
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext


class PrefixCommands(interactions.Extension):
    """Prefix command extension (triggered with the "s " prefix)."""

    @prefixed_command(name="ping")
    async def ping(self, ctx: PrefixedContext):
        """Returns the bot's current latency."""
        msg = interactions.Embed(title="🏓 Pong !", description="Latency in ms :")
        msg.add_field(
            name=f"{self.bot.user.username}'s Latency (ms): ",
            value=f"{round(self.bot.latency * 1000)}ms.",
            inline=False,
        )
        msg.set_footer(
            text=f"Requested by {ctx.author.username}",
            icon_url=ctx.author.display_avatar.url,
        )
        msg.color = 0xA84300  # dark orange
        await ctx.send(embed=msg)


def setup(bot: interactions.Client):
    PrefixCommands(bot)
