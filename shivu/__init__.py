import logging
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
from shivu.config import Development as Config

# ---------------- LOGGING ---------------- #

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)

LOGGER = logging.getLogger(__name__)

# ---------------- CONFIG ---------------- #

API_ID = Config.API_ID
API_HASH = Config.API_HASH
TOKEN = Config.TOKEN
GROUP_ID = Config.GROUP_ID
CHARA_CHANNEL_ID = Config.CHARA_CHANNEL_ID
MONGO_URL = Config.MONGO_URL
PHOTO_URL = Config.PHOTO_URL
SUPPORT_CHAT = Config.SUPPORT_CHAT
UPDATE_CHAT = Config.UPDATE_CHAT
BOT_USERNAME = Config.BOT_USERNAME
SUDO_USERS = Config.SUDO_USERS
OWNER_ID = Config.OWNER_ID

# ---------------- DATABASE ---------------- #

mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["Character_catcher"]

collection = db["anime_characters_lol"]
user_totals_collection = db["user_totals_lmaoooo"]
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db["group_user_totalsssssss"]
top_global_groups_collection = db["top_global_groups"]
pm_users = db["total_pm_users"]

# ---------------- PYROGRAM BOT ---------------- #

app = Client(
    name="Shivu",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    in_memory=True,
)

# ---------------- START BOT ---------------- #

if __name__ == "__main__":
    LOGGER.info("🚀 Shivu bot starting...")
    app.run()
