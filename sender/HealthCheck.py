import asyncio
import logging
from datetime import datetime, timedelta
from time import time


class HealthChecker:
    def __init__(
        self,
        telegram=None,
        email=None,
        ping_interval_seconds=3600,
    ):
        self.telegram = telegram
        self.email = email
        self.ping_interval_seconds = ping_interval_seconds

        self.last_ping_time = int(time())
        self.start_time = int(time())
        self.errors_since_last_ping = 0

        self.logger = logging.getLogger("health-checker")

    async def record_error(self):
        self.errors_since_last_ping += 1

    async def check_and_send_ping(self, monitored_pairs):
        current_time = int(time())

        if current_time - self.last_ping_time >= self.ping_interval_seconds:
            await self.send_health_ping(monitored_pairs)
            self.last_ping_time = current_time
            self.errors_since_last_ping = 0

    async def send_health_ping(self, monitored_pairs):
        uptime_seconds = int(time()) - self.start_time
        uptime_str = self._format_uptime(uptime_seconds)

        message = f"""🤖 *Bot Health Check*

Status: ✅ Running
Uptime: {uptime_str}
Monitored Pairs: {monitored_pairs}
Errors Since Last Ping: {self.errors_since_last_ping}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        if self.telegram:
            try:
                await self.telegram.send_generic_message(message)
                self.logger.info("Health ping sent to Telegram")
            except Exception as e:
                self.logger.error("Failed to send health ping to Telegram: %s", e)

        if self.email and self.email.is_enabled():
            try:
                await self.email.send_health_ping(
                    monitored_pairs,
                    self.errors_since_last_ping,
                )
                self.logger.info("Health ping sent to Email")
            except Exception as e:
                self.logger.error("Failed to send health ping to Email: %s", e)

    def _format_uptime(self, seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"