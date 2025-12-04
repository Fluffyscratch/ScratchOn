"""
Traditional prefix commands (non-slash).
"""
import discord

from config import bot


@bot.command()
async def ping(ctx):
    """Returns bot latency."""
    msg = discord.Embed(title="🏓 Pong !", description="Latency in ms :")
    msg.add_field(
        name=f"{bot.user.name}'s Latency (ms): ",
        value=f"{round(bot.latency * 1000)}ms.",
        inline=False
    )
    msg.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)
    msg.color = discord.Color.dark_orange()
    await ctx.send(embed=msg)
