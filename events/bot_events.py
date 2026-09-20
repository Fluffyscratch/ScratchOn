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

# ------------------------------------------------------------------ #
# Helper functions                                                        #
# ------------------------------------------------------------------ #
def classify(activity) -> str | None:
    """Map an activity to a stats key, or None if irrelevant."""
    T = interactions.ActivityType
    name = activity.name or ""
    playing = activity.type == T.PLAYING
    streaming = activity.type == T.STREAMING

    if name == "TurboWarp Desktop":
        return "turbowarp" if playing else "streaming_turbowarp" if streaming else None
    if match(r"Scratch 3\.\d+\.\d+", name):
        return "scratch3" if playing else "streaming_scratch3" if streaming else None
    if playing and name == "Scratch 2 Offline Editor":
        return "scratch2"
    if playing and match(r"Scratch 1\.4 of \d{2}-[A-Za-z]{3}-\d{2}", name):
        return "scratch1"
    return None

_user_states: dict[int, set[str]] = {}

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

    @interactions.listen(interactions.events.PresenceUpdate)
    async def on_member_update(self, event):
        """Handle member rich presence update events."""
        stats = config.activity_stats
        uid = int(event.user.id)

        new = {k for a in event.activities if (k := classify(a))}
        old = _user_states.get(uid, set())

        for key in old - new:
            stats[key] -= 1
        for key in new - old:
            stats[key] += 1

        _user_states[uid] = new

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
    async def on_command_error(self, event: CommandError):
        logging.exception(f"Error in command", exc_info=event.error)

        try:
            await event.ctx.send("❌ An internal error occurred.", ephemeral=True)
        except Exception:
            pass


def setup(bot: interactions.Client):
    BotEvents(bot)
