"""
Utility functions for the bot.
"""
import os
import scratchattach as scratch
from scratchattach import MultiEventHandler
from pyppeteer import launch


async def dc2scratch(username: str) -> str | None:
    """
    Converts a Discord username to a Scratch username using stored bindings.
    
    :param username: Discord username to look up.
    :return: Corresponding Scratch username, or None if not found.
    """
    with open("ScratchOn_private/dcusers.txt") as f1, open("ScratchOn_private/scusers.txt") as f2:
        dc_users = [line.strip() for line in f1.readlines()]
        sc_users = [line.strip() for line in f2.readlines()]

        if username in dc_users:
            index = dc_users.index(username)
            return sc_users[index]
        return None


async def replace_last_screenshot(url: str, screenshot_path: str = 'screenshot.png'):
    """
    Takes a screenshot of a URL, replacing any existing screenshot.
    
    :param url: URL to screenshot.
    :param screenshot_path: Path to save the screenshot.
    """
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
        print(f"Deleted the previous screenshot: {screenshot_path}")
    
    browser = await launch(
        headless=True,
        executablePath="/usr/bin/chromium-browser"
    )
    page = await browser.newPage()
    await page.goto(url)
    await page.screenshot({'path': screenshot_path})
    print(f"New screenshot saved as: {screenshot_path}")
    await browser.close()


def remove_line_by_index(file_path: str, index_to_remove: int):
    """
    Removes a specific line from a file by its index.
    
    :param file_path: Path to the file.
    :param index_to_remove: Zero-based index of the line to remove.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if 0 <= index_to_remove < len(lines):
        del lines[index_to_remove]

    with open(file_path, 'w') as file:
        file.writelines(lines)


def update_pings():
    """
    Updates the message event handlers for users who have ping notifications enabled.
    """
    with open("ScratchOn_private/users2ping.txt") as file:
        whatever = False
        temp = ...
        for item in file.readlines():
            if item == "\n" or item == "":
                break
            if whatever:
                temp = temp, scratch.get_user(item.strip()).message_events()
            else:
                whatever = True
                temp = scratch.get_user(item.strip()).message_events()
        
        multievents = len(file.readlines()) - 1 != 1

    if multievents:
        combined = MultiEventHandler(temp)
        print(temp)
        print(combined)

        @combined.event(function=combined)
        def on_ready():
            print("Message trackers are up to date !")

        @combined.request(function=combined)
        def your_request():
            ...

        combined.start()
    else:
        events = temp

        @events.event()
        def on_count_change(old_count, new_count):
            print("message count changed from", old_count, "to", new_count)

        @events.event()
        def on_ready():
            print("Event listener ready!")

        events.start()


def limiter(text: str, limit: int) -> str:
    """
    Limits text to a certain length and adds ellipsis.
    
    :param text: Text to limit.
    :param limit: Maximum character length.
    :return: Limited text with ellipsis.
    """
    result = text[:limit]
    return f"{result}..."
