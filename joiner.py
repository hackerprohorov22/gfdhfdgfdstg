from hikkatl.types import Message
from .. import loader, utils
import re
import aiohttp
import logging
from telethon import functions

logger = logging.getLogger(__name__)

@loader.tds
class AutoJoinModule(loader.Module):
    """Модуль для автоматического присоединения к приватным каналам"""

    strings = {
        "name": "AutoJoinModule",
        "monitoring_started": "Мониторинг сообщений начат",
        "monitoring_stopped": "Мониторинг сообщений остановлен",
        "log_chat_created": "Создана группа для логов: {title}",
        "joined_channel": "Успешно присоединился к каналу: {link}",
        "failed_to_join": "Не удалось присоединиться к каналу: {link}",
        "error_joining": "Ошибка при попытке присоединиться к каналу: {error}",
        "id": "Id",
        "uuid": "UUID",
        "firstname": "Firstname",
        "lastname": "Lastname",
        "username": "Username",
        "password": "Password",
        "email": "Email",
        "ip": "IP",
        "macAddress": "MAC-address",
        "website": "Website",
        "image": "Image"
    }

    async def prandomcmd(self, message: Message):
        """Get random people"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://fakerapi.it/api/v1/users?_quantity=1") as get:
                data = (await get.json())["data"][0]
                await session.close()

        string = "".join(f"<b>{self.strings[key]}</b>: <code>{val}</code>\n" for val, key in data.items())

        await utils.answer(message, string)

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.me = await client.get_me()
        self.log_chat_id = self._db.get(self.name, "log_chat_id", None)

    @loader.command
    async def start(self, message: Message):
        """Начать мониторинг сообщений"""
        self.is_running = True
        if not self.log_chat_id:
            await self.create_log_chat(message)
        await self.log_to_chat(self.strings["monitoring_started"])

    @loader.command
    async def stop(self, message: Message):
        """Остановить мониторинг сообщений"""
        self.is_running = False
        await self.log_to_chat(self.strings["monitoring_stopped"])

    async def create_log_chat(self, message: Message):
        """Создать группу для логов"""
        result = await self._client(functions.messages.CreateChatRequest(
            users=[self.me.id],
            title="AutoJoin Logs"
        ))
        self.log_chat_id = result.chats[0].id
        self._db.set(self.name, "log_chat_id", self.log_chat_id)
        await self.log_to_chat(self.strings["log_chat_created"].format(title=result.chats[0].title))

    async def log_to_chat(self, log_message: str):
        """Отправить лог в группу"""
        if self.log_chat_id:
            await self._client.send_message(self.log_chat_id, log_message)
        else:
            logger.error("Лог-группа не создана. Пожалуйста, запустите /start для создания лог-группы.")

    async def watcher(self, message: Message):
        """Мониторинг сообщений"""
        if not self.is_running:
            return

        if "t.me/joinchat" in message.text or "t.me/+" in message.text:
            link = re.search(r"https://t\.me/[+a-zA-Z0-9_/-]+", message.text)
            if link:
                try:
                    result = await self._client(functions.channels.JoinChannelRequest(channel=link.group()))
                    await self.log_to_chat(self.strings["joined_channel"].format(link=link.group()))
                except Exception as e:
                    await self.log_to_chat(self.strings["failed_to_join"].format(link=link.group()))
                    await self.log_to_chat(self.strings["error_joining"].format(error=str(e)))
