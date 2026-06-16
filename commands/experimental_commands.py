"""
Experimental slash commands (beta features).
"""

import interactions

import scratchattach as scratch
import requests

from config import scratch_orange, betaembed, button_states
from database import get_server_data
from utils import (
    dc2scratch,
    replace_last_screenshot,
    remove_line_by_index,
    update_pings,
)


class ExperimentalCommands(interactions.Extension):
    """Experimental / beta slash commands."""

    @interactions.slash_command(
        name="remixtree",
        description="BETA - Gets a project's remix tree.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def remixtree(self, ctx: interactions.SlashContext, project: str):
        if ctx.author.username == "fluffyscratch":
            id = "".join(filter(str.isdigit, project))
            # await directly — we're already inside an async function
            await replace_last_screenshot(f"scratch.mit.edu/projects/{id}/remixtree")
            await ctx.send(file=interactions.File(file="screenshot.png"))
        else:
            await ctx.send(embed=betaembed)

    @interactions.slash_command(
        name="toggle_ping",
        description="BETA - Enable or disable discord ping when receiving a new message. Requires binding.",
    )
    async def toggle_ping(self, ctx: interactions.SlashContext):
        if ctx.author.username == "fluffyscratch":
            target = str(ctx.author)
            found = False
            i = -1

            with open("private/dcusers.txt") as file:
                for item in file.readlines():
                    i += 1
                    if item.strip() == target:
                        found = True
                        break

            if found:
                with open("private/scusers.txt") as file:
                    s_user = file.readlines()[i]
                target = s_user
                found = False
                i = 0

                with open("private/users2ping.txt") as file:
                    for item in file.readlines():
                        i += 1
                        if item.strip() == target:
                            found = True
                            break

                if found:
                    remove_line_by_index("users2ping.txt", i - 1)
                    update_pings()
                    await ctx.send(
                        embed=interactions.Embed(
                            title="Success !",
                            description="Pinging when receiving a scratch message is now disabled for your account !",
                            color=0x57F287,
                        )
                    )
                else:
                    with open("private/users2ping.txt", "a+") as file:
                        file.write(f"{s_user}\n")
                    update_pings()
                    await ctx.send(
                        embed=interactions.Embed(
                            title="Success !",
                            description="Pinging when receiving a scratch message is now enabled for your account !",
                            color=0x57F287,
                        )
                    )
            else:
                await ctx.send(
                    embed=interactions.Embed(
                        title="Error :",
                        description="You need to bind your scratch account to use this command. To bind your scratch account, use /bind !",
                        color=0xFF0000,
                    )
                )
        else:
            await ctx.send(embed=betaembed)

    @interactions.slash_command(
        name="settings",
        description="BETA - Configure ScratchOn settings for this server",
    )
    async def settings(self, ctx: interactions.SlashContext):
        if ctx.author.username == "fluffyscratch":
            # Read current state from the database
            ai_state = (
                interactions.ButtonStyle.SUCCESS
                if get_server_data(ctx.guild_id, "ai")
                else interactions.ButtonStyle.DANGER
            )
            embed_state = (
                interactions.ButtonStyle.SUCCESS
                if get_server_data(ctx.guild_id, "embeds")
                else interactions.ButtonStyle.DANGER
            )

            embed = interactions.Embed(
                title="Settings",
                description="Please select your preferences.",
                color=0x3498DB,  # blue
            )

            # Buttons for toggling features
            ai_button = interactions.Button(
                label="AI",
                style=ai_state,
                custom_id="ai_button",
            )
            embeds_button = interactions.Button(
                label="Embeds",
                style=embed_state,
                custom_id="embeds_button",
            )

            # Language dropdown
            language_select = interactions.StringSelectMenu(
                interactions.StringSelectOption(label="English", value="en"),
                interactions.StringSelectOption(label="Français", value="fr"),
                placeholder="Select your language here",
                custom_id="language_select",
            )

            # Buttons go in one row; the select menu in its own row
            action_row = interactions.ActionRow(ai_button, embeds_button)
            select_row = interactions.ActionRow(language_select)

            # Persist current states so on_component in bot_events can read them
            button_states["ai_button"] = ai_state
            button_states["embeds_button"] = embed_state

            await ctx.send(embed=embed, components=[action_row, select_row])
        else:
            await ctx.send(embed=betaembed)

    @interactions.slash_command(
        name="scratchgpt",
        description="BETA - Chat with a powerful AI to get scratch related help !",
    )
    @interactions.slash_option(
        name="prompt",
        description="Your question or prompt",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def scratchgpt(self, ctx: interactions.SlashContext, prompt: str):
        await ctx.defer()

        if get_server_data(ctx.guild_id, "ai"):
            url = "https://api.penguinai.tech/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            data = {
                "model": "gpt-4-turbo",
                "messages": [
                    {
                        "role": "scratcher",
                        "content": (
                            "Answer this knowing you're a scratch assistant and number one scratch discord bot "
                            f"called ScratchOn and like scratching, coding and helping people : {prompt}"
                        ),
                    }
                ],
            }
            response = requests.post(url=url, headers=headers, json=data)

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                await ctx.send(
                    embed=interactions.Embed(description=content, color=scratch_orange)
                )
            else:
                await ctx.send(
                    embed=interactions.Embed(
                        color=0xFF0000,
                        title="Sorry, the API we use appears to be down :/",
                    )
                )
        else:
            if ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
                await ctx.send(
                    embed=interactions.Embed(
                        color=0xFF0000,
                        title=":x: Sorry, AI is not allowed on this server. Since you're a server admin, you can change this using /settings.",
                    )
                )
            else:
                await ctx.send(
                    embed=interactions.Embed(
                        color=0xFF0000,
                        title=":x: Sorry, AI is not allowed on this server.",
                    )
                )

    @interactions.slash_command(
        name="compare",
        description="BETA - Compares two Scratch users' stats.",
    )
    @interactions.slash_option(
        name="user1",
        description="First Scratch username",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="user2",
        description="Second Scratch username",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def compare(self, ctx: interactions.SlashContext, user1: str, user2: str):
        if ctx.author.username == "fluffyscratch":
            try:
                await ctx.defer()
                sc_user1 = scratch.get_user(user1)
                sc_user2 = scratch.get_user(user2)

                embed = interactions.Embed(
                    title=f"Comparing {user1} and {user2}", color=scratch_orange
                )
                embed.add_field(
                    name=user1,
                    value=(
                        f"Projects: {sc_user1.project_count()}\n"
                        f"Followers: {sc_user1.follower_count()}\n"
                        f"Following: {sc_user1.following_count()}\n"
                        f"Loves: {sc_user1.loves_count()}\n"
                        f"Favorites: {sc_user1.favorites_count()}"
                    ),
                    inline=True,
                )
                embed.add_field(name="\u200b", value="\u200b", inline=True)
                embed.add_field(
                    name=user2,
                    value=(
                        f"Projects: {sc_user2.project_count()}\n"
                        f"Followers: {sc_user2.follower_count()}\n"
                        f"Following: {sc_user2.following_count()}\n"
                        f"Loves: {sc_user2.loves_count()}\n"
                        f"Favorites: {sc_user2.favorites_count()}"
                    ),
                    inline=True,
                )

                await ctx.send(embed=embed)

            except scratch.utils.exceptions.UserNotFound:
                await ctx.send(
                    embed=interactions.Embed(
                        title="Error",
                        description="One or both of the specified users do not exist on Scratch.",
                        color=0xFF0000,
                    )
                )
        else:
            await ctx.send(embed=betaembed)


def setup(bot: interactions.Client):
    ExperimentalCommands(bot)
