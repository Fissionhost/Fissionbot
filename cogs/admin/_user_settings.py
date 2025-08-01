import nextcord
from nextcord.ui import Modal, TextInput, Button, View
from cogs._pterodapi import API
from json import loads

# flake8: noqa: E501

api = API(
    address="https://fissionhost.dpdns.org",
    application_token="ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp",
    user_token="ptlc_1qcXqvxqhFdQyBDk4UvvF0sw6IM2TDTd5UTFFc6BHUO",
    debug=True,
)

class UserSettingsModal(Modal):
    def __init__(self):
        super().__init__(title="Enter Username")
        self.username_input = TextInput(
            label="Username",
            placeholder="Enter the username to manage...",
            required=True,
            min_length=1
        )
        self.add_item(self.username_input)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await UserSettingsView.show_for_username(interaction, self.username_input.value)

class UserSettingsView(View):
    def __init__(self, username: str, user_id: str | None, interaction_user: nextcord.User):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.interaction_user = interaction_user
        
        # Initialize buttons
        self.delete_button = Button(label="Delete User", style=nextcord.ButtonStyle.danger)
        self.manage_button = Button(label="Modify User", style=nextcord.ButtonStyle.primary)
        self.create_button = Button(label="Create User", style=nextcord.ButtonStyle.success)
        
        # Add buttons to view
        self.add_item(self.delete_button)
        self.add_item(self.manage_button)
        
        # Disable buttons if user doesn't exist
        if user_id is None:
            self.delete_button.disabled = True
            self.manage_button.disabled = True
            self.add_item(self.create_button)
        
        # Set up callbacks
        self.delete_button.callback = self.on_delete
        self.manage_button.callback = self.on_manage
        if user_id is None:
            self.create_button.callback = self.on_create

    @classmethod
    async def show_for_username(cls, interaction: nextcord.Interaction, username: str):
        username_mopped = api.Users.mop(username)
        user_id = await api.Users.get_id(username_mopped)
        
        embed = nextcord.Embed(
            title=f"User Settings for {username}",
            description="Select an action to perform:",
            color=nextcord.Color.blue()
        )
        
        view = cls(username, user_id, interaction.user)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user == self.interaction_user

    async def on_delete(self, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        
        confirm_view = DeleteConfirmationView(
            username=self.username,
            user_id=self.user_id,
            interaction_user=self.interaction_user
        )
        
        await interaction.response.send_message(
            f"Are you sure you want to delete {self.username}? This action cannot be undone.",
            view=confirm_view,
            ephemeral=True
        )

    async def on_manage(self, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        
        await interaction.response.send_message(
            f"Managing user: {self.username}",
            ephemeral=True
        )

    async def on_create(self, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        
        await interaction.response.send_message(
            f"Creating user: {self.username}",
            ephemeral=True
        )

class  DeleteConfirmationView(View):
    def __init__(self, username: str, user_id: str | None, interaction_user: nextcord.User):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.interaction_user = interaction_user

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user == self.interaction_user

    @nextcord.ui.button(label="Yes", style=nextcord.ButtonStyle.danger)
    async def confirm_button(self, button: Button, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        
        servers = loads(await api.Users.get_servers(self.user_id))
        if 'attributes' not in servers:
            await interaction.response.edit_message(
                content=f"The user has no servers!",
                view=None
        )

        for server in servers['attributes']['relationships']['servers']['data']:
            server_id = server['attributes']['id']
            response = await api.Servers.delete_server(server_id)
            

        response = await api.Users.delete_user(self.user_id)
        
        await interaction.response.edit_message(
            content=f"User {self.username} deleted.",
            view=None
        )

    @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.secondary)
    async def cancel_button(self, button: Button, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        await interaction.response.delete_message()

async def userSettings(interaction: nextcord.Interaction):
    await interaction.response.send_modal(UserSettingsModal())