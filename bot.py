import nextcord
from nextcord.ext import commands
import os
import logging
import colorlog
import aiosqlite
from dotenv import load_dotenv
from os import getenv
from config import APPLICATION_DETAILS
from json import load, dump

load_dotenv()

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s] %(asctime)s - %(name)s: %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)

logging.getLogger("nextcord").setLevel(logging.WARNING)
logging.getLogger("discord").setLevel(logging.WARNING)


class Bot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.application_details = {}
        self.debuggingMode = False
        self.db: aiosqlite.Connection = None

    async def SaveDetails(self, userID: int, key: str, value: any) -> bool:
        try:
            if userID not in self.application_details:
                self.application_details[userID] = {}

            self.application_details[userID][key] = value

            with open(APPLICATION_DETAILS, "r") as file:
                data = load(file)

            data[userID] = self.application_details[userID]

            with open(APPLICATION_DETAILS, "w") as file:
                dump(data, file, indent=4)

            return
        except Exception as e:
            if self.debuggingMode:
                raise e
            return e


intents = nextcord.Intents.default()
intents.members = True
# Command prefix is necessary for some reason
bot = Bot(command_prefix="!", intents=intents)
bot.debuggingMode = True


@bot.event
async def on_ready() -> None:
    bot.db = await aiosqlite.connect("fissionbot.db")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS referrals ("
                         "referrer_id BIGINT, count INTEGER DEFAULT 0)")

    # load_application_details()
    # Future task

    logger.info(f"Logged in as {bot.user.name} - {bot.user.id}")
    return await bot.change_presence(
        activity=nextcord.Activity(
            type=nextcord.ActivityType.watching,
            name="EXPERIMENTAL"))

# Manually load apply since it's in a subfolder
bot.load_extension("cogs.apply")

# Optionally auto-load others
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(getenv("DISCORD_TOKEN"))
