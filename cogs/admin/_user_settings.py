import nextcord
import secrets
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

class UserPasswordModal(Modal):
    def __init__(self, username: str):
        super().__init__("Enter the desired password", timeout=300)
        self.username = username
        self.newpassword = TextInput(
            label="Password",
            placeholder="eg. iLoveCelcus123!",
            min_length=5,
            max_length=100,
            required=True
        )
        
        self.add_item(self.newpassword)
    
    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        newpassword = str(self.newpassword.value)

        username_mopped = api.Users.mop(self.username)
        user_id = await api.Users.get_id(username_mopped)

        user_details = loads(await api.Users.get_details(username_mopped))
        attribs = user_details['data'][0]['attributes']
        email = attribs['email']
        firstname = attribs['first_name']
        lastname = attribs['last_name']

        await api.Users.update_user_password(
            user_id,
            email,
            api.Users.mop(self.username),
            firstname,
            lastname,
            newpassword
        )

        embed=nextcord.Embed(
            title='Account modified succesfully!',
            description='Below will be the new user details',
            color=nextcord.Color.green()
        )
        
        embed.add_field(name='Username', value=api.Users.mop(self.username))
        embed.add_field(name='New Password', value=newpassword)

        try:
            return await interaction.followup.send(
                embed=embed
            )
        except Exception as e:
            await interaction.followup.send("Username: {}, Password: {}".format(
                api.Users.mop(self.username),
                newpassword
            ))
            api.logger.error(e)

class UserInfoModal(Modal):
    def __init__(self, username: str):
        super().__init__("Enter your information", timeout=300)
        self.username = username
        self.email = TextInput(
            label="Email",
            placeholder="the.email@example.com",
            min_length=5,
            max_length=100,
            required=True
        )
        self.firstname = TextInput(
            label="First Name",
            placeholder="John",
            min_length=2,
            max_length=50,
            required=True
        )
        self.surname = TextInput(
            label="Surname",
            placeholder="Doe",
            min_length=2,
            max_length=50,
            required=True
        )
        
        self.add_item(self.email)
        self.add_item(self.firstname)
        self.add_item(self.surname)
    
    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Make the API call with the collected information
        # Get the values entered in the modal
        email = str(self.email.value)
        firstname = str(self.firstname.value)
        surname = str(self.surname.value)

        response = await api.Users.create_user(
            self.username,
            email,
            firstname,
            surname
        )

        username_mopped = api.Users.mop(self.username)
        user_id = await api.Users.get_id(username_mopped)
        
        if user_id is None:
            api.logger.error(f"Failed to create user: {self.username}")
            api.logger.error(response)
            return await interaction.followup.send(
                embed=nextcord.Embed(
                    title='Account Failed to Create',
                    description="The user's account has not been created!",
                    color=nextcord.Color.red()
                ), ephemeral=True
            )

        words = [
            "apple", "river", "cloud", "stone", "light", "star", "wolf", "tree", "moon", "fire",
            "ocean", "leaf", "wind", "sky", "mount", "echo", "frost", "dawn", "hawk", "rose"
        ]
        password = (
            secrets.choice(words).capitalize() +
            secrets.choice(words).capitalize() +
            secrets.choice(words).capitalize() +
            str(secrets.randbelow(90) + 10)  # 2 random digits
        )
        self.password = password

        await api.Users.update_user_password(
            user_id,
            email,
            api.Users.mop(self.username),
            firstname,
            surname,
            self.password
        )

        embed=nextcord.Embed(
            title='User account created!',
            description='Below will be the details generated',
            color=nextcord.Color.blue()
        )

        embed.add_field(name="User ID", value=user_id)
        embed.add_field(name="Email", value=email)
        embed.add_field(name="Username", value=api.Users.mop(self.username))
        embed.add_field(name="Firstname", value=firstname)
        embed.add_field(name="Surname", value=surname)
        embed.add_field(name="Password", value=self.password)
        
        try:
            return await interaction.followup.send(
                embed=embed
            )
        except Exception as e:
            api.logger.warning("The account details failed to send, so it must be sent here!")
            api.logger.warning("Username: {}, Password: {}".format(
                api.Users.mop(self.username),
                self.password
            ))
            await interaction.followup.send("Username: {}, Password: {}".format(
                api.Users.mop(self.username),
                self.password
            ))
            api.logger.error(str(e))

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
        self.manage_button = Button(label="Modify Password", style=nextcord.ButtonStyle.primary)
        self.create_button = Button(label="Create User", style=nextcord.ButtonStyle.success)
        
        # Add buttons to view
        self.add_item(self.delete_button)
        self.add_item(self.manage_button)
        self.add_item(self.create_button)
        
        # Disable buttons if user doesn't exist
        if user_id is None:
            self.delete_button.disabled = True
            self.manage_button.disabled = True
        else:
            self.create_button.disabled = True
        
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

        user_details_resp = await api.Users.get_details(username_mopped)

        if user_details_resp is not None:
            user_details = loads(user_details_resp)['data'][0]['attributes']
            embed.add_field(name="ID", value=user_details['id'])
            embed.add_field(name="Email", value=user_details['email'])
            embed.add_field(name="Firstname", value=user_details['first_name'])
            embed.add_field(name="Lastname", value=user_details['last_name'])
            embed.add_field(name="Created at", value=user_details['created_at'])

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
        
        # Send the modal to collect password
        modal = UserPasswordModal(self.username)
        return await interaction.response.send_modal(modal)

    async def on_create(self, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        
        # Send the modal to collect user information
        modal = UserInfoModal(self.username)
        return await interaction.response.send_modal(modal)

class DeleteConfirmationView(View):
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
            return await interaction.response.edit_message(
                embed=nextcord.Embed(
                    title="Error deleting user's servers",
                    description="Maybe the user has no servers?",
                    color=nextcord.Color.red()
                ), ephemeral=True
            )

        for server in servers['attributes']['relationships']['servers']['data']:
            server_id = server['attributes']['id']
            await api.Servers.delete_server(server_id)
            

        await api.Users.delete_user(self.user_id)
        user_id = await api.Users.get_id(api.Users.mop(self.username))
        
        if user_id is None:
            return await interaction.response.edit_message(
                embed=nextcord.Embed(
                    title="Account deleted",
                    description="The account was succesfully deleted!",
                    color=nextcord.Color.green()
                ), ephemeral=True
            )
        
        return await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Error deleting account",
                description="The account still remains!",
                color=nextcord.Color.red()
            ), ephemeral=True
        )

    @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.secondary)
    async def cancel_button(self, button: Button, interaction: nextcord.Interaction):
        if not await self.interaction_check(interaction):
            return
        await interaction.response.delete_message()

async def userSettings(interaction: nextcord.Interaction):
    await interaction.response.send_modal(UserSettingsModal())