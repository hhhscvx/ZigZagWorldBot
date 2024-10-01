import asyncio
from random import randint, uniform

from pyrogram import Client

from data import config
from utils.core import logger
from utils.zigzagworld import ZigZagWorld


async def start(tg_client: Client, proxy: str | None = None):
    zigzag = ZigZagWorld(tg_client=tg_client, proxy=proxy)
    session_name = tg_client.name + '.session'

    await asyncio.sleep(uniform(*config.DELAY_CONN_ACCOUNT))

    if await zigzag.login():
        while True:
            try:
                account = await zigzag.get_me()
                logger.success(f"{session_name} | Signed in! Balance: {account['coins']} | "
                               f"Energy: {account['energy_count']}/{account['max_energy']}")
                await asyncio.sleep(1)

                # Tasks
                tasks = await zigzag.get_tasks()
                for task in tasks:
                    if task['type'] != 'tg':
                        complete_task = await zigzag.complete_task(task_id=task['id'])
                        if complete_task['success'] is True:
                            logger.success(f"{session_name} | Complete task «{task['name']}»! Earned +{task['award']}"
                                           f" | Current balance: {complete_task['user']['coins']}")
                        await asyncio.sleep(uniform(1, 3))

            except Exception as e:
                logger.error(f"{session_name} | Unknown Error: {e}")
                await asyncio.sleep(delay=3)
    else:
        await zigzag.logout()
