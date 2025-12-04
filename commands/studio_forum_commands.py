"""
Studio and forum-related slash commands.
"""
import discord
from discord import app_commands

import scratchattach as scratch

from config import bot, scratch_orange
from utils import limiter


@bot.tree.command(name="studio", description="Reads informations about a studio.")
async def studio(interact: discord.Interaction, studio: str):
    id = ''.join(filter(str.isdigit, studio))
    studio_obj = scratch.get_studio(id)
    
    if studio_obj.open_to_all:
        access = "Everyone"
    else:
        access = "Only curators"
    
    msg = discord.Embed(title=studio_obj.title)
    msg.set_image(url=studio_obj.image_url)
    msg.set_thumbnail(url=studio_obj.host().icon_url)
    desc = limiter(text=studio_obj.description, limit=500)

    msg.description = (
        f"Owned by **{studio_obj.host()}**, with id {studio_obj.host_id}\n"
        f"**{access}** can add projects.\n\n"
        "**This studio has :**\n"
        f"- {studio_obj.project_count} projects\n"
        f"- {studio_obj.follower_count} followers\n"
        f"- {studio_obj.manager_count} managers\n\n"
        f"**Description :**\n{desc}"
    )

    msg.set_footer(text=f"Studio id : {studio_obj.id}, link : https://scratch.mit.edu/studios/{studio_obj.id}")
    msg.color = scratch_orange

    await interact.response.send_message(embed=msg)


@bot.tree.command(name="forums", description="Check for topics in any forum category !")
@app_commands.choices(category=[
    app_commands.Choice(name="Announcements", value=5),
    app_commands.Choice(name="New Scratchers", value=6),
    app_commands.Choice(name="Help with Scripts", value=7),
    app_commands.Choice(name="Show and Tell", value=8),
    app_commands.Choice(name="Project Ideas", value=9),
    app_commands.Choice(name="Collaboration", value=10),
    app_commands.Choice(name="Requests", value=11),
    app_commands.Choice(name="Project Save & Level Codes", value=60),
    app_commands.Choice(name="Questions about scratch", value=4),
    app_commands.Choice(name="Suggestions", value=1),
    app_commands.Choice(name="Bugs and Glitches", value=3),
    app_commands.Choice(name="Advanced Topics", value=31),
    app_commands.Choice(name="Connecting to the Physical World", value=32),
    app_commands.Choice(name="Developing Scratch Extensions", value=48),
    app_commands.Choice(name="Open Source Projects", value=49),
    app_commands.Choice(name="Things I'm Making and Creating", value=29),
    app_commands.Choice(name="Things I'm Reading and Playing", value=30),
])
async def forums(interact: discord.Interaction, category: int):
    msg = discord.Embed(title="Topics in this category :", color=scratch_orange)
    desc = ""
    for item in scratch.get_topic_list(category_id=category, page=1):
        desc = (
            f"{desc}"
            f"\n\n**[{item.title}](https://scratch.mit.edu/discuss/topic/{item.id})** - "
            f"{item.reply_count} replies - {item.view_count} views (last update : {item.last_updated})"
        )
    msg.description = desc
    await interact.response.send_message(embed=msg)


@bot.tree.command(name="topic", description="Gives useful infos about a forum topic.")
async def topic(interact: discord.Interaction, topic: str):
    id = ''.join(filter(str.isdigit, topic))
    stopic = scratch.get_topic(id)
    msg = discord.Embed(title=stopic.title, color=scratch_orange)
    msg.description = (
        f"Link : https://scratch.mit.edu/discuss/topic/{stopic.id}\n"
        f"Category : {stopic.category_name}\n"
        f" Last updated : {stopic.last_updated}\n"
        f"Author : {stopic.first_post().author_name}\n"
        "First post :\n"
        f"```{stopic.first_post().content}```"
    )
    msg.set_thumbnail(url=stopic.first_post().author().icon_url)
    await interact.response.send_message(embed=msg)
