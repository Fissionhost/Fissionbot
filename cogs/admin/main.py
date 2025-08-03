from nextcord.ext import commands
from nextcord import (
    Interaction,
    SelectOption,
    Embed,
    Color,
    ui,
    SlashOption,
    slash_command
)
from config import ADMIN_IDS
from cogs.admin._user_settings import userSettings
from cogs.admin._misc_settings import miscSettings
from cogs.admin._server_settings import serverSettings
from cogs._pterodapi import API
from json import loads
from logging import getLogger


egg_to_id: dict[str, int] = {
    "VanillaMC": 4,
    "ForgeMC": 3,
    "PaperMC": 5,
    "FabricMC": 15,
    "SpongeMC": 21,
    "BungeecordMC": 1,
    "PocketmineMPMC": 19,
    "NukkitMC": 18,
    "Node.js Generic": 17,
    "Python": 16,
    "Rust": 30
}

api = API(
    address="https://fissionhost.dpdns.org",
    application_token="ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp",
    user_token="ptlc_1qcXqvxqhFdQyBDk4UvvF0sw6IM2TDTd5UTFFc6BHUO",
    debug=True,
)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = getLogger(__name__)

    @slash_command(name="admin", description="Show an admin panel")
    async def admin(self, interaction: Interaction):
        if interaction.user.id not in ADMIN_IDS:
            return await interaction.response.send_message(
                embed=Embed(
                    title="Insufficient Permissions",
                    description="You do not have permission to do this!",
                    color=Color.red(),
                ))

        class AdminDropdown(ui.Select):
            def __init__(self):
                options = [
                    SelectOption(label="Servers",
                                 description="Manage servers"),
                    SelectOption(label="Users",
                                 description="Manage users"),
                    SelectOption(label="Misc",
                                 description="Other settings that don't fit"
                                 " into a catagory"),
                ]
                super().__init__(placeholder="Choose an admin action...",
                                 min_values=1,
                                 max_values=1,
                                 options=options)

            async def callback(self, select_interaction: Interaction):
                selected = self.values[0]
                match selected:
                    case "Severs":
                        await serverSettings(select_interaction)
                    case "Users":
                        await userSettings(select_interaction)
                    case "Misc":
                        await miscSettings(select_interaction)
                    case _:
                        return

        class AdminDropdownView(ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(AdminDropdown())

        await interaction.response.send_message(
            embed=Embed(
                title="Admin Panel",
                description="Select an action from the dropdown below.",
                color=Color.blue(),
            ),
            view=AdminDropdownView(),
            ephemeral=True
        )

    @slash_command(
        name='create_server',
        description='Manually create a server'
    )
    async def admin_create_server(
        self,
        interaction: Interaction,
        egg: str = SlashOption(
            name="egg",
            description="Select a server type",
            choices=[
                "VanillaMC",
                "ForgeMC",
                "PaperMC",
                "FabricMC",
                "SpongeMC",
                "BungeecordMC",
                "PocketmineMPMC",
                "NukkitMC",
                "Node.js Generic",
                "Python",
                "Rust"
            ]
        ),
        user_id: int = SlashOption(
            name="user_id",
            description="ID of the user to assign the server to"
        )
    ):
        if interaction.user.id not in ADMIN_IDS:
            return await interaction.response.send_message(
                embed=Embed(
                    title="Insufficient Permissions",
                    description="You do not have permission to do this!",
                    color=Color.red(),
                ))

        original_embed = Embed(
            title="Creating server...",
            description='Please wait while the server is requested',
            color=Color.orange()
        )
        embed = original_embed.copy()
        embed.add_field(name='Status', value='Converting choice to egg id...')
        msg = await interaction.response.send_message(embed=embed)

        egg_id = egg_to_id[egg]

        embed = original_embed.copy()
        embed.add_field(name='Status', value='Sending request to api...')
        embed.add_field(name='Egg ID', value=egg_id)
        await msg.edit(embed=embed)

        response = loads(await api.Servers.create_server(
            egg=egg_id, user_id=user_id
        ))
        if 'attributes' in response:
            embed = original_embed.copy()
            embed.color = Color.green()
            embed.add_field(name='Status', value='Complete')
            embed.add_field(name='Egg ID', value=egg_id)
            await msg.edit(embed=embed)
        else:
            embed = original_embed.copy()
            embed.color = Color.red()
            embed.add_field(name='Status', value='Failed')
            embed.add_field(name='Egg ID', value=egg_id)
            await msg.edit(embed=embed)

            return self.logger.error(
                f"Failed to create server: {response}"
            )

        return


def setup(bot):
    admin = Admin(bot)
    bot.add_cog(admin)
