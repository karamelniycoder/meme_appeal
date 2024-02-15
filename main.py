import os
import sys
import time
import random
import urllib3
import threading
from loguru import logger
from datetime import datetime
from eth_account import Account
from concurrent.futures import ThreadPoolExecutor

from config import PAUSE
from modules.form import Form
from modules.excel import Excel
from utilities.common import read_files
from modules.check_status import CheckStatus


file_lock = threading.Lock()

def configuration():
    urllib3.disable_warnings()
    format = "<light-cyan>{time:HH:mm:ss}</light-cyan> | <level> {level: <8}</level> | <white>{""message}</white>"
    logger.remove()
    logger.add(sys.stdout, colorize=True, format=format)
    logger.add(f"logs/{datetime.now().strftime('%m-%d_%H-%M-%S')}.log", format=format)
    logger.level("SUCCESS", color='<GREEN><bold>')
    logger.level("ERROR", color='<RED><bold>')


def append_to_file(file_path, string_to_append):
    with file_lock:
        with open(file_path, 'a') as file:
            file.write(string_to_append + '\n')


def check(index, key, proxy):
    if not proxy.startswith('http'): proxy = f'http://{proxy}'

    login = CheckStatus(index, key, proxy)
    username = login.execute()
    if username == "Not robot":
        append_to_file("./data/success_private_key.txt", key)
        append_to_file("./data/success_proxy.txt", proxy)
    elif username:
        append_to_file("./data/to_appeal_private_key.txt", key)
        append_to_file("./data/to_appeal_proxy.txt", proxy)
    else:
        append_to_file("./data/no_points_private_key.txt", key)
        append_to_file("./data/no_points_proxy.txt", proxy)
    

def check_appeal(index, key, proxy, token, answer, excel):
    if not proxy.startswith('http'): proxy = f'http://{proxy}'

    login = CheckStatus(index, key, proxy)
    username = login.execute()
    account = Account.from_key(key)
    
    if username == "Not robot":
        status = '✅ Not Robot'
        # append_to_file("./data/success_private_key.txt", key)
        # append_to_file("./data/success_proxy.txt", proxy)
    elif username:
        # append_to_file("./data/to_appeal_private_key.txt", key)
        # append_to_file("./data/to_appeal_proxy.txt", proxy)
        form = Form(index, proxy, username, token, account.address, answer)
        status = form.login()
    else:
        status = "❌ Cannot get twitter username"
        # append_to_file("./data/no_points_private_key.txt", key)
        # append_to_file("./data/no_points_proxy.txt", proxy)

    excel.add_account(index=index, privatekey=key, address=account.address, token=token, proxy=proxy, status=status)


def main():
    configuration()
    private_keys, tokens, proxies, answers = read_files()
    while len(proxies) < len(private_keys):
        proxies.append(proxies[0])
    
    print("Choose an option:")
    print("1. Run checker")
    print("2. Run checker + appeal")
    choice = int(input("Enter your choice: "))
    num_threads = int(input("Enter the number of threads: "))

    excel = Excel(total_len=len(private_keys))
    
    if choice == 1:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for index, (private_key, proxy) in enumerate(zip(private_keys, proxies)):
                executor.submit(check(index + 1, private_key, proxy))
                time.sleep(random.randint(PAUSE[0], PAUSE[1]))

    elif choice == 2:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for index, (private_key, token, proxy, answer) in enumerate(zip(private_keys, tokens, proxies, answers)):
                executor.submit(check_appeal(f"{index+1}/{len(private_keys)}", private_key, proxy, token, answer, excel))
                time.sleep(random.randint(PAUSE[0], PAUSE[1]))

if __name__ == "__main__":
    for folder_name in ['results', 'logs']:
        if not os.path.isdir(folder_name): os.mkdir(folder_name)

    main()
