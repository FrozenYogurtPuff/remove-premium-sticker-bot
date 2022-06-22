import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    filters,
    MessageHandler,
    ContextTypes,
)
from telegram.error import BadRequest
from telegram.helpers import escape_markdown

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def escape_user_markdown(raw: str, update: Update) -> str:
    markdown = escape_markdown(raw, version=2)
    segments = markdown.split("$user")
    text = update.message.from_user.mention_markdown_v2().join(segments)
    return text


class RemovePremiumStickerBot:
    def __init__(self, api_key: str, msg: dict[str, Optional[str]]):
        self._app = Application.builder().token(api_key).build()
        self._msg = msg

    async def send_if_set(
        self, key: str, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if self._msg[key]:
            text = escape_user_markdown(self._msg[key], update)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=text, parse_mode="MarkdownV2"
            )

    def register(self):
        async def remove_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.delete()
            logger.debug(
                f"Delete message from user {update.message.from_user.full_name}"
            )
            await self.send_if_set("delete", update, context)

        async def permission_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.info(
                f"Occur {context.error} when delete message from user {update.message.from_user.full_name}"
            )
            if isinstance(context.error, BadRequest):
                await self.send_if_set("permission", update, context)
            else:
                await self.send_if_set("error", update, context)

        check_sticker_handler = MessageHandler(filters.Sticker.PREMIUM, remove_sticker)
        self._app.add_handler(check_sticker_handler)

        self._app.add_error_handler(permission_error)

    def start(self):
        self._app.run_polling(drop_pending_updates=True)
