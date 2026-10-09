"""
Studio and forum-related slash commands.
"""

import interactions

import scratchattach as scratch

from config import scratch_orange
from utils import studio_embed


class StudioForumCommands(interactions.Extension):
    """Studio and forum slash commands."""

    @interactions.slash_command(
        name="studio",
        description="Gets informations about a studio.",
    )
    @interactions.slash_option(
        name="studio",
        description="Studio ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def studio(self, ctx: interactions.SlashContext, studio: str):
        msg = studio_embed(studio)
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="forums",
        description="Check for topics in any forum category!",
    )
    @interactions.slash_option(
        name="category",
        description="Forum category",
        opt_type=interactions.OptionType.INTEGER,
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="Announcements", value=5),
            interactions.SlashCommandChoice(name="New Scratchers", value=6),
            interactions.SlashCommandChoice(name="Help with Scripts", value=7),
            interactions.SlashCommandChoice(name="Show and Tell", value=8),
            interactions.SlashCommandChoice(name="Project Ideas", value=9),
            interactions.SlashCommandChoice(name="Collaboration", value=10),
            interactions.SlashCommandChoice(name="Requests", value=11),
            interactions.SlashCommandChoice(
                name="Project Save & Level Codes", value=60
            ),
            interactions.SlashCommandChoice(name="Questions about scratch", value=4),
            interactions.SlashCommandChoice(name="Suggestions", value=1),
            interactions.SlashCommandChoice(name="Bugs and Glitches", value=3),
            interactions.SlashCommandChoice(name="Advanced Topics", value=31),
            interactions.SlashCommandChoice(
                name="Connecting to the Physical World", value=32
            ),
            interactions.SlashCommandChoice(
                name="Developing Scratch Extensions", value=48
            ),
            interactions.SlashCommandChoice(name="Open Source Projects", value=49),
            interactions.SlashCommandChoice(
                name="Things I'm Making and Creating", value=29
            ),
            interactions.SlashCommandChoice(
                name="Things I'm Reading and Playing", value=30
            ),
        ],
    )
    async def forums(self, ctx: interactions.SlashContext, category: int):
        msg = interactions.Embed(
            title="Topics in this category:", color=scratch_orange
        )
        desc = ""
        for item in scratch.get_topic_list(category_id=category, page=1):
            desc = (
                f"{desc}"
                f"\n\n**[{item.title}](https://scratch.mit.edu/discuss/topic/{item.id})** - "
                f"{item.reply_count} replies - {item.view_count} views "
                f"(last update : {item.last_updated})"
            )
        msg.description = desc
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="topic",
        description="Gives useful infos about a forum topic.",
    )
    @interactions.slash_option(
        name="topic",
        description="Topic ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def topic(self, ctx: interactions.SlashContext, topic: str):
        id = "".join(filter(str.isdigit, topic))
        stopic = scratch.get_topic(id)
        first_post = stopic.first_post()
        msg = interactions.Embed(title=stopic.title, color=scratch_orange)
        msg.description = (
            f"Link: https://scratch.mit.edu/discuss/topic/{stopic.id}\n"
            f"Category: {stopic.category_name}\n"
            f"Last updated: {stopic.last_updated}\n"
            f"Author: [{first_post.author_name}](https://scratch.mit.edu/users/{first_post.author_name})\n"
            "First post:\n"
            f"```{first_post.content}```"
        )
        msg.set_thumbnail(url=first_post.author().icon_url)
        await ctx.send(embed=msg)


def setup(bot: interactions.Client):
    StudioForumCommands(bot)
