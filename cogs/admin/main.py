from nextcord.ext import commands
from nextcord import (
    Interaction,
    SelectOption,
    Embed,
    Color,
    ui,
    slash_command
)
from cogs import _pterodapi
from config import ADMIN_IDS


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = _pterodapi.API(
            address="https://panel.fissionhost.org",
            application_token=(
                "ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp"
            ),  # Flake8's fault
            user_token="ptlc_1qcXqvxqhFdQyBDk4UvvF0sw6IM2TDTd5UTFFc6BHUO",
            debug=True,
        )

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
                    SelectOption(label="Server Details",
                                 description="Get details for a server"),
                    SelectOption(label="😊",
                                 description="😊"),
                    SelectOption(label="😁",
                                 description="😁"),
                ]
                super().__init__(placeholder="Choose an admin action...",
                                 min_values=1,
                                 max_values=1,
                                 options=options)

            async def callback(self, select_interaction: Interaction):
                selected = self.values[0]
                if selected == "Restart Server":
                    await select_interaction.response.send_message(
                        "Restarting server...", ephemeral=True)
                elif selected == "Stop Server":
                    await select_interaction.response.send_message(
                        "Stopping server...", ephemeral=True)
                elif selected == "Get Server Status":
                    await select_interaction.response.send_message(
                        "Fetching server status...", ephemeral=True)
                else:
                    await select_interaction.response.send_message(
                        "Work in progress! 😁", ephemeral=True)

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
