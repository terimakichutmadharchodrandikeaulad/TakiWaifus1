class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7524032836"
    sudo_users = "8285724366", "8494985365", "7139800986"
    GROUP_ID = -1003149311859
    TOKEN = "8239143373:AAEnZAN1YtQmSWav4ZkgC4BQXhvmXlTpz7U"
    mongo_url = "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    PHOTO_URL = ["https://envs.sh/u3o.jpg/IMG20250817833.jpg", "https://envs.sh/GhJ.jpg/IMG20250925634.jpg", "https://envs.sh/GhJ.jpg/IMG20250925634.jpg"]
    SUPPORT_CHAT = "narzofamily"
    UPDATE_CHAT = "narzoxbot"
    BOT_USERNAME = "narzowaifubot"
    CHARA_CHANNEL_ID = "-1002017843882"
    api_id = 23562992
    api_hash = "e070a310ca3e76ebc044146b9829237c"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
