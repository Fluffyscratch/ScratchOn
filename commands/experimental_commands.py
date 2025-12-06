"""
Experimental slash commands (beta features).
"""

import asyncio
import discord
from discord import app_commands
from discord.ui import Button, Select, View

import scratchattach as scratch
import requests

from config import bot, scratch_orange, betaembed, button_states
from database import get_server_data
from utils import (
    dc2scratch,
    replace_last_screenshot,
    remove_line_by_index,
    update_pings,
)


@bot.tree.command(name="remixtree", description="BETA - Gets a project's remix tree.")
async def remixtree(interact: discord.Interaction, project: str):
    if interact.user.name == "fluffyscratch":
        id = "".join(filter(str.isdigit, project))
        asyncio.get_event_loop().run_until_complete(
            replace_last_screenshot(f"scratch.mit.edu/projects/{id}/remixtree")
        )
        await interact.response.send_message(file=discord.File("screenshot.png"))
    else:
        await interact.response.send_message(embed=betaembed)


@bot.tree.command(
    name="toggle_ping",
    description="BETA - Enable or disable discord ping when recieving a new message. Requires binding.",
)
async def toggle_ping(interact: discord.Interaction):
    if interact.user.name == "fluffyscratch":
        target = str(interact.user)
        found = False
        i = -1

        with open("ScratchOn_private/dcusers.txt") as file:
            for item in file.readlines():
                i += 1
                if item.strip() == target:
                    found = True
                    break

        print(i)

        if found:
            with open("ScratchOn_private/scusers.txt") as file:
                s_user = file.readlines()[i]
            print(s_user)
            target = s_user
            found = False
            i = 0

            with open("ScratchOn_private/users2ping.txt") as file:
                for item in file.readlines():
                    i += 1
                    if item.strip() == target:
                        found = True
                        break

            if found:
                remove_line_by_index("users2ping.txt", i - 1)
                update_pings()
                await interact.response.send_message(
                    embed=discord.Embed(
                        title="Success !",
                        description="Pinging when recieving a scratch message is now disabled for your account !",
                        color=discord.Color.green(),
                    )
                )
            else:
                with open("ScratchOn_private/users2ping.txt", "a+") as file:
                    file.write(f"{s_user}\n")
                    update_pings()
                    await interact.response.send_message(
                        embed=discord.Embed(
                            title="Success !",
                            description="Pinging when recieving a scratch message is now enabled for your account !",
                            color=discord.Color.green(),
                        )
                    )
        else:
            await interact.response.send_message(
                embed=discord.Embed(
                    title="Error :",
                    description="You need to bind your scratch account to use this command. To bind your scratch account, use /bind !",
                    color=discord.Color.red(),
                )
            )
    else:
        await interact.response.send_message(embed=betaembed)


@bot.tree.command(
    name="settings", description="BETA - Configure ScratchOn settings for this server"
)
async def settings(interaction: discord.Interaction):
    if interaction.user.name == "fluffyscratch":
        # Button current color state
        ai_state = (
            discord.ButtonStyle.green
            if get_server_data(interaction.guild_id, "ai")
            else discord.ButtonStyle.red
        )
        embed_state = (
            discord.ButtonStyle.green
            if get_server_data(interaction.guild_id, "embeds")
            else discord.ButtonStyle.red
        )

        # Create the embed
        embed = discord.Embed(
            title="Settings",
            description="Please select your preferences.",
            color=discord.Color.blue(),
        )

        # Create the buttons with initial states
        ai_button = Button(label="AI", style=ai_state, custom_id="ai_button")
        embeds_button = Button(
            label="Embeds", style=embed_state, custom_id="embeds_button"
        )

        # Define the dropdown (Select menu)
        language_select = Select(
            placeholder="Select your language here",
            options=[
                discord.SelectOption(label="English", value="en"),
                discord.SelectOption(label="Français", value="fr"),
            ],
        )

        # Define the view
        view = View()
        view.add_item(ai_button)
        view.add_item(embeds_button)
        view.add_item(language_select)

        # Save initial button states to the global dictionary
        button_states["ai_button"] = ai_state
        button_states["embeds_button"] = embed_state

        # Send the embed with the UI elements
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=betaembed)


@bot.tree.command(
    name="recommend",
    description="BETA - Gives you recommended scratchers, projects or studios customised for you.",
)
@app_commands.choices(
    type=[
        app_commands.Choice(name="User", value="user"),
        app_commands.Choice(name="Project", value="project"),
        app_commands.Choice(name="Studio", value="studio"),
    ]
)
async def recommend(interact: discord.Interaction, type: str):
    if interact.user.name == "fluffyscratch":
        scratch_username = await dc2scratch(interact.user.name)
        if scratch_username is not None:
            scratch.get_user(scratch_username)
        else:
            await interact.response.send_message(
                embed=discord.Embed(
                    title="Sorry, you need to /bind your account so we can recommend you things !",
                    color=discord.Color.red(),
                )
            )
    else:
        await interact.response.send_message(embed=betaembed)


@bot.tree.command(
    name="scratchgpt",
    description="BETA - Chat with a powerful AI to get scratch related help !",
)
async def scratchgpt(interact: discord.Interaction, prompt: str):
    await interact.response.defer()

    if get_server_data(interact.guild_id, "ai"):
        url = "https://api.penguinai.tech/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "gpt-4-turbo",
            "messages": [
                {
                    "role": "scratcher",
                    "content": f"Answer this knowing you're a scratch assistant and number one scratch discord bot called ScratchOn and like scratching, coding and helping people : {prompt}",
                }
            ],
        }
        response = requests.post(url=url, headers=headers, json=data)

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            await interact.followup.send(
                embed=discord.Embed(description=content, color=scratch_orange)
            )
        else:
            await interact.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title="Sorry, the API we use appears to be down :/",
                )
            )
    else:
        if interact.user.guild_permissions.administrator:
            await interact.followup.send(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title=":x: Sorry, AI is not allowed on this server. Since you're a server admin, you can change this using /settings.",
                )
            )
        else:
            await interact.followup.send(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title=":x: Sorry, AI is not allowed on this server.",
                )
            )


@bot.tree.command(
    name="compare",
    description="BETA - Compares two Scratch users' stats.",
)
async def compare(interact: discord.Interaction, user1: str, user2: str):
    if interact.user.name == "fluffyscratch":
        try:
            await interact.response.defer()
            sc_user1 = scratch.get_user(user1)
            sc_user2 = scratch.get_user(user2)

            embed = discord.Embed(
                title=f"Comparing {user1} and {user2}", color=scratch_orange
            )
            embed.add_field(
                name=user1,
                value=f"Projects: {sc_user1.project_count()}\nFollowers: {sc_user1.follower_count()}\nFollowing: {sc_user1.following_count()}\nLoves: {sc_user1.loves_count()}\nFavorites: {sc_user1.favorites_count()}",
                inline=True,
            )
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(
                name=user2,
                value=f"Projects: {sc_user2.project_count()}\nFollowers: {sc_user2.follower_count()}\nFollowing: {sc_user2.following_count()}\nLoves: {sc_user2.loves_count()}\nFavorites: {sc_user2.favorites_count()}",
                inline=True,
            )

            await interact.followup.send(embed=embed)
        except scratch.utils.exceptions.UserNotFound:
            await interact.followup.send(
                embed=discord.Embed(
                    title="Error",
                    description="One or both of the specified users do not exist on Scratch.",
                    color=discord.Color.red(),
                )
            )
    else:
        await interact.response.send_message(embed=betaembed)
