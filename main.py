import asyncio
import logging
import os
import sys
from discord import Client, AuthFailure, NotFound, Forbidden, HTTPException
from random import choices
from parse_data import parse_tokens_from_file, parse_http_proxies_from_file

file_log = logging.FileHandler('./log.txt')
console_out = logging.StreamHandler()
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.WARNING, handlers=(file_log, console_out))


class CustomError(Exception):
    pass


class MyClient(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id: int = kwargs.get("guild_id")
        self.channel_id: int = kwargs.get("channel_id")
        self.message_id: int = kwargs.get("message_id")
        self.emoji_list: list[str] = kwargs.get("emoji_list")
        self.emoji: str = kwargs.get("emoji")
        self.ds_link: str = kwargs.get("ds_link")
        self.account_number: int = kwargs.get("account_number")
        self.count_accounts: int = kwargs.get("count_accounts")

    async def on_ready(self):
        logging.warning(f"[{self.account_number}/{self.count_accounts}] Successfully logged as {self.user}")

        try:
            guild_name = await self.fetch_guild(self.guild_id)
        except (Exception,) as e:
            logging.error(
                f"[{self.account_number}/{self.count_accounts}] [ERROR] Аккаунта {self.user}"
                f" нету на сервере {self.guild_id}.")
            await self.close()
            return

        logging.warning(
            f"[{self.account_number}/{self.count_accounts}] Добавляю реакцию аккаунтом"
            f" {self.user} для сервера {guild_name}...")

        try:
            var = choices(self.emoji, weights)[0]
            await self.http.add_reaction(channel_id=self.channel_id, message_id=self.message_id, emoji=var)
            logging.warning(
                f"[{self.account_number}/{self.count_accounts}] [SUCCESS] Реакция аккаунтом {self.user}"
                f" для сервера {self.guild_id} поставлена!")
        except NotFound:
            logging.warning(
                f"[{self.account_number}/{self.count_accounts}]"
                f" Неправильный ID сервера/канала/сообщения. Реакция аккаунтом"
                f" {self.user} для сервера {self.guild_id} не была поставлена.")

        except Forbidden:
            logging.warning(
                f"[{self.account_number}/{self.count_accounts}]"
                f" У аккаунта нету прав на это действие. Реакция аккаунтом {self.user} для сервера"
                f" {self.guild_id} не была поставлена.")

        except HTTPException as e:
            logging.warning(
                f"[{self.account_number}/{self.count_accounts}] Ошибка >> {e}."
                f" Реакция аккаунтом {self.user} для сервера {self.guild_id} не была поставлена.")

        except Exception as e:
            logging.error(f"[{self.account_number}/{self.count_accounts}] Ошибка >> {e}")

        await self.close()


def parse_answer_to_bool(answer: str) -> bool:
    answer = answer.strip().lower()
    if answer == "yes" or answer == "y" or answer == "":
        return True
    else:
        return False


async def start():
    os.system("cls||clear")  # Erase the console

    print("""░██████╗░██╗██╗░░░██╗███████╗░█████╗░░██╗░░░░░░░██╗░█████╗░██╗░░░██╗
            ██╔════╝░██║██║░░░██║██╔════╝██╔══██╗░██║░░██╗░░██║██╔══██╗╚██╗░██╔╝
            ██║░░██╗░██║╚██╗░██╔╝█████╗░░███████║░╚██╗████╗██╔╝███████║░╚████╔╝░
            ██║░░╚██╗██║░╚████╔╝░██╔══╝░░██╔══██║░░████╔═████║░██╔══██║░░╚██╔╝░░
            ╚██████╔╝██║░░╚██╔╝░░███████╗██║░░██║░░╚██╔╝░╚██╔╝░██║░░██║░░░██║░░░
            ░╚═════╝░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝░░░╚═╝░░░

            created by @crypto_satana | @scissor_eth\n""")

    kwargs_dict = {}

    count_tokens: int = int(input("Введи сколько аккаунтов использовать >> ").strip())
    use_proxy: bool = parse_answer_to_bool(input("Использовать прокси (Y/n)? >> ").strip().lower())
    tokens_list: list[str] = parse_tokens_from_file("tokens.txt")[:count_tokens]  # parsing tokens from file
    count_accounts = len(tokens_list)

    if use_proxy:
        proxies_list: list[str] = parse_http_proxies_from_file(path="proxies.txt")  # parsing proxies
        if len(proxies_list) < count_accounts:
            logging.error("[ERROR] Количество прокси не совпадает с количеством токенов!")
            sys.exit()

    kwargs_dict["emoji_list"] = input("Введи список emoji через пробел >> ")
    kwargs_dict["emoji"] = kwargs_dict["emoji_list"].split(" ")  # reaction which we need
    use_probability: bool = parse_answer_to_bool(input("Ввести соотношеняе на emoji (Y/n)?>> ").strip().lower())
    global weights
    weights = []

    def probability_input(i):
        try:
            var = float(input("Введите процентное значение для " + str(i.strip()) + " emoji>>").strip()) / 100
            if var < 0 or var > 1:
                raise CustomError
            weights.append(var)
        except Exception as e:
            print("Неверно указано значение")
            probability_input(i)

    def probability_func(use_probability):
        try:
            if use_probability:
                for i in kwargs_dict["emoji"]:
                    probability_input(i)
            else:
                var = 1 / len(kwargs_dict["emoji"])
                for i in kwargs_dict["emoji"]:
                    weights.append(var)
            if sum(weights) != 1:
                weights.clear()
                raise CustomError

        except Exception as e:
            print("Введенное количество процентов не равно 100. Введите еще раз")
            probability_func(use_probability)

    probability_func(use_probability)

    kwargs_dict["ds_link"] = input("Введи ссылку на сообщение с сервера >> ").strip()
    kwargs_dict["guild_id"] = int(kwargs_dict["ds_link"].split("/")[4])
    kwargs_dict["channel_id"] = int(kwargs_dict["ds_link"].split("/")[5])  # on server channel ID
    kwargs_dict["message_id"]: int = int(
        kwargs_dict["ds_link"].split("/")[6])  # message ID
    kwargs_dict["count_accounts"] = count_accounts

    async def run_acc(account_number, client_token):
        kwargs_dict["account_number"] = account_number + 1

        if use_proxy:
            proxy_url = proxies_list[account_number] 
            client = MyClient(token=client_token, proxy_url=proxy_url, **kwargs_dict)  # run client with proxie
        else:
            client = MyClient(token=client_token, **kwargs_dict)  # run client without proxie

        try:
            await client.login(client_token)
            await client.connect()

        except AuthFailure:
            logging.warning(
                f"[НЕВАЛИДНЫЙ ТОКЕН] [{account_number + 1}/{count_accounts}]"
                f" Токен {client_token} просрочен или не работает прокси.")

    coros = [run_acc(account_number, client_token) for account_number, client_token in enumerate(tokens_list)]
    await asyncio.gather(*coros)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(start())
