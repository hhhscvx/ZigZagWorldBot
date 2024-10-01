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
                        if complete_task.get('success') is True:
                            logger.success(f"{session_name} | Complete task «{task['name']}»! Earned +{task['award']}"
                                           f" | Current balance: {complete_task['user']['coins']}")
                        await asyncio.sleep(uniform(1, 3))

                # Buy Store
                store_items = await zigzag.get_store()
                for item in store_items:
                    if item['currency'] == 'stars':
                        continue
                    start_price = item['start_price']
                    multiply = item['multiply_price']
                    level = ([i for i in account['store'] if i['store_id'] == item['id']])[0]
                    print('LEVEL:', level)
                    curr_price = start_price * multiply * level
                    print('CURR PRICE:', curr_price)
                    if curr_price > config.MAX_STORE_ITEM_PRICE:
                        continue
                    item_buyed = await zigzag.buy_store_item(item_id=item['id'])
                    if item_buyed.get('success') is True:
                        logger.success(
                            f"{session_name} | Buy item «{item['name']}»! +{item['award']} {item['award_type']}")
                        account = item_buyed['user']

            except Exception as e:
                logger.error(f"{session_name} | Unknown Error: {e}")
                await asyncio.sleep(delay=3)
    else:
        await zigzag.logout()
