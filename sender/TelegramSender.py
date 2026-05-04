import logging
import asyncio

from concurrent.futures import ThreadPoolExecutor
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import RetryAfter
from time import sleep


class TelegramSender:
    def __init__(
        self,
        token,
        chat_id,
        alert_chat_id=0,
        bot_emoji="\U0001F916",  # 🤖
        top_emoji="\U0001F3C6",  # 🏆
        news_emoji="\U0001F4F0",  # 📰
    ):

        self.token = token
        self.chat_id = chat_id
        self.alert_chat_id = alert_chat_id

        self.bot_emoji = bot_emoji
        self.top_emoji = top_emoji
        self.news_emoji = news_emoji

        self.bot = Bot(self.token)

        self.logger = logging.getLogger("telegram-sender")

    def is_alert_chat_enabled(self):
        return self.alert_chat_id != 0 and self.alert_chat_id != self.chat_id

    async def send_message(self, message, is_alert_chat=False):
        chat_id = self.chat_id if not is_alert_chat else self.alert_chat_id

        self.logger.info(message)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
                return
            except RetryAfter as e:
                self.logger.error(
                    "Flood limit is exceeded. Sleep {} seconds.", e.retry_after
                )
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                self.logger.error("Failed to send message: %s", e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                else:
                    self.logger.error("Message failed after %d retries: %s", max_retries, message)

    async def send_generic_message(self, message, args=None, is_alert_chat=False):
        if args is not None:
            message = message.format(args)
        await self.send_message(self.bot_emoji + " " + message, is_alert_chat)

    async def send_report_message(self, message, args=None, is_alert_chat=False):
        if args is not None:
            message = message.format(args)
        await self.send_message(self.top_emoji + " " + message, is_alert_chat)

    async def send_news_message(self, message, args=None, is_alert_chat=False):
        if args is not None:
            message = message.format(args)
        await self.send_message(self.news_emoji + " " + message, is_alert_chat)
