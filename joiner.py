from hikkatl.types import Message
from .. import loader, utils
import re
import aiohttp

@loader.tds
class AutoJoinModule(loader.Module):
    """Модуль для автоматического присоединения к приватным каналам"""
    strings = {"name": "AutoJoinModule"}

    def __init__(self):
        self.is_running = False

    @loader.command
    async def start(self, message: Message):
        """Начать мониторинг сообщений"""
        self.is_running = True
        await utils.answer(message, "Мониторинг сообщений начат")

    @loader.command
    async def stop(self, message: Message):
        """Остановить мониторинг сообщений"""
        self.is_running = False
        await utils.answer(message, "Мониторинг сообщений остановлен")

    async def watcher(self, message: Message):
        """Мониторинг сообщений"""
        if not self.is_running:
            return

        if "joinchat" in message.text:
            link = re.search(r"https://t\.me/joinchat/\S+", message.text)
            if link:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(link.group()) as response:
                            if response.status == 200:
                                await message.reply("Присоединился к каналу по ссылке!")
                            else:
                                await message.reply("Не удалось присоединиться к каналу!")
                except Exception as e:
                    await message.reply(f"Произошла ошибка: {str(e)}")
