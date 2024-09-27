import asyncio
from random import uniform

from pyrogram import Client

from data import config
from utils.core import logger
from utils.zigzagworld import ZigZagWorld


async def start(tg_client: Client, proxy: str | None = None):
    zigzag = ZigZagWorld(tg_client=tg_client, proxy=proxy)
    session_name = tg_client.name + '.session'

    await asyncio.sleep(uniform(*config.DELAY_CONN_ACCOUNT))

    while True:
        try:
            ...

        except Exception as e:
            logger.error(f"{session_name} | Unknown Error: {e}")
            await asyncio.sleep(delay=3)
