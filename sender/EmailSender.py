import logging
import aiosmtplib
from email.message import EmailMessage
from datetime import datetime


class EmailSender:
    def __init__(
        self,
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        email_from=None,
        email_to=None,
        username=None,
        password=None,
        use_tls=True,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email_from = email_from
        self.email_to = email_to
        self.username = username
        self.password = password
        self.use_tls = use_tls

        self.logger = logging.getLogger("email-sender")

    def is_enabled(self):
        return bool(self.email_from and self.email_to and self.password)

    async def send_message(self, subject, body, html_body=None):
        if not self.is_enabled():
            self.logger.debug("Email not configured, skipping.")
            return

        msg = EmailMessage()
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        msg["Subject"] = subject
        msg.set_content(body)

        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
            )
            self.logger.info("Email sent: %s", subject)
        except Exception as e:
            self.logger.error("Failed to send email: %s", e)

    async def send_alert(self, emoji, symbol, interval, change, price, alert_type="PUMP"):
        direction = "PUMP" if change > 0 else "DUMP"
        subject = f"{emoji} {direction} {symbol} {interval} {change:.2f}%"
        body = f"""{emoji} *{direction} ALERT*

Symbol: {symbol}
Interval: {interval}
Change: {change:.2f}%
Price: {price}

Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        await self.send_message(subject, body)

    async def send_generic_message(self, message):
        await self.send_message(
            f"🤖 Binance Alert - {datetime.now().strftime('%H:%M')}",
            message,
        )

    async def send_health_ping(self, monitored_pairs, errors_since_last=None):
        uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"✅ Bot Alive - {uptime}"
        body = f"""✅ Binance Pump & Dump Alerts - Health Check

Status: Running ✅
Monitored Pairs: {monitored_pairs}
Time: {uptime}

---
Sent automatically every hour to confirm bot is alive.
"""
        if errors_since_last:
            body += f"\nErrors since last ping: {errors_since_last}"

        await self.send_message(subject, body)

    async def send_error_alert(self, error_message):
        await self.send_message(
            f"⚠️ Bot Error - {datetime.now().strftime('%H:%M')}",
            f"""⚠️ BINANCE ALERT SYSTEM ERROR

Error: {error_message}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""",
        )