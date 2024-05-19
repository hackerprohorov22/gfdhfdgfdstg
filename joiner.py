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
        if not self.is_running or not message.text:
            return

        match = re.search(r"https://t\.me/(joinchat/\S+|\+\S+)", message.text)
        if match:
            link = match.group()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as response:
                        if response.status == 200:
                            await self._client(JoinChannelRequest(link))
                            await message.reply("Присоединился к каналу по ссылке!")
                        else:
                            await message.reply("Не удалось присоединиться к каналу!")
            except Exception as e:
                await message.reply(f"Произошла ошибка: {str(e)}")
