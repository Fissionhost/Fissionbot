from nextcord.ext import commands
from nextcord import (
    Interaction,
    SelectOption,
    Embed,
    Color,
    ui,
    slash_command
)
from config import ADMIN_IDS
from cogs.admin._user_settings import userSettings
from cogs.admin._misc_settings import miscSettings
from cogs.admin._server_settings import serverSettings


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    async def server_details(interaction: Interaction):
        pass


def setup(bot):
    admin = Admin(bot)
    bot.add_cog(admin)
