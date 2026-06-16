"""
Studio and forum-related slash commands.
"""

import interactions
import scratchattach as scratch

from config import scratch_orange
from utils import limiter


def _extract_id(raw: str) -> str:
    """Return only the digits from *raw* (works for IDs and URLs)."""
    return "".join(filter(str.isdigit, raw))


class StudioForumCommands(interactions.Extension):
    """Studio and forum slash commands."""

    @interactions.slash_command(
        name="studio",
        description="Reads information about a studio.",
    )
    @interactions.slash_option(
        name="studio",
        description="Studio ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def studio(self, ctx: interactions.SlashContext, studio: str) -> None:
        studio_id = _extract_id(studio)
        studio_obj = scratch.get_studio(studio_id)

        access = "Everyone" if studio_obj.open_to_all else "Only curators"
        desc = limiter(text=studio_obj.description, limit=500)

        embed = interactions.Embed(title=studio_obj.title)
        embed.set_image(url=studio_obj.image_url)
        embed.set_thumbnail(url=studio_obj.host().icon_url)
        embed.description = (
            f"Owned by **{studio_obj.host()}**, with id {studio_obj.host_id}\n"
            f"**{access}** can add projects.\n\n"
            "**This studio has :**\n"
            f"- {studio_obj.project_count} projects\n"
            f"- {studio_obj.follower_count} followers\n"
            f"- {studio_obj.manager_count} managers\n\n"
            f"**Description :**\n{desc}"
        )
        embed.set_footer(
            text=(
                f"Studio id : {studio_obj.id}, "
                f"link : https://scratch.mit.edu/studios/{studio_obj.id}"
            )
        )
        embed.color = scratch_orange
        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="forums",
        description="Check for topics in any forum category !",
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
    async def forums(self, ctx: interactions.SlashContext, category: int) -> None:
        lines: list[str] = []
        for item in scratch.get_topic_list(category_id=category, page=1):
            lines.append(
                f"\n\n**[{item.title}](https://scratch.mit.edu/discuss/topic/{item.id})** - "
                f"{item.reply_count} replies - {item.view_count} views "
                f"(last update : {item.last_updated})"
            )

        await ctx.send(
            embed=interactions.Embed(
                title="Topics in this category :",
                description="".join(lines),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="topic",
        description="Gives useful info about a forum topic.",
    )
    @interactions.slash_option(
        name="topic",
        description="Topic ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def topic(self, ctx: interactions.SlashContext, topic: str) -> None:
        topic_id = _extract_id(topic)
        topic_obj = scratch.get_topic(topic_id)

        embed = interactions.Embed(title=topic_obj.title, color=scratch_orange)
        embed.description = (
            f"Link : https://scratch.mit.edu/discuss/topic/{topic_obj.id}\n"
            f"Category : {topic_obj.category_name}\n"
            f"Last updated : {topic_obj.last_updated}\n"
            f"Author : {topic_obj.first_post().author_name}\n"
            "First post :\n"
            f"```{topic_obj.first_post().content}```"
        )
        embed.set_thumbnail(url=topic_obj.first_post().author().icon_url)
        await ctx.send(embed=embed)


def setup(bot: interactions.Client) -> None:
    StudioForumCommands(bot)
