import logging

from environs import Env, EnvError

from bot import RemovePremiumStickerBot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


class ConfigNotFound(Exception):
    pass


def parse_env():
    env = Env()
    env.read_env()

    try:
        _api_key = env.str("TG_API_KEY")
    except EnvError:
        raise ConfigNotFound("Telegram API Key not detected.")

    delete_msg = env.str("DELETE_MSG", None)
    no_permission_msg = env.str("NO_PERMISSION_MSG", None)
    other_error_msg = env.str("OTHER_ERROR_MSG", None)

    _msg = {
        "delete": delete_msg,
        "permission": no_permission_msg,
        "error": other_error_msg,
    }

    return _api_key, _msg


if __name__ == "__main__":
    api_key, msg = parse_env()
    bot = RemovePremiumStickerBot(api_key, msg)
    bot.register()
    bot.start()
