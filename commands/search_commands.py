"""
Search and discovery slash commands (ESDB-powered and others).
"""
import discord
from discord import app_commands
import requests

import scratchattach as scratch

from config import bot, scratch_orange


@bot.tree.command(name="randomprojects", description="Shows a number of random scratch projects, powered by ESDB.")
async def randomprojects(interact: discord.Interaction, number: int):
    response = requests.get(f"https://explore.eletrix.fr/api/projects/random?limit={number}")
    
    if response.status_code == 200:
        message = ""
        for item in response.json():
            message = f"{message} [**{item['title']}**](https://scratch.mit.edu/projects/{item['id']}) :\n\n"
        
        msg = discord.Embed()
        if number == 1:
            msg.title = "Here is 1 random project !"
        else:
            msg.title = f"Here are {number} random projects !"
        msg.description = message
        msg.color = scratch_orange
        await interact.response.send_message(embed=msg)
    else:
        await interact.response.send_message(embed=discord.Embed(
            title=f"Whoops, looks like we've got an error {response.status_code} !<:giga404:1330551323610976339>",
            color=discord.Color.red()
        ))


@bot.tree.command(name="bettersearch", description="Allows you to search projects without bugs such as <900 million ids. Powered by ESDB.")
async def bettersearch(interact: discord.Interaction, query: str):
    response = requests.get(f"https://explore.eletrix.fr/api/projects/search?search={query}")
    
    if response.status_code == 200:
        message = ""
        for item in response.json():
            message = f"{message} [**{item['title']}**](https://scratch.mit.edu/projects/{item['id']}) :\n\n"
        
        msg = discord.Embed()
        msg.title = f"<:search:1333037655902130247>Results for '{query}' :"
        msg.description = message
        msg.color = scratch_orange
        await interact.response.send_message(embed=msg)
    else:
        await interact.response.send_message(embed=discord.Embed(
            title=f"Whoops, looks like we've got an error {response.status_code} !<:giga404:1330551323610976339>",
            color=discord.Color.red()
        ))


@bot.tree.command(name="christmas", description="Take a look at the best christmas projects easily !")
async def christmas(interact: discord.Interaction):
    message = ""
    projects = scratch.search_projects(
        query="christmas",
        mode="trending",
        language="en",
        limit=10,
        offset=0
    )
    for item in projects:
        message = (
            f"{message}\n\n **[{item.title}](<https://scratch.mit.edu/projects/{item.id}>)** "
            f"by [{item.author().username}](scratch.mit.edu/users/{item.author().username})"
        )
    await interact.response.send_message(embed=discord.Embed(
        title="<:SantaCat:1444277069826494557>Top 10 trending christmas projects<:SantaCat:1444277069826494557> :",
        description=message,
        color=scratch_orange
    ))
