import nextcord
from nextcord.ext import commands
import os
import logging
import colorlog
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
bot = Bot(command_prefix="!", intents=intents)
bot.debuggingMode = True

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


# Manually load apply since it's in a subfolder
bot.load_extension("cogs.apply")

# Optionally auto-load others
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.slash_command()
async def restartcommand(ctx, extension: str):
    """Restart a specific command by reloading its extension."""
    try:
        bot.unload_extension(extension)
        bot.load_extension(extension)
        await ctx.send(
            f"Extension `{extension}` has been restarted successfully."
        )
    except Exception as e:
        await ctx.send(
            f"Failed to restart extension `{extension}`: {e}"
        )


bot.run(getenv("DISCORD_TOKEN"))
