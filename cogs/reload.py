from nextcord.ext import commands
from nextcord import Interaction, SlashOption, Embed, Color, slash_command
from config import ADMIN_IDS


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="reload", description="Reload a command")
    async def reload(
        self,
        interaction: Interaction,
        extension: str = SlashOption(
            name="extension",
            description="Choose a command to reload",
            required=True,
            choices=("cogs.apply", "cogs.reload", "cogs.admin", "cogs.server_info"),  # noqa: E501
        ),
    ):
        if interaction.user.id not in ADMIN_IDS:
            self.bot.logger.error(
                "Extension [{extension}] wasn't reloaded because "
                f"[{interaction.user.name}] didn't have sufficient permission"
            )
            return await interaction.response.send_message(
                embed=Embed(
                    title="Insufficient Permissions",
                    description="You do not have permission to do this!",
                    color=Color.red(),
                )
            )

        try:
            self.bot.unload_extension(extension)
            self.bot.load_extension(extension)
            self.bot.logger.warning(f"Extension [{extension}] was reloaded")

            return await interaction.response.send_message(
                f"Extension `{extension}` has been reloaded successfully.",
                ephemeral=True,
            )
        except Exception as e:
            self.bot.logger.warning(
                f"Extension [{extension}] failed to reloaded: {e}"
            )
            return await interaction.response.send_message(
                f"Failed to reload extension `{extension}`: {e}",
                ephemeral=True
            )


def setup(bot):
    bot.add_cog(Reload(bot))
