"""
Blockbit communication portal
"""

import scratchattach as sa
from scratchattach import Encoding

import websockets
import json


# Login to Scratch
with open("ScratchOn_private/password.txt") as f:
    session = sa.login(username="_Scratch-On_", password=f.readlines()[0])

# Connect to the Blockbit project's cloud variables
cloud = session.connect_cloud(669020072)
latest_value = 1


def request_search(username: str):
    """
    Send a request to Scratch asking for a user's balance or data.

    The Scratch project listens for messages in the TO_HOST variable.
    """
    cloud.set_var("TO_HOST", Encoding.encode(f"search&{username}"))


async def get_response():
    global latest_value
    async with websockets.connect("wss://clouddata.scratch.mit.edu") as ws:
        await ws.send(json.dumps({"method": "handshake", "project_id": 669020072}))
        while True:
            message = json.loads(await ws.recv())
            if message.get("method") == "variables":
                variables = Encoding.decode(message.get("variables", {}))
                if variables:
                    # Get the last variable value received
                    last_var = list(variables.values())[-1]
                    latest_value = last_var


def get_latest_response() -> int | str | None:
    """
    Get the most recent response sent back by the Scratch project.

    If the response is a number, return it as an int. Otherwise, return it as a string.
    """
    get_response()
    return float(latest_value) if latest_value is not None else None
