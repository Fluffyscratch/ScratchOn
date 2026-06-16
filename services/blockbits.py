"""
BlockBit cloud variable communication.
"""

import json
import logging

import websockets
from scratchattach import Encoding

logger = logging.getLogger(__name__)

latest_value: int | str | None = None


def request_search(username: str) -> None:
    """
    Send a request to the Scratch project asking for a user's balance.

    The Scratch project listens for messages in the ``TO_HOST`` variable.
    """
    # cloud.set_var("TO_HOST", Encoding.encode(f"search&{username}"))


async def _fetch_response() -> None:
    """Connect to the cloud-data websocket and update *latest_value*."""
    global latest_value
    async with websockets.connect("wss://clouddata.scratch.mit.edu") as ws:
        await ws.send(json.dumps({"method": "handshake", "project_id": 669020072}))
        while True:
            message = json.loads(await ws.recv())
            if message.get("method") == "variables":
                variables = Encoding.decode(message.get("variables", {}))
                if variables:
                    latest_value = list(variables.values())[-1]


def get_latest_response() -> int | str | None:
    """
    Return the most recent response from the Scratch project.

    If the response is numeric it is returned as an ``int``.
    """
    # NOTE: _fetch_response is async and must be started as a background task
    # before calling this function; here we simply return the cached value.
    if latest_value is None:
        return None
    try:
        return float(latest_value)
    except (ValueError, TypeError):
        return latest_value
