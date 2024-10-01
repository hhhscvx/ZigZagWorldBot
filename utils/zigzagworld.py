
import asyncio
from random import uniform
from urllib.parse import quote, unquote

import aiohttp
from aiohttp_socks import ProxyConnector
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw.types import WebViewResultUrl
from fake_useragent import UserAgent

from data import config
from utils.core import logger


class ZigZagWorld:
    def __init__(self, tg_client: Client, proxy: str | None = None) -> None:
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.proxy = f"{config.PROXY_TYPE_REQUESTS}://{proxy}" if proxy else None
        connector = ProxyConnector.from_url(url=self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPE_TG,
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        headers = {"User-Agent": UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def logout(self) -> None:
        await self.session.close()

    async def login(self) -> bool | None:
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"{self.session_name} | Session {self.session_name} invalid")
            await self.logout()
            return None

        self.session.headers['Auth'] = query
        self.session.headers['Authorization'] = ''
        return True

    async def get_me(self) -> dict:
        resp = await self.session.get("https://api.zigzagworld.online/api/account/me")
        return await resp.json()

    async def watch_add(self, sleep_time: int) -> dict:
        await asyncio.sleep(sleep_time)
        resp = await self.session.get("https://api.zigzagworld.online/api/rewards/ad")
        return await resp.json()  # success, user

    async def send_tap(self, taps_count: int) -> dict:
        resp = await self.session.post("https://api.zigzagworld.online/api/taps",
                                       json={'taps': taps_count})

        return await resp.json()

    async def get_daily_rewards(self) -> list[dict]:
        resp = await self.session.get("https://api.zigzagworld.online/api/rewards")
        return await resp.json()

    async def collect_daily_reward(self, reward_type: str) -> dict:  # sleep watching ad нужен будет
        resp = await self.session.post("https://api.zigzagworld.online/api/rewards",
                                       json={'type': reward_type})
        return await resp.json()  # success, user

    async def get_store(self) -> list[dict]:
        resp = await self.session.get("https://api.zigzagworld.online/api/store")
        return await resp.json()

    async def buy_store_item(self, item_id: int) -> dict:
        resp = await self.session.post("https://api.zigzagworld.online/api/store",
                                       json={'id': item_id})
        return await resp.json()  # success, user

    async def get_tasks(self) -> list[dict]:
        resp = await self.session.get("https://api.zigzagworld.online/api/tasks")
        return await resp.json()

    async def complete_task(self, task_id: int) -> dict:
        resp = await self.session.post("https://api.zigzagworld.online/api/tasks/complete",
                                       json={'id': task_id})
        return await resp.json()  # Прост чекать что success true

    async def get_tg_web_data(self) -> str | None:
        try:
            await self.tg_client.connect()

            await self.tg_client.send_message('ZigZagWorldBot', '/start')
            await asyncio.sleep(uniform(1.5, 2))

            web_view: WebViewResultUrl = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('ZigZagWorldBot'),
                bot=await self.tg_client.resolve_peer('ZigZagWorldBot'),
                platform='android',
                from_bot_menu=False,
                url="https://front.zigzagworld.online/"
            ))
            await self.tg_client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            print(f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}")

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"

        except Exception as err:
            return
