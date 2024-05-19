"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/CakesTwix
    This program is free software; you can redistribute it and/or modify

"""

__version__ = (1, 0, 0)

# requires: aiohttp
# meta pic: https://www.pngall.com/wp-content/uploads/12/Avatar-Transparent.png
# meta developer: @cakestwix_mods

import logging
from .. import loader, utils
import re
import aiohttp
from telethon import functions
from hikkatl.types import Message

logger = logging.getLogger(__name__)


@loader.tds
class AutoJoinModule(loader.Module):
    """Модуль для автоматического присоединения к приватным каналам"""
    strings = {"name": "AutoJoinModule"}

    def __init__(self):
        self.is_running = False
        self.log_chat_id = None

    @loader.command
    async def start(self, message: Message):
        """Начать мониторинг сообщений"""
        self.is_running = True
        await self.log_to_chat("Мониторинг сообщений начат")
        if not self.log_chat_id:
            await self.create_log_chat(message)

    @loader.command
    async def stop(self, message: Message):
        """Остановить мониторинг сообщений"""
        self.is_running = False
        await self.log_to_chat("Мониторинг сообщений остановлен")

    async def create_log_chat(self, message: Message):
        """Создать группу для логов"""
        result = await self._client(functions.messages.CreateChatRequest(
            users=[await self._client.get_me()],
            title="AutoJoin Logs"
        ))
        self.log_chat_id = result.chats[0].id
        await self.log_to_chat(f"Создана группа для логов: {result.chats[0].title}")

    async def log_to_chat(self, log_message: str):
        """Отправить лог в группу"""
        if self.log_chat_id:
            await self._client.send_message(self.log_chat_id, log_message)

    async def watcher(self, message: Message):
        """Мониторинг сообщений"""
        if not self.is_running:
            return

        if "t.me/joinchat" in message.text or "t.me/+" in message.text:
            link = re.search(r"https://t\.me/[+a-zA-Z0-9_/-]+", message.text)
            if link:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(link.group()) as response:
                            if response.status == 200:
                                await self.log_to_chat(f"Успешно присоединился к каналу: {link.group()}")
                            else:
                                await self.log_to_chat(f"Не удалось присоединиться к каналу: {link.group()}")
                except Exception as e:
                    await self.log_to_chat(f"Ошибка при попытке присоединиться к каналу: {str(e)}")
