import asyncio
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Module-level config (will be populated when attached to a bot)
BOT_TOKEN = None
COMMANDS_TOKEN = None
APPLICATION_ID = None


# Decorator for excluding commands from Top.gg
def exclude_from_topgg(func):
    """
    Decorator to exclude commands from Top.gg posting

    Usage:
    @bot.tree.command(name="admin", description="Admin command")
    @exclude_from_topgg
    async def admin_command(interaction: discord.Interaction):
        await interaction.response.send_message("Admin only!")
    """
    func._exclude_from_topgg = True
    return func


# Setup logging
def setup_logging():
    """Setup logging configuration"""
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


# Initialize bot with proper intents
# Note: this module no longer creates its own Bot instance. Use `attach_to_bot(bot)`
# to integrate Top.gg functionality into an existing bot.


class TopGGIntegration:
    """Handles Top.gg API integration for command posting"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.commands_token = COMMANDS_TOKEN

    async def post_commands_to_topgg(self) -> bool:
        """Post bot commands to Top.gg"""
        if not self.commands_token:
            logging.error("Commands token not found. Set Commands-TK in environment.")
            return False

        url = f"https://top.gg/api/v1/projects/@me/commands"
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
                ) as response:
                    if response.status in [200, 204]:
                        logging.info(
                            f"✅ Successfully posted {len(commands_data)} commands to Top.gg"
                        )
                        return True
                    else:
                        text = await response.text()
                        logging.error(
                            f"❌ Failed to post commands to Top.gg: {response.status} - {text}"
                        )
                        return False
        except Exception as e:
            logging.error(f"❌ Error posting commands to Top.gg: {e}")
            return False

    async def _get_bot_commands_for_topgg(self) -> List[Dict]:
        """Convert bot's commands to Top.gg API format with decorator exclusions"""
        commands_list = []
        excluded_count = 0

        # Get all slash commands and context menus
        for command in self.bot.tree.get_commands():
            try:
                # Check if command is excluded via decorator
                if self._is_command_excluded(command):
                    logging.info(
                        f"🚫 Skipping command '{command.name}' (excluded from Top.gg)"
                    )
                    excluded_count += 1
                    continue

                command_data = await self._convert_command_to_topgg_format(command)
                if command_data:
                    commands_list.append(command_data)
            except Exception as e:
                logging.error(
                    f"❌ Error converting command {getattr(command, 'name', 'unknown')}: {e}"
                )

        # Log summary
        total_commands = len(self.bot.tree.get_commands())
        logging.info(
            f"📊 Top.gg command summary: {len(commands_list)} posted, {excluded_count} excluded, {total_commands} total"
        )

        return commands_list

    def _is_command_excluded(self, command) -> bool:
        """Check if a command should be excluded from Top.gg"""
        # Check for decorator exclusion on callback
        if hasattr(command, "callback") and hasattr(
            command.callback, "_exclude_from_topgg"
        ):
            return True

        # For command groups, check the group itself
        if hasattr(command, "_callback") and hasattr(
            command._callback, "_exclude_from_topgg"
        ):
            return True

        # Check if the command object itself has the exclusion flag
        if hasattr(command, "_exclude_from_topgg"):
            return True

        return False

    async def _convert_command_to_topgg_format(self, command) -> Optional[Dict]:
        """Convert a Discord command to Top.gg API format"""
        try:
            # Base command structure
            command_data = {
                "id": str(command.id) if hasattr(command, "id") and command.id else "0",
                "application_id": str(self.bot.application_id),
                "name": command.name,
                "version": "1",
            }

            # Handle different command types
            if isinstance(command, discord.app_commands.ContextMenu):
                # Context menu commands
                command_data.update(
                    {
                        "type": 2 if command.type == discord.AppCommandType.user else 3,
                        "description": "",
                    }
                )
            elif isinstance(command, discord.app_commands.Group):
                # Command groups
                command_data.update(
                    {
                        "type": 1,  # CHAT_INPUT
                        "description": command.description or "Command group",
                        "options": [],
                    }
                )

                # Add subcommands
                for subcommand in command.commands:
                    option_data = {
                        "type": 1,  # SUB_COMMAND
                        "name": subcommand.name,
                        "description": subcommand.description or "Subcommand",
                    }

                    # Add parameters if any
                    if hasattr(subcommand, "parameters") and subcommand.parameters:
                        option_data["options"] = []
                        for param in subcommand.parameters:
                            param_data = self._convert_parameter_to_option(param)
                            if param_data:
                                option_data["options"].append(param_data)

                    command_data["options"].append(option_data)
            else:
                # Regular slash commands
                command_data.update(
                    {
                        "type": 1,  # CHAT_INPUT
                        "description": command.description or "No description",
                    }
                )

                # Add parameters/options
                if hasattr(command, "parameters") and command.parameters:
                    command_data["options"] = []
                    for param in command.parameters:
                        param_data = self._convert_parameter_to_option(param)
                        if param_data:
                            command_data["options"].append(param_data)

            # Add permissions if specified
            if hasattr(command, "default_permissions") and command.default_permissions:
                command_data["default_member_permissions"] = str(
                    command.default_permissions.value
                )

            return command_data

        except Exception as e:
            logging.error(
                f"❌ Error converting command {command.name} to Top.gg format: {e}"
            )
            return None

    def _convert_parameter_to_option(self, param) -> Optional[Dict]:
        """Convert a command parameter to Discord option format"""
        try:
            option_data = {
                "name": param.name,
                "description": getattr(param, "description", "Parameter"),
                "required": param.required
                if hasattr(param, "required")
                else param.default == param.empty,
            }

            # Get the actual type, handling Union types and Optional
            param_type = param.type
            if hasattr(param_type, "__origin__") and param_type.__origin__ is Union:
                param_type = next(
                    (arg for arg in param_type.__args__ if arg != type(None)), str
                )

            # Map Python types to Discord option types
            if param_type == str or param_type is str:
                option_data["type"] = 3  # STRING
            elif param_type == int or param_type is int:
                option_data["type"] = 4  # INTEGER
            elif param_type == bool or param_type is bool:
                option_data["type"] = 5  # BOOLEAN
            elif param_type == float or param_type is float:
                option_data["type"] = 10  # NUMBER
            elif hasattr(param_type, "__name__"):
                type_name = param_type.__name__.lower()
                if "user" in type_name or "member" in type_name:
                    option_data["type"] = 6  # USER
                elif "channel" in type_name:
                    option_data["type"] = 7  # CHANNEL
                elif "role" in type_name:
                    option_data["type"] = 8  # ROLE
                elif "attachment" in type_name:
                    option_data["type"] = 11  # ATTACHMENT
                else:
                    option_data["type"] = 3  # Default to STRING
            else:
                option_data["type"] = 3  # Default to STRING

            return option_data

        except Exception as e:
            logging.error(
                f"❌ Error converting parameter {getattr(param, 'name', 'unknown')}: {e}"
            )
            return None

    async def start_periodic_updates(self):
        """Start periodic updates for commands"""
        # Start command updates (every 24 hours)
        asyncio.create_task(self._periodic_commands())

    async def _periodic_commands(self):
        """Periodically update commands"""
        while True:
            try:
                await self.post_commands_to_topgg()
                await asyncio.sleep(86400)  # 24 hours
            except Exception as e:
                logging.error(f"❌ Error in periodic command update: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying


class CommandSyncer:
    """Handles command synchronization with Discord"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def sync_commands(self, guild_id: Optional[int] = None) -> int:
        """Sync commands to Discord"""
        try:
            if guild_id:
                # Sync to specific guild (faster for testing)
                guild = discord.Object(id=guild_id)
                synced = await self.bot.tree.sync(guild=guild)
                logging.info(f"✅ Synced {len(synced)} commands to guild {guild_id}")
            else:
                # Sync globally (takes up to 1 hour to propagate)
                synced = await self.bot.tree.sync()
                logging.info(f"✅ Synced {len(synced)} commands globally")

            return len(synced)

        except Exception as e:
            logging.error(f"❌ Failed to sync commands: {e}")
            return 0


def attach_to_bot(bot: commands.Bot, env_path: str = "ScratchOn/TopGG.env"):
    """Attach Top.gg integration to an existing `commands.Bot` instance.

    This will:
    - load environment variables from `env_path` (optional)
    - configure logging
    - register an `on_ready` listener that syncs commands, starts periodic updates
      and posts initial commands to Top.gg.

    Call this before `bot.run(token)`.
    """

    # Load env and configure module-level tokens
    load_dotenv(dotenv_path=env_path)
    global BOT_TOKEN, COMMANDS_TOKEN, APPLICATION_ID
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    COMMANDS_TOKEN = os.getenv("Commands-TK")
    APPLICATION_ID = os.getenv("APPLICATION_ID")

    # Ensure logging configured
    setup_logging()

    topgg_integration = TopGGIntegration(bot)
    syncer = CommandSyncer(bot)

    async def _on_ready():
        logging.info(f"🚀 Bot logged in as {bot.user} (ID: {bot.user.id})")
        logging.info(f"📊 Connected to {len(bot.guilds)} guilds")

        # attach to bot for later manual use
        setattr(bot, "_topgg_integration", topgg_integration)
        setattr(bot, "_topgg_syncer", syncer)

        # Sync commands
        try:
            synced_count = await syncer.sync_commands()
            logging.info(f"✅ Command sync completed: {synced_count} commands")
        except Exception as e:
            logging.error(f"❌ Command sync failed: {e}")

        # Start Top.gg periodic updates
        try:
            await topgg_integration.start_periodic_updates()
            logging.info("✅ Top.gg integration started")
        except Exception as e:
            logging.error(f"❌ Top.gg integration failed: {e}")

        # Post initial commands
        try:
            await topgg_integration.post_commands_to_topgg()
            logging.info("✅ Initial Top.gg commands posted")
        except Exception as e:
            logging.error(f"❌ Failed to post initial Top.gg commands: {e}")

    # Register listeners
    bot.add_listener(_on_ready, "on_ready")

    # Optional lightweight guild join/remove logging
    async def _on_guild_join(guild):
        logging.info(f"📈 Joined guild: {guild.name} (ID: {guild.id})")

    async def _on_guild_remove(guild):
        logging.info(f"📉 Left guild: {guild.name} (ID: {guild.id})")

    bot.add_listener(_on_guild_join, "on_guild_join")
    bot.add_listener(_on_guild_remove, "on_guild_remove")

    return topgg_integration


async def post_commands_now(bot: commands.Bot) -> bool:
    """Helper to post commands immediately using an attached integration.

    Returns True on success.
    """
    topgg = getattr(bot, "_topgg_integration", None)
    if topgg is None:
        topgg = TopGGIntegration(bot)
    return await topgg.post_commands_to_topgg()
