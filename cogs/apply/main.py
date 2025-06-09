from nextcord.ext import commands
from nextcord import (
    Interaction,
    SlashOption,
    SelectOption,
    TextInputStyle,
    Embed,
    Color,
    slash_command,
    ui,
)
from cogs import _pterodapi
from cogs._errors import HandleError
from config import ERROR_CHANNEL


class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.application_details: dict[int, dict[str, str]] = {}
        self.api = _pterodapi.API(
            address="https://panel.fissionhost.org",
            application_token="ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp",
            user_token="ptlc_1qcXqvxqhFdQyBDk4UvvF0sw6IM2TDTd5UTFFc6BHUO",
            debug=True,
        )

    @slash_command(name="apply", description="Submit an application")
    async def apply(
        self,
        interaction: Interaction,
        type: str = SlashOption(
            name="type",
            description="The type of server you are requesting",
            required=True,
            choices=("Discord Bot", "Minecraft"),
        ),
    ):

        if e := await self.bot.SaveDetails(
            userID=interaction.user.id, key="nest", value=type
        ):
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            if not ErrorChannel:
                ErrorChannel = await self.bot.fetch_channel(ERROR_CHANNEL)
            return await HandleError(interaction, e, ErrorChannel)

        if type == "Minecraft":
            embed = Embed(
                title="Minecraft Server Application",
                description="Please select the type of server you want to apply for:",
                color=Color.blurple(),
            )

            serversubtype_select_options = [
                SelectOption(
                    label="Paper",
                    description="A Minecraft game server based on Spigot.",
                ),
                SelectOption(
                    label="Bungeecord",
                    description="BungeeCord is a sophisticated proxy for managing multiple servers.",
                ),
                SelectOption(
                    label="Forge",
                    description="Forge is a popular mod loader for Minecraft that allows users to add mods.",
                ),
                SelectOption(
                    label="Fabric",
                    description="Fabric is primarily designed for running modded clients but also servers.",
                ),
                SelectOption(
                    label="Vanilla",
                    description="Plain vanilla server software, if you're nostalgic.",
                ),
                SelectOption(
                    label="Nukkit",
                    description="Nukkit is nuclear-powered server software for Minecraft Bedrock Edition.",
                ),
                SelectOption(
                    label="Pocketmine",
                    description="PocketMine-MP is customisable server software for Minecraft: Bedrock Edition written in PHP.",
                ),
            ]

        elif type == "Discord Bot":
            embed = Embed(
                title="Discord Bot Application",
                description="Please select the type of server you want to apply for",
                color=Color.blurple(),
            )
        serversubtype_select_options = [
            SelectOption(
                label="Python",
                description="Python is a versatile, high-level programming language known for its readability and ease of use.",
            ),
            SelectOption(
                label="Javascript",
                description="JavaScript is a versatile, lightweight programming language.",
            ),
        ]

        serversubtype_select = ui.Select(
            placeholder="Choose a server type...", options=serversubtype_select_options
        )
        serversubtype_select.callback = self.ServerTypeCallback

        view = ui.View()
        view.add_item(serversubtype_select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def ServerTypeCallback(self, interaction: Interaction) -> None:
        await self.bot.SaveDetails(
            userID=interaction.user.id,
            key="subtype",
            value=interaction.data["values"][0],
        )

        modal = ui.Modal(title="Server Application", timeout=None)
        modal.add_item(
            ui.TextInput(
                label="Why do you want a server?",
                placeholder="Explain your motivation...",
                required=True,
                style=TextInputStyle.paragraph,
            )
        )
        modal.add_item(
            ui.TextInput(
                label="How did you find us?",
                placeholder="Describe your connection...",
                required=True,
                style=TextInputStyle.paragraph,
            )
        )
        modal.add_item(
            ui.TextInput(label="Email", placeholder="*****@*******.com", required=True)
        )
        modal.callback = None  # Next stage
        await interaction.response.send_modal(modal)


def setup(bot):
    bot.add_cog(Apply(bot))
