from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    ALL_PLANETS: list[str] = ['bitrix', 'fossilith', 'mineris',
                              'cryptonix', 'hashaur', 'mesohex', 'terrablock']

    COMPLETE_TASKS: bool = True  # set to False after completing all tasks by soft

    RANDOM_TAPS_COUNT: list[int] = [5, 12]
    SLEEP_BETWEEN_TAP: list[float] = [0.3, 0.8]
    MIN_AVAILABLE_ENERGY: int = 15
    SLEEP_BY_MIN_ENERGY: list[int] = [600, 1500]

    SLEEP_WATCHING_AD: list[int] = [10, 20]

    MAX_STORE_ITEM_PRICE: int = 200_000

    USE_PROXY_FROM_FILE: bool = False  # True - if use proxy from file, False - if use proxy from accounts.json
    PROXY_PATH: str = "data/proxy.txt"
    PROXY_TYPE_TG: str = "socks5"  # proxy type for tg client. "socks4", "socks5" and "http" are supported
    # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
    PROXY_TYPE_REQUESTS: str = "socks5"

    WORKDIR: str = 'sessions/'

    # timeout in seconds for checking accounts on valid
    TIMEOUT: int = 30

    DELAY_CONN_ACCOUNT: list[int] = [5, 15]


config = Settings()
