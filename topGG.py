import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
import interactions
from dotenv import load_dotenv

# Module-level config (populated when attach_to_bot is called)
BOT_TOKEN = None
COMMANDS_TOKEN = None
APPLICATION_ID = None


# ---------------------------------------------------------------------------
# Decorator for excluding commands from Top.gg
# ---------------------------------------------------------------------------


def exclude_from_topgg(func):
    """
    Decorator to exclude a command from Top.gg posting.

    Usage::

        @slash_command(name="admin", description="Admin command")
        @exclude_from_topgg
        async def admin_command(ctx: SlashContext):
            await ctx.send("Admin only!")
    """
    func._exclude_from_topgg = True
    return func


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------


def setup_logging():
    """Configure file + stdout logging."""
    logging_path = Path("logs")
    logging_path.mkdir(exist_ok=True)

    log_file = logging_path / f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# ---------------------------------------------------------------------------
# Top.gg integration
# ---------------------------------------------------------------------------


class TopGGIntegration:
    """Handles Top.gg API integration for command posting."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot
        self.commands_token = COMMANDS_TOKEN

    async def post_commands_to_topgg(self) -> bool:
        """Post the bot's registered commands to Top.gg."""
        if not self.commands_token:
            logging.error("Commands token not found. Set Commands-TK in environment.")
            return False

        url = "https://top.gg/api/v1/projects/@me/commands"
        headers = {
            "Authorization": f"Bearer {self.commands_token}",
            "Content-Type": "application/json",
        }

        try:
            commands_data = await self._get_bot_commands_for_topgg()

            if not commands_data:
                logging.warning("⚠️ No commands found to post to Top.gg")
                return False

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=headers, json=commands_data
                ) as resp:
                    if resp.status in (200, 204):
                        logging.info(
                            f"✅ Successfully posted {len(commands_data)} commands to Top.gg"
                        )
                        return True
                    else:
                        text = await resp.text()
                        logging.error(
                            f"❌ Failed to post commands to Top.gg: {resp.status} - {text}"
                        )
                        return False

        except Exception as e:
            logging.error(f"❌ Error posting commands to Top.gg: {e}")
            return False

    async def _get_bot_commands_for_topgg(self) -> List[Dict]:
        """Convert the bot's application commands to Top.gg API format."""
        commands_list = []
        excluded_count = 0

        for command in self.bot.application_commands:
            try:
                if self._is_command_excluded(command):
                    logging.info(f"🚫 Skipping '{command.name}' (excluded from Top.gg)")
                    excluded_count += 1
                    continue

                command_data = await self._convert_command_to_topgg_format(command)
                if command_data:
                    commands_list.append(command_data)

            except Exception as e:
                name = getattr(command, "name", "unknown")
                logging.error(f"❌ Error converting command '{name}': {e}")

        total = len(list(self.bot.application_commands))
        logging.info(
            f"📊 Top.gg command summary: {len(commands_list)} posted, "
            f"{excluded_count} excluded, {total} total"
        )
        return commands_list

    def _is_command_excluded(self, command) -> bool:
        """Return True if this command carries the @exclude_from_topgg marker."""
        # Check the decorated callback function
        if hasattr(command, "callback") and hasattr(
            command.callback, "_exclude_from_topgg"
        ):
            return True
        # Some internals store it differently
        if hasattr(command, "_callback") and hasattr(
            command._callback, "_exclude_from_topgg"
        ):
            return True
        # Direct attribute (set manually)
        if hasattr(command, "_exclude_from_topgg"):
            return True
        return False

    async def _convert_command_to_topgg_format(self, command) -> Optional[Dict]:
        """Convert an interactions.py command object to the Top.gg API payload format."""
        try:
            # Resolve command ID (only available after syncing)
            cmd_id = "0"
            if hasattr(command, "cmd_id") and command.cmd_id:
                raw = command.cmd_id
                if isinstance(raw, dict):
                    # cmd_id is keyed by scope; take the first value
                    cmd_id = str(next(iter(raw.values()), "0"))
                else:
                    cmd_id = str(raw)

            command_data: Dict = {
                "id": cmd_id,
                "application_id": str(self.bot.app_id),
                "name": command.name,
                "version": "1",
            }

            # Context-menu commands (USER = 2, MESSAGE = 3)
            if isinstance(command, interactions.ContextMenuCommand):
                command_data.update(
                    {
                        "type": command.type.value,
                        "description": "",
                    }
                )

            else:
                # Slash command — may have subcommands (group-like)
                command_data.update(
                    {
                        "type": 1,  # CHAT_INPUT
                        "description": getattr(command, "description", "")
                        or "No description",
                    }
                )

                options = getattr(command, "options", None) or []

                if options:
                    converted_options = []
                    for opt in options:
                        opt_data = self._convert_option(opt)
                        if opt_data:
                            converted_options.append(opt_data)
                    if converted_options:
                        command_data["options"] = converted_options

            # Honour default_member_permissions if present
            if (
                hasattr(command, "default_member_permissions")
                and command.default_member_permissions
            ):
                command_data["default_member_permissions"] = str(
                    command.default_member_permissions.value
                    if hasattr(command.default_member_permissions, "value")
                    else command.default_member_permissions
                )

            return command_data

        except Exception as e:
            logging.error(f"❌ Error converting '{getattr(command, 'name', '?')}': {e}")
            return None

    def _convert_option(self, option) -> Optional[Dict]:
        """
        Convert a SlashCommandOption (interactions.py) to the Top.gg option dict.

        In interactions.py, option.type is already a Discord OptionType integer enum,
        so no Python-type mapping is needed.
        """
        try:
            opt_type = option.type
            type_value = opt_type.value if hasattr(opt_type, "value") else int(opt_type)

            option_data: Dict = {
                "name": option.name,
                "description": getattr(option, "description", "Parameter")
                or "Parameter",
                "required": getattr(option, "required", True),
                "type": type_value,
            }

            # Carry nested options (sub-command / sub-command-group)
            nested = getattr(option, "options", None)
            if nested:
                converted = [self._convert_option(o) for o in nested]
                option_data["options"] = [o for o in converted if o]

            # Carry choices
            choices = getattr(option, "choices", None)
            if choices:
                option_data["choices"] = [
                    {"name": c.name, "value": c.value} for c in choices
                ]

            return option_data

        except Exception as e:
            logging.error(
                f"❌ Error converting option '{getattr(option, 'name', '?')}': {e}"
            )
            return None

    async def start_periodic_updates(self):
        """Start the background task that re-posts commands every 24 hours."""
        asyncio.create_task(self._periodic_commands())

    async def _periodic_commands(self):
        while True:
            try:
                await self.post_commands_to_topgg()
                await asyncio.sleep(86_400)  # 24 hours
            except Exception as e:
                logging.error(f"❌ Error in periodic command update: {e}")
                await asyncio.sleep(3_600)  # retry after 1 hour


