"""
Discord bot events.
"""

from re import match
import interactions
import logging
from interactions.api.events import CommandError

import config
from config import bot, bot_statuses, button_states, bot_ready
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
        global bot_ready
        bot_ready = True
        self.status_task.start()

    @interactions.listen(interactions.events.GuildJoin)
    async def on_guild_join(self, event: interactions.events.GuildJoin):
        """When joining a server, register it in the database."""
        global bot_ready
        if bot_ready:
            add_server(event.guild.id)

    @interactions.listen(interactions.events.MemberUpdate)
    async def on_member_update(self, before, after):
        """Handle member rich presence update events."""
        if before.activities != after.activities:
            # Handle activity changes to update stats
            stats = config.activity_stats
            for newactivity, oldactivity in zip(after.activities, before.activities):
                # Handle new activities
                if newactivity.name == "TurboWarp Desktop":
                    if newactivity.type == interactions.ActivityType.PLAYING:
                        stats["turbowarp"] += 1
                    elif newactivity.type == interactions.ActivityType.STREAMING:
                        stats["streaming_turbowarp"] += 1
                elif match(r"Scratch 3\.\d+\.\d+", newactivity.name):
                    if newactivity.type == interactions.ActivityType.PLAYING:
                        stats["scratch3"] += 1
                    elif newactivity.type == interactions.ActivityType.STREAMING:
                        stats["streaming_scratch3"] += 1
                elif (
                    newactivity.name == "Scratch 2 Offline Editor"
                    and newactivity.type == interactions.ActivityType.PLAYING
                ):
                    stats["scratch2"] += 1
                elif (
                    match(r"Scratch 1\.4 of \d{2}-[A-Za-z]{3}-\d{2}", newactivity.name)
                    and newactivity.type == interactions.ActivityType.PLAYING
                ):
                    stats["scratch1"] += 1

                # Handle removed activities
                if oldactivity.name == "TurboWarp Desktop":
                    if oldactivity.type == interactions.ActivityType.PLAYING:
                        stats["turbowarp"] -= 1
                    elif oldactivity.type == interactions.ActivityType.STREAMING:
                        stats["streaming_turbowarp"] -= 1
                elif match(r"Scratch 3\.\d+\.\d+", oldactivity.name):
                    if oldactivity.type == interactions.ActivityType.PLAYING:
                        stats["scratch3"] -= 1
                    elif oldactivity.type == interactions.ActivityType.STREAMING:
                        stats["streaming_scratch3"] -= 1
                elif (
                    oldactivity.name == "Scratch 2 Offline Editor"
                    and oldactivity.type == interactions.ActivityType.PLAYING
                ):
                    stats["scratch2"] -= 1
                elif (
                    match(r"Scratch 1\.4 of \d{2}-[A-Za-z]{3}-\d{2}", oldactivity.name)
                    and oldactivity.type == interactions.ActivityType.PLAYING
                ):
                    stats["scratch1"] -= 1

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

    # ------------------------------------------------------------------ #
    # Error handler                                                       #
    # ------------------------------------------------------------------ #

    @interactions.listen()
    async def on_command_error(event: CommandError):
        logging.exception(f"Error in command", exc_info=event.error)

        try:
            await event.ctx.send("❌ An internal error occurred.", ephemeral=True)
        except Exception:
            pass


def setup(bot: interactions.Client):
    BotEvents(bot)
