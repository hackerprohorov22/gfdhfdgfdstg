from .. import loader, utils
import re
from telethon import events

@loader.tds
class AutoJoinChannelsMod(loader.Module):
    """Автоматически присоединяется к каналам по ссылкам"""
    strings = {"name": "AutoJoinChannels"}

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._running = False

    async def autostartcmd(self, message):
        """Запустить мониторинг каналов"""
        self._running = True
        await utils.answer(message, self.strings('Мониторинг каналов запущен!'))

    async def autostopcmd(self, message):
        """Остановить мониторинг каналов"""
        self._running = False
        await utils.answer(message, self.strings('Мониторинг каналов остановлен!'))

    @loader.unrestricted
    @loader.ratelimit
    async def watcher(self, message):
        if not self._running:
            return
        if re.search(r't.me/joinchat/', message.text):
            link = re.findall(r't.me/joinchat/\S+', message.text)[0]
            await self._client(JoinChannelRequest(link))
            await utils.answer(message, f'Присоединился к каналу: {link}')

