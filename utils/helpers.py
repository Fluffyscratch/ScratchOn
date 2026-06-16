"""
Utility functions for the bot.
"""

import logging
import os

import scratchattach as scratch
from scratchattach import MultiEventHandler

logger = logging.getLogger(__name__)


async def dc2scratch(username: str) -> str | None:
    """
    Convert a Discord username to a Scratch username using stored bindings.

    :param username: Discord username to look up.
    :return: Corresponding Scratch username, or ``None`` if not found.
    """
    with open("private/dcusers.txt") as dc_file, open("private/scusers.txt") as sc_file:
        dc_users = [line.strip() for line in dc_file]
        sc_users = [line.strip() for line in sc_file]

    if username in dc_users:
        index = dc_users.index(username)
        return sc_users[index]
    return None


async def replace_last_screenshot(
    url: str,
    screenshot_path: str = "screenshot.png",
) -> None:
    """
    Take a screenshot of *url*, replacing any existing file at *screenshot_path*.

    :param url:            URL to screenshot.
    :param screenshot_path: Destination path.
    """
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
        logger.info("Deleted previous screenshot: %s", screenshot_path)

    from pyppeteer import launch

    browser = await launch(headless=True, executablePath="/usr/bin/chromium-browser")
    page = await browser.newPage()
    await page.goto(url)
    await page.screenshot({"path": screenshot_path})
    logger.info("New screenshot saved: %s", screenshot_path)
    await browser.close()


def remove_line_by_index(file_path: str, index_to_remove: int) -> None:
    """
    Remove a specific line from *file_path* by its zero-based index.

    :param file_path:       Path to the file.
    :param index_to_remove: Zero-based line index to remove.
    """
    with open(file_path, "r") as fh:
        lines = fh.readlines()

    if 0 <= index_to_remove < len(lines):
        del lines[index_to_remove]

    with open(file_path, "w") as fh:
        fh.writelines(lines)


def update_pings() -> None:
    """
    Update the message-event handlers for users with ping notifications enabled.
    """
    with open("private/users2ping.txt") as fh:
        lines = fh.readlines()

    event_handler = None
    for line in lines:
        name = line.strip()
        if not name:
            break
        user_events = scratch.get_user(name).message_events()
        event_handler = (
            user_events
            if event_handler is None
            else MultiEventHandler(event_handler, user_events)
        )

    if event_handler is None:
        return

    @event_handler.event
    def on_ready():
        logger.info("Message trackers are up to date!")

    @event_handler.request
    def on_request():
        pass

    event_handler.start()


def limiter(text: str, limit: int) -> str:
    """
    Truncate *text* to *limit* characters and append an ellipsis.

    :param text:  Text to truncate.
    :param limit: Maximum character length.
    :return: Truncated text.
    """
    return text[:limit] + "..."
