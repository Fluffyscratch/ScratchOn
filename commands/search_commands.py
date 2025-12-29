"""
Search and discovery slash commands (ESDB-powered and others).
"""

import random

import discord
from discord import app_commands
import requests

import scratchattach as scratch

from config import bot, scratch_orange


@bot.tree.command(
    name="randomprojects",
    description="Shows a number of random scratch projects.",
)
async def randomprojects(interact: discord.Interaction, number: int):
    await interact.response.defer()

    message = ""
    max_project_id = scratch.total_site_stats().get("PROJECT_COUNT")
    for i in range(number):
        while True:
            try:
                project = scratch.get_project(random.randint(1, max_project_id))
            except scratch.utils.exceptions.ProjectNotFound:
                continue
            break
        message = f"{message} [**{project.title}**](https://scratch.mit.edu/projects/{project.id})\n\n"

    msg = discord.Embed()
    if number == 1:
        msg.title = "Here is 1 random project !"
    else:
        msg.title = f"Here are {number} random projects !"
    msg.description = message
    msg.color = scratch_orange
    await interact.followup.send(embed=msg)


@bot.tree.command(
    name="christmas", description="Take a look at the best christmas projects easily !"
)
async def christmas(interact: discord.Interaction):
    await interact.response.defer()

    message = ""
    projects = scratch.search_projects(
        query="christmas", mode="popular", language="en", limit=10, offset=0
    )
    for item in projects:
        message = (
            f"{message}\n\n **[{item.title}](<https://scratch.mit.edu/projects/{item.id}>)**\n"
            f"-# by [{item.author().username}](https://scratch.mit.edu/users/{item.author().username})"
        )
    await interact.followup.send(
        embed=discord.Embed(
            title="<:SantaCat:1444277069826494557>Top 10 popular christmas projects<:SantaCat:1444277069826494557> :",
            description=message,
            color=scratch_orange,
        )
    )
