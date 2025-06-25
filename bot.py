import nextcord
from nextcord.ext import commands
import os
import logging
import colorlog
import aiosqlite
from dotenv import load_dotenv
from os import getenv, path
from config import APPLICATION_DETAILS
from json import load, dump

load_dotenv()

_handler = colorlog.StreamHandler()
_handler.setFormatter(
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
logging.getLogger("nextcord").setLevel(logging.WARNING)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("aiosqlite").setLevel(logging.WARNING)

logger.handlers.clear()
logger.addHandler(_handler)


class Bot(commands.Bot):
    def __init__(self, command_prefix: str, intents, debuggingMode: bool) -> None:  # noqa: E501
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.application_details: dict[int, dict[str, str]] = {}
        self.debuggingMode: bool = debuggingMode
        self.db: aiosqlite.Connection = None
        self.logger = logger

        logger.setLevel(logging.DEBUG) if debuggingMode \
            else logger.setLevel(logging.INFO)

    async def SaveDetails(self, userID: int, key: str, value: any) -> None | Exception:  # noqa: E501
        userID = int(userID)

        try:
            if userID not in self.application_details or self.application_details[userID] is None:  # noqa: E501
                self.application_details[userID] = {}

            self.application_details[userID][key] = value

            with open(APPLICATION_DETAILS, "w") as file:
                dump(self.application_details, file, indent=4)

            if self.debuggingMode:
                logger.debug("[SaveDetails] Application info:"
                             f" {bot.application_details}")

            return None
        except Exception as e:
            if self.debuggingMode:
                raise e
            return e

    async def DeleteUserDetails(self, userID: int) -> None | Exception:
        try:
            self.application_details[userID] = None
            with open(APPLICATION_DETAILS, "w") as file:
                dump(self.application_details, file, indent=4)

            if self.debuggingMode:
                logger.debug("[DeleteUserDetails] Application info:"
                             f" {bot.application_details}")

            return None
        except Exception as e:
            if self.debuggingMode:
                raise e
            return e


_intents = nextcord.Intents.default()
_intents.members = True
# Command prefix is necessary for some reason
bot = Bot(command_prefix="!", intents=_intents, debuggingMode=True)


@bot.event
async def on_ready() -> None:
    bot.db = await aiosqlite.connect("fissionbot.db")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS referrals ("
                         "referrer_id BIGINT, count INTEGER DEFAULT 0)")

    logger.info(f"Logged in as {bot.user.name} - {bot.user.id}")
    if path.exists(APPLICATION_DETAILS):
        with open(APPLICATION_DETAILS, "r") as f:
            bot.application_details = {int(k): v for k, v in load(f).items()}

    if bot.debuggingMode:
        logger.debug(f"Application info: {bot.application_details}")

    return await bot.change_presence(
        activity=nextcord.Activity(
            type=nextcord.ActivityType.watching,
            name="EXPERIMENTAL"))

# Manually load apply since it's in a subfolder
bot.load_extension("cogs.apply")
bot.load_extension("cogs.admin")

# Optionally auto-load others
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(getenv("DISCORD_TOKEN"))