# ---------------------------------------------------------------------------
# Command syncer
# ---------------------------------------------------------------------------


class CommandSyncer:
    """Wraps interactions.py's command synchronisation."""

    def __init__(self, bot: interactions.Client):
        self.bot = bot

    async def sync_commands(self, guild_id: Optional[int] = None) -> int:
        """
        Sync slash commands with Discord.

        interactions.py syncs commands automatically on startup when
        ``sync_interactions=True`` (the default).  This method is provided
        for explicit / manual re-syncs.
        """
        try:
            await self.bot.synchronise_interactions()
            count = len(list(self.bot.application_commands))
            logging.info(f"✅ Synced {count} application commands")
            return count
        except Exception as e:
            logging.error(f"❌ Failed to sync commands: {e}")
            return 0


# ---------------------------------------------------------------------------
# attach_to_bot — public entry point
# ---------------------------------------------------------------------------


def attach_to_bot(bot: interactions.Client, env_path: str = "TopGG.env"):
    """Attach Top.gg integration to an existing ``interactions.Client`` instance.

    This will:

    * load environment variables from *env_path* (if present)
    * configure logging
    * register ``Ready``, ``GuildJoin``, and ``GuildLeft`` listeners directly
      on *bot* that sync commands and post to Top.gg after the bot is ready.

    Call this **before** ``bot.start(token)``.
    """

    load_dotenv(dotenv_path=env_path)
    global BOT_TOKEN, COMMANDS_TOKEN, APPLICATION_ID
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    COMMANDS_TOKEN = os.getenv("Commands-TK")
    APPLICATION_ID = os.getenv("APPLICATION_ID")

    setup_logging()

    topgg_integration = TopGGIntegration(bot)
    syncer = CommandSyncer(bot)

    # Attach helpers to the bot instance so they can be retrieved later
    setattr(bot, "_topgg_integration", topgg_integration)
    setattr(bot, "_topgg_syncer", syncer)

    # ------------------------------------------------------------------ #
    # Event listeners registered directly on the bot                      #
    # ------------------------------------------------------------------ #

    @bot.listen(interactions.events.Ready)
    async def _on_ready(event: interactions.events.Ready):
        logging.info(f"🚀 Bot logged in as {bot.user.username} (ID: {bot.user.id})")
        logging.info(f"📊 Connected to {len(bot.guilds)} guilds")

        try:
            await syncer.sync_commands()
        except Exception as e:
            logging.error(f"❌ Command sync failed: {e}")

        try:
            await topgg_integration.start_periodic_updates()
            logging.info("✅ Top.gg integration started")
        except Exception as e:
            logging.error(f"❌ Top.gg integration failed: {e}")

        try:
            await topgg_integration.post_commands_to_topgg()
            logging.info("✅ Initial Top.gg commands posted")
        except Exception as e:
            logging.error(f"❌ Failed to post initial Top.gg commands: {e}")

    @bot.listen(interactions.events.GuildJoin)
    async def _on_guild_join(event: interactions.events.GuildJoin):
        logging.info(f"📈 Joined guild: {event.guild.name} (ID: {event.guild.id})")

    @bot.listen(interactions.events.GuildLeft)
    async def _on_guild_remove(event: interactions.events.GuildLeft):
        name = event.guild.name if event.guild else "Unknown"
        gid = event.guild.id if event.guild else "?"
        logging.info(f"📉 Left guild: {name} (ID: {gid})")

    return topgg_integration


# ---------------------------------------------------------------------------
# Helper for ad-hoc posting
# ---------------------------------------------------------------------------


async def post_commands_now(bot: interactions.Client) -> bool:
    """Post commands immediately using the bot's attached integration (if any)."""
    topgg: Optional[TopGGIntegration] = getattr(bot, "_topgg_integration", None)
    if topgg is None:
        topgg = TopGGIntegration(bot)
    return await topgg.post_commands_to_topgg()
