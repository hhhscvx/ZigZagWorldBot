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

    tasks_completed = False

    if await zigzag.login():
        while True:
            try:
                account = await zigzag.get_me()
                logger.success(f"{session_name} | Signed in! Balance: {account['coins']} | "
                               f"Energy: {account['energy_count']}/{account['max_energy']}")
                await asyncio.sleep(1)

                # Tasks
                if config.COMPLETE_TASKS is True and tasks_completed is False:
                    tasks = await zigzag.get_tasks()
                    await asyncio.sleep(1)
                    for task in tasks:
                        if task['type'] != 'tg':
                            complete_task = await zigzag.complete_task(task_id=task['id'])
                            if complete_task.get('success') is True:
                                logger.success(f"{session_name} | Complete task «{task['name']}»! Earned +{task['award']}"
                                               f" | Current balance: {complete_task['user']['coins']}")
                            await asyncio.sleep(uniform(1, 3))
                    tasks_completed = True

                # Buy Store
                for _ in range(20):
                    store_items = await zigzag.get_store()
                    await asyncio.sleep(1)
                    for item in store_items:
                        if item['currency'] == 'stars':
                            continue
                        start_price = item['start_price']
                        multiply = item['multiply_price']
                        level = ([i for i in account['store'] if i['store_id'] == item['id']])
                        level = level[0]['level'] if level else 0
                        print('LEVEL:', level)
                        curr_price = start_price * multiply * level if level != 0 else start_price
                        print('CURR PRICE:', curr_price)
                        if curr_price > config.MAX_STORE_ITEM_PRICE:
                            continue
                        item_buyed = await zigzag.buy_store_item(item_id=item['id'])
                        if item_buyed.get('success') is True:
                            logger.success(
                                f"{session_name} | Buy item «{item['name']}»! +{item['award']} {item['award_type']}")
                            account = item_buyed['user']
                        await asyncio.sleep(uniform(1, 2))

                # Taps
                account = await zigzag.get_me()
                available_taps = account['energy_count']
                await asyncio.sleep(1)
                while True:
                    if available_taps > config.MIN_AVAILABLE_ENERGY:
                        taps_count = randint(*config.RANDOM_TAPS_COUNT)
                        tap = await zigzag.send_tap(taps_count=taps_count)
                        if tap.get('success') is True:
                            logger.success(
                                f"{session_name} | Tapped +{taps_count} taps! Energy: {tap['user']['energy_count']}/{tap['user']['max_energy']} | Balance: {tap['user']['coins']}")
                            available_taps = tap['user']['energy_count']
                        await asyncio.sleep(uniform(*config.SLEEP_BETWEEN_TAP))
                    else:
                        account = await zigzag.get_me()
                        sleep_time = uniform(*config.SLEEP_BY_MIN_ENERGY)
                        logger.info(
                            f"{session_name} | Energy: {account['energy_count']}/{account['max_energy']} | Balance: {account['coins']}")
                        logger.info(f" | Sleep {int(sleep_time)}s...")
                        await asyncio.sleep(sleep_time)
                        break

            except Exception as error:
                logger.error(f"{session_name} | Unknown Error: {error}")
                raise error
                await asyncio.sleep(delay=3)
    else:
        await zigzag.logout()
