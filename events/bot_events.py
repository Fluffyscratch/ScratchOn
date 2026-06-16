"""
Discord bot events.
"""

import logging

import interactions
from interactions.api.events import CommandError

from config import bot_statuses, button_states
from database import add_server

logger = logging.getLogger(__name__)


class BotEvents(interactions.Extension):
    """Core bot lifecycle events and error handling."""

    # ------------------------------------------------------------------ #
    # Status cycling                                                       #
    # ------------------------------------------------------------------ #

    @interactions.Task.create(interactions.IntervalTrigger(seconds=10))
    async def status_task(self):
        """Cycle through bot statuses every 10 seconds."""
        await self.bot.change_presence(
            activity=interactions.Activity(
                name=next(bot_statuses),
                type=interactions.ActivityType.GAME,
            )
        )

    # ------------------------------------------------------------------ #
    # Lifecycle listeners                                                  #
    # ------------------------------------------------------------------ #

    @interactions.listen(interactions.events.Ready)
    async def on_ready(self, event: interactions.events.Ready) -> None:
        logger.info("ScratchOn is ready!")
        self.status_task.start()

    @interactions.listen(interactions.events.GuildJoin)
    async def on_guild_join(self, event: interactions.events.GuildJoin) -> None:
        """Register a newly joined server in the database."""
        add_server(event.guild.id)

    # ------------------------------------------------------------------ #
    # Component interaction handler (settings buttons)                     #
    # ------------------------------------------------------------------ #

    @interactions.listen(interactions.events.Component)
    async def on_component(self, event: interactions.events.Component) -> None:
        """Toggle button states for the ``/settings`` UI."""
        ctx = event.ctx
        button_id = ctx.custom_id

        if button_id not in ("ai_button", "embeds_button"):
            return

        current = button_states.get(button_id, interactions.ButtonStyle.DANGER)
        new_style = (
            interactions.ButtonStyle.SUCCESS
            if current == interactions.ButtonStyle.DANGER
            else interactions.ButtonStyle.DANGER
        )
        button_states[button_id] = new_style

        # Rebuild components with updated styles
        ai_button = interactions.Button(
            label="AI",
            style=button_states.get("ai_button", interactions.ButtonStyle.DANGER),
            custom_id="ai_button",
        )
        embeds_button = interactions.Button(
            label="Embeds",
            style=button_states.get("embeds_button", interactions.ButtonStyle.DANGER),
            custom_id="embeds_button",
        )
        language_select = interactions.StringSelectMenu(
            interactions.StringSelectOption(label="English", value="en"),
            interactions.StringSelectOption(label="Français", value="fr"),
            placeholder="Select your language here",
            custom_id="language_select",
        )

        action_row = interactions.ActionRow(ai_button, embeds_button)
        select_row = interactions.ActionRow(language_select)

        await ctx.edit_origin(components=[action_row, select_row])

        color_name = "green" if new_style == interactions.ButtonStyle.SUCCESS else "red"
        await ctx.send(
            f"The **{button_id}** color changed to **{color_name}**!", ephemeral=True
        )

    # ------------------------------------------------------------------ #
    # Error handler                                                        #
    # ------------------------------------------------------------------ #

    @interactions.listen()
    async def on_command_error(event: CommandError) -> None:
        logger.exception(
            "Error in command %s", event.ctx.command.name, exc_info=event.error
        )
        try:
            await event.ctx.send("An internal error occurred.", ephemeral=True)
        except Exception:
            pass


def setup(bot: interactions.Client) -> None:
    BotEvents(bot)
