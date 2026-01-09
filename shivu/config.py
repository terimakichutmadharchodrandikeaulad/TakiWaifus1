# config.py
import os

class Config(object):
    LOGGER = True

    # --- Use environment variables; fallbacks are provided for development only ---
    # Owner ID (from my.telegram.org or your Telegram user id)
    OWNER_ID = int(os.environ.get("OWNER_ID", "7524032836"))

    # Comma-separated sudo user IDs in env, converted to a set of ints
    # Example env value: "8285724366,8494985365,7139800986"
    _sudo_env = os.environ.get("SUDO_USERS", "8285724366,8494985365,7139800986")
    SUDO_USERS = set(int(x.strip()) for x in _sudo_env.split(",") if x.strip())

    # Group / channel IDs (use negative for supergroups/channels)
    GROUP_ID = int(os.environ.get("GROUP_ID", "-1003149311859"))

    # Bot token (from BotFather) - put this in environment, do NOT commit
    TOKEN = os.environ.get("TOKEN", "8239143373:AAEnZAN1YtQmSWav4ZkgC4BQXhvmXlTpz7U")

    # MongoDB connection string - keep secret
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    # Photo URLs: comma-separated in env or fallback list
    _photos = os.environ.get(
        "PHOTO_URL",
        "https://envs.sh/u3o.jpg/IMG20250817833.jpg,https://envs.sh/GhJ.jpg/IMG20250925634.jpg"
    )
    PHOTO_URL = [u.strip() for u in _photos.split(",") if u.strip()]

    # Chat / channel usernames (no leading @ required, but allowed)
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "narzofamily")
    UPDATE_CHAT = os.environ.get("UPDATE_CHAT", "narzoxbot")

    # Bot username (short name without @)
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "narzowaifubot")

    # Character / channel id used by the bot (int)
    CHARA_CHANNEL_ID = int(os.environ.get("CHARA_CHANNEL_ID", "-1002017843882"))

    # API credentials from my.telegram.org
    API_ID = int(os.environ.get("API_ID", "23562992"))
    API_HASH = os.environ.get("API_HASH", "e070a310ca3e76ebc044146b9829237c")

    @classmethod
    def get_sudo_list(cls):
        """Return sudo users as a list (useful for iteration)."""
        return list(cls.SUDO_USERS)


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
