"""
Discord bot events.
"""
import discord
from discord.ext import tasks
from discord.ui import Button, Select, View

from config import bot, bot_statuses, button_states
from database import add_server


@tasks.loop(seconds=10)
async def status():
    """Cycles through bot statuses."""
    await bot.change_presence(activity=discord.Game(next(bot_statuses)))


def setup_events():
    """Sets up all bot events."""

    @bot.event
    async def on_ready():
        print("ScratchOn is ready !")
        status.start()
        try:
            synced_commands = await bot.tree.sync()
            print(f"Synced {len(synced_commands)} commands.")
        except Exception:
            print("Nah, I don't want to sync my commands today.")

    @bot.event
    async def on_guild_join(guild):
        """When joining a server, add a settings line corresponding to them."""
        add_server(guild.id)

    @bot.event
    async def on_interaction(interaction: discord.Interaction):
        """Button interaction handlers for settings."""
        if interaction.type == discord.InteractionType.component:
            button_id = interaction.data['custom_id']

            # Make sure the button_id exists in button_states
            if button_id not in button_states:
                button_states[button_id] = discord.ButtonStyle.red

            current_style = button_states[button_id]

            # Toggle the button's color (green <-> red)
            new_style = (
                discord.ButtonStyle.green 
                if current_style == discord.ButtonStyle.red 
                else discord.ButtonStyle.red
            )

            # Update the state in button_states
            button_states[button_id] = new_style

            # Rebuild the view with the updated buttons
            ai_button = Button(
                label="AI",
                style=button_states.get("ai_button", discord.ButtonStyle.red),
                custom_id="ai_button"
            )
            embeds_button = Button(
                label="Embeds",
                style=button_states.get("embeds_button", discord.ButtonStyle.red),
                custom_id="embeds_button"
            )
            language_select = Select(
                placeholder="Select your language here",
                options=[
                    discord.SelectOption(label="English", value="en"),
                    discord.SelectOption(label="Français", value="fr"),
                ]
            )

            view = View()
            view.add_item(ai_button)
            view.add_item(embeds_button)
            view.add_item(language_select)

            # Edit the original message to reflect the updated button colors
            await interaction.response.edit_message(view=view)

            # Acknowledge the button press
            color_name = 'green' if new_style == discord.ButtonStyle.green else 'red'
            await interaction.followup.send(
                f"The {button_id} color changed to {color_name}!",
                ephemeral=True
            )
