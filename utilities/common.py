import random
import requests
from time import sleep
from loguru import logger
from pyuseragents import random as random_useragent



def read_files():
    with open("./data/private_keys.txt") as file:
        private_keys = [line.strip() for line in file if line.strip()]

    with open("./data/proxies.txt") as file:
        proxies = [line.strip() for line in file if line.strip()]

    with open("./data/discord_tokens.txt") as file:
        tokens = [line.strip() for line in file if line.strip()]

    with open("./data/appeal_text.txt", encoding='utf-8') as file:
        answers = [line.strip() for line in file if line.strip()]

    while len(proxies) < len(private_keys):
        proxies.append(random.choice(proxies))

    return private_keys, tokens, proxies, answers

def create_client(proxy: str, proxy_change_link: str, index: str) -> requests.Session:
    session = requests.Session()

    if proxy_change_link:
        while True:
            r = session.get(proxy_change_link)
            if 'mobileproxy' in proxy_change_link and r.json().get('status') == 'OK':
                logger.debug(f'{index} | Proxy Changed IP: {r.json()["new_ip"]}')
                break
            elif not 'mobileproxy' in proxy_change_link and r.status_code == 200:
                logger.debug(f'{index} | Proxy Changed IP: {r.text}')
                break
            logger.error(f'{index} | Proxy Change IP error: {r.text} | {r.status_code}')
            sleep(10)

    if proxy:
        session.proxies.update({
            "http": proxy,
            "https": proxy,
        })

    session.headers.update({
        'authority': 'memefarm-api.memecoin.org',
        'accept': 'application/json',
        'accept-language': 'uk',
        'origin': 'https://www.memecoin.org',
        'user-agent': random_useragent()
    })

    return session
