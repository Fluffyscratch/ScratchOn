"""
Project-related slash commands.
"""

import os
import discord
from discord import app_commands
from datetime import datetime

import scratchattach as scratch

from config import bot, scratch_orange
from utils import limiter


@bot.tree.command(
    name="modstatus", description="Tells if a project is either FE or NFE."
)
async def modstatus(interact: discord.Interaction, project: str):
    id = "".join(filter(str.isdigit, project))
    project_obj = scratch.get_project(id)

    modstatus = project_obj.moderation_status()
    embeded_msg = discord.Embed(title="This project is...")

    if modstatus == "notsafe":
        embeded_msg.description = (
            "<:Nope:1333795409403052032>Not Safe (NFE) !<:Nope:1333795409403052032>"
        )
        embeded_msg.color = discord.Color.red()
    elif modstatus == "safe":
        embeded_msg.description = (
            "<:Verified:1333795453250175058>Safe (FE) !<:Verified:1333795453250175058>"
        )
        embeded_msg.color = discord.Color.green()
    else:
        embeded_msg.description = "<:forumneutral:1341109236679053312>Not Reviewed (counts as FE) !<:forumneutral:1341109236679053312>"
        embeded_msg.color = discord.Color.light_grey()

    embeded_msg.set_footer(text=f"Project ID : {id}")
    await interact.response.send_message(embed=embeded_msg)


@bot.tree.command(
    name="embed",
    description="Gives an embeded version of the specified project, mainly for websites.",
)
async def embed(interact: discord.Interaction, project: str):
    id = "".join(filter(str.isdigit, project))
    project_obj = scratch.get_project(id)

    link = project_obj.embed_url
    embeded_msg = discord.Embed(
        title="This project is now embedded ! <:embed:1343565862077988904>",
        description=f"🔗 Link : {link}",
        color=scratch_orange,
    )

    await interact.response.send_message(embed=embeded_msg)


@bot.tree.command(
    name="project", description="Gets a lot of informations about a project."
)
async def project(interact: discord.Interaction, project: str):
    id = "".join(filter(str.isdigit, project))
    project_obj = scratch.get_project(id)

    msg = discord.Embed(title=f"{project_obj.title} :")

    # Fields are used for project statistics
    msg.add_field(name="Views :", value=f"{project_obj.views} :eye:")
    msg.add_field(name="Loves :", value=f"{project_obj.loves} :heart:")
    msg.add_field(name="Faves :", value=f"{project_obj.favorites} :star:")
    msg.add_field(
        name="Loves per view :",
        value=f"{round(project_obj.loves / project_obj.views, 2)} :heart: / :eye:",
    )
    msg.add_field(
        name="Faves per view :",
        value=f"{round(project_obj.favorites / project_obj.views, 2)} :star: / :eye:",
    )
    msg.add_field(
        name="Loves per view (%) :",
        value=f"{round((project_obj.loves / project_obj.views) * 100)} :heart: / 100 :eye:",
    )
    msg.add_field(
        name="Faves per view (%) :",
        value=f"{round((project_obj.favorites / project_obj.views) * 100)} :star: / 100 :eye:",
    )

    msg.color = scratch_orange
    desc = limiter(text=project_obj.instructions, limit=500)
    msg.description = (
        f"Made by {project_obj.author_name}, at {project_obj.share_date} "
        f"(Last modified at {project_obj.last_modified})\n"
        f"<:Turbowarp:1330552274774396979>Turbowarp link : https://turbowarp.org/{id}\n\n"
        f"**Description :**\n{desc}\n\n"
        f"**Notes and Credits :**\n{project_obj.notes}\n\n"
        "<:scratchstats:1330550531864662018> Statistics :\n"
    )
    msg.set_image(url=project_obj.thumbnail_url)

    await interact.response.send_message(embed=msg)


@bot.tree.command(
    name="trendscore",
    description="Gets a project's trending potential, represented as a score number.",
)
async def trendscore(interact: discord.Interaction, project: str):
    id = "".join(filter(str.isdigit, project))
    proj = scratch.get_project(id)
    diff = datetime.now() - datetime.strptime(proj.share_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    score = round(proj.views / (diff.days * 24 + diff.seconds / 3600), 3)

    await interact.response.send_message(
        embed=discord.Embed(
            title=f"<:popular:1330550904813916272>'{proj.title}' has a trending score of {score} !<:popular:1330550904813916272>",
            color=discord.Colour.gold(),
        )
    )


@bot.tree.command(
    name="ontrend",
    description="Checks if a project is on trending in a specific language.",
)
async def ontrend(
    interact: discord.Interaction, project: str, language: str, limit: int
):
    i = 0
    found = False
    id = "".join(filter(str.isdigit, project))

    for item in scratch.explore_projects(
        language=language, limit=limit, mode="trending"
    ):
        i += 1
        if item.id == int(id):
            found = True
            break

    if found:
        await interact.response.send_message(
            embed=discord.Embed(
                title="Project found !",
                description=f"This project is on trending, at the **{i}th** position !",
                colour=discord.Color.green(),
            )
        )
    else:
        await interact.response.send_message(
            embed=discord.Embed(
                title="Project not found !",
                description="This project is not on trending !",
                color=discord.Colour.red(),
            )
        )


@bot.tree.command(
    name="newestprojects", description="Get all the newest published projects."
)
async def newestprojects(interact: discord.Interaction):
    import pprint

    await interact.response.send_message(
        embed=discord.Embed(
            title="<:newscratcher:1330550984971259954>Newest scratch projects :",
            description=pprint.pformat(scratch.newest_projects()),
            color=scratch_orange,
        )
    )


@bot.tree.command(name="s_download", description="Downloads the specified project")
async def s_download(interact: discord.Interaction, project: str):
    id = "".join(filter(str.isdigit, project))
    await interact.response.defer()
    proj = scratch.get_project(id)
    proj.download(filename="project.sb3", dir="ScratchOn_private")

    await interact.followup.send(
        file=discord.File(
            fp="ScratchOn_private/project.sb3", filename=f"{proj.title}.sb3"
        )
    )

    os.remove(path="ScratchOn_private/project.sb3")
