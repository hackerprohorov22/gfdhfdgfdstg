from telethon.tl.functions.channels import CreateChannelRequest

@loader.tds
class AutoJoinModule(loader.Module):
    """Модуль для автоматического присоединения к приватным каналам"""
    strings = {"name": "AutoJoinModule"}

    def __init__(self):
        self.is_running = False
        self.log_channel = None

    @loader.command
    async def start(self, message: Message):
        """Начать мониторинг сообщений"""
        self.is_running = True
        self.log_channel = await self._client(CreateChannelRequest(
            "AutoJoin Logs", "Логи автоматического присоединения", megagroup=True))
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
                    await self._client(JoinChannelRequest(link.group()))
                    await self._client.send_message(self.log_channel, f"Успешно присоединился к {link.group()}")
                except Exception as e:
                    await self._client.send_message(self.log_channel, f"Не удалось присоединиться к {link.group()}. Ошибка: {str(e)}")
