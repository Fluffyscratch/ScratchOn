"""
Discord bot events.
"""

import interactions

from config import bot, bot_statuses, button_states
from database import add_server


class BotEvents(interactions.Extension):
    """Extension for core bot lifecycle events."""

    # ------------------------------------------------------------------ #
    # Status cycling task                                                  #
    # ------------------------------------------------------------------ #

    @interactions.Task.create(interactions.IntervalTrigger(seconds=10))
    async def status_task(self):
        """Cycles through bot statuses every 10 seconds."""
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
    async def on_ready(self, event: interactions.events.Ready):
        print("ScratchOn is ready !")
        self.status_task.start()

    @interactions.listen(interactions.events.GuildJoin)
    async def on_guild_join(self, event: interactions.events.GuildJoin):
        """When joining a server, register it in the database."""
        add_server(event.guild.id)

    # ------------------------------------------------------------------ #
    # Component interaction handler (settings buttons)                    #
    # ------------------------------------------------------------------ #

    @interactions.listen(interactions.events.Component)
    async def on_component(self, event: interactions.events.Component):
        """Toggle button states for the /settings UI."""
        ctx = event.ctx
        button_id = ctx.custom_id

        # Only handle the two known settings toggles
        if button_id not in ("ai_button", "embeds_button"):
            return

        # Default to DANGER (red = disabled) when first seen
        if button_id not in button_states:
            button_states[button_id] = interactions.ButtonStyle.DANGER

        current_style = button_states[button_id]

        # Toggle: SUCCESS (green) ↔ DANGER (red)
        new_style = (
            interactions.ButtonStyle.SUCCESS
            if current_style == interactions.ButtonStyle.DANGER
            else interactions.ButtonStyle.DANGER
        )
        button_states[button_id] = new_style

        # Rebuild the full component layout with updated styles
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

        # Edit the original message in-place
        await ctx.edit_origin(components=[action_row, select_row])

        # Acknowledge the toggle with an ephemeral followup
        color_name = "green" if new_style == interactions.ButtonStyle.SUCCESS else "red"
        await ctx.send(
            f"The **{button_id}** color changed to **{color_name}**!",
            ephemeral=True,
        )


def setup(bot: interactions.Client):
    BotEvents(bot)
