from nextcord.ext import commands
from nextcord import (
    Interaction,
    SlashOption,
    SelectOption,
    TextInputStyle,
    Embed,
    Color,
    ui,
    InteractionType,
    ButtonStyle,
    slash_command
)
from cogs import _pterodapi
from cogs._errors import HandleError
from config import (
    ERROR_CHANNEL_ID,
    APPLICATION_CHANNEL_ID,
    ADMIN_IDS,
    APPLICATION_SUCCESS_CHANNEL_ID,
)
from json import loads
from string import digits, ascii_letters
from secrets import choice as secret_choice


class Apply(commands.Cog):
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
        if int(interaction.user.id) in self.bot.application_details:
            await self.bot.DeleteUserDetails(
                userID=int(interaction.user.id)
            )

        if e := await self.bot.SaveDetails(
            userID=int(interaction.user.id), key="nest", value=type
        ):
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL_ID)
            if not ErrorChannel:
                ErrorChannel = await self.bot.fetch_channel(ERROR_CHANNEL_ID)
            return await HandleError(interaction, e, ErrorChannel)

        if type == "Minecraft":
            embed = Embed(
                title="Minecraft Server Application",
                description="Please select the type of server you want to"
                            " apply for:",
                color=Color.blurple(),
            )

            serversubtype_select_options = [
                SelectOption(
                    label="Paper",
                    description="A Minecraft game server based on Spigot.",
                ),
                SelectOption(
                    label="Bungeecord",
                    description="BungeeCord is a sophisticated proxy for "
                    "managing multiple servers.",
                ),
                SelectOption(
                    label="Forge",
                    description="Forge is a popular mod loader for Minecraft "
                    "that allows users to add mods.",
                ),
                SelectOption(
                    label="Fabric",
                    description="Fabric is primarily designed for running "
                    "modded clients but also servers.",
                ),
                SelectOption(
                    label="Vanilla",
                    description="Plain vanilla server software, if you're "
                    "nostalgic.",
                ),
                SelectOption(
                    label="Nukkit",
                    description="Nukkit is nuclear-powered server software for"
                    " Minecraft Bedrock Edition.",
                ),
                SelectOption(
                    label="Pocketmine",
                    description="PocketMine-MP is customisable server software"
                    " for Minecraft: Bedrock Edition written in PHP.",
                ),
            ]

        elif type == "Discord Bot":
            embed = Embed(
                title="Discord Bot Application",
                description="Please select the type of server you want to "
                            "apply for",
                color=Color.blurple(),
            )
            serversubtype_select_options = [
                SelectOption(
                    label="Python",
                    description="Python is a versatile, high-level "
                                "programming "
                                "language known for its readability and ease "
                                "of use.",
                ),
                SelectOption(
                    label="Javascript",
                    description="JavaScript is a versatile, lightweight "
                                "programming language.",
                ),
            ]

        serversubtype_select = ui.Select(
            placeholder="Choose a server type...",
            options=serversubtype_select_options
        )
        serversubtype_select.callback = self.ServerTypeCallback

        view = ui.View()
        view.add_item(serversubtype_select)
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)

    async def ServerTypeCallback(self, interaction: Interaction) -> None:
        await self.bot.SaveDetails(
            userID=int(interaction.user.id),
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
            ui.TextInput(
                label="Email",
                placeholder="*****@*******.com",
                required=True,
            )
        )
        modal.callback = self.ApplicationModalCallback  # Next stage
        await interaction.response.send_modal(modal)

    async def ApplicationModalCallback(self, interaction: Interaction):
        msg = await interaction.response.send_message(
            embed=Embed(
                title="Submitting Application",
                description="Your application is going through some "
                            "pre-screens. Thank you for your patience!",
                color=Color.orange()
            ).add_field(name="Stuck here?",
                        value="Please tell a member of staff!"),
            ephemeral=True)

        embed = Embed(
            title="Application Submitted",
            description="Your application has been submitted successfully!",
            color=Color.green()
        )

        idx_to_fieldname = {0: "Reasoning", 1: "Where from", 2: "Email"}
        idx_to_keyname = {0: "reasoning", 1: "origination", 2: "email"}
        for idx, item in enumerate(interaction.data["components"]):
            value = item["components"][0]["value"]
            embed.add_field(
                name=idx_to_fieldname[idx],
                value=value,
                inline=False)
            await self.bot.SaveDetails(
                int(interaction.user.id),
                idx_to_keyname[idx],
                value=value
            )

        if len(self.bot.application_details[int(interaction.user.id)]) != 5:
            self.bot.application_details[int(interaction.user.id)] = None
            return await msg.edit(embed=Embed(
                title="Application Details are malformed",
                description="I've reset your application. Try again!",
                color=Color.red()
            ))

        (servertype, serversubtype, reasoning, origination, email
         ) = self.bot.application_details[int(interaction.user.id)].values()

        embed.add_field(name="Server Type", value=servertype)
        embed.add_field(name="Server Subtype", value=serversubtype)

        await msg.edit(embed=embed)

        embed = Embed(
            title="New application",
            color=Color.blue()
        )

        embed.add_field(name="Applicant", value=interaction.user.mention)
        embed.add_field(name="Server Type", value=servertype)
        embed.add_field(name="Server Subtype", value=serversubtype)
        embed.add_field(name="Reasoning", value=reasoning)
        embed.add_field(name="Origination", value=origination)
        embed.add_field(name="Email", value=email)

        APPLICATION_CHANNEL = self.bot.get_channel(APPLICATION_CHANNEL_ID)
        if not APPLICATION_CHANNEL:
            await self.bot.fetch_channel(APPLICATION_CHANNEL_ID)
        view = ui.View()
        accept_button = ui.Button(
            label="Accept",
            style=ButtonStyle.success,
            custom_id="accept_btn")
        deny_button = ui.Button(
            label="Deny",
            style=ButtonStyle.danger,
            custom_id="deny_btn")
        # accept_button.callback = accept_callback
        # deny_button.callback = deny_callback

        view.add_item(accept_button)
        view.add_item(deny_button)

        if APPLICATION_CHANNEL:
            msg = await APPLICATION_CHANNEL.send(embed=embed, view=view)
        else:
            self.bot.logger.warning("[Error] Staff channel not found!")

        return

    async def AccountCreationCallback(self, interaction: Interaction):
        # Sending a message to prevent timeouts

        embed = (
            Embed(
                title="Creating account",
                description="Please wait while we sort some things out. Your "
                "server and account will be ready shortly!",
                color=Color.orange()).add_field(
                name="Progress",
                value="Creating account...")).add_field(
            name="Stuck here?",
            value="Please tell a member of staff!")

        msg = await interaction.response.send_message(
            embed=embed
        )

        # Actual registration of account
        idx_to_key = {0: "name", 1: "surname", 2: "referrer"}
        for idx, item in enumerate(interaction.data["components"]):
            value = item["components"][0]["value"]
            await self.bot.SaveDetails(int(interaction.user.id),
                                       idx_to_key[idx],
                                       value)

        username = await self.api.Users.mop(interaction.user.name)
        UserDetails = self.bot.application_details[int(interaction.user.id)]
        account_response = loads(await self.api.Users.create_user(
            username=username,
            email=UserDetails["email"],
            firstname=UserDetails["name"],
            surname=UserDetails["surname"]
        ))

        # Checkng for creation of account
        if "attributes" not in account_response:
            ERROR_CHANNEL = self.bot.get_channel(ERROR_CHANNEL_ID)
            if not ERROR_CHANNEL:
                await self.bot.fetch_channel(ERROR_CHANNEL_ID)
            await ERROR_CHANNEL.send(embed=Embed(
                title="An error occured while creating an account",
                description=str(account_response),
                color=Color.red()
            ).add_field(name="User ID", value=int(interaction.user.id)))

            return await msg.edit(embed=Embed(
                title="An unexpected error occured!",
                description="Do you already have an account?",
                color=Color.red())
            )

        embed = (
            Embed(
                title="Creating account",
                description="Please wait while we sort some things out. Your "
                "server and account will be ready shortly!",
                color=Color.orange()).add_field(
                name="Progress",
                value="Creating server...")).add_field(
            name="Stuck here?",
            value="Please tell a member of staff!")
        await msg.edit(embed=embed)

        # Creating the server for the account
        server_creation_response = loads(await self.api.Servers.create_server(
            egg=[UserDetails["nest"], UserDetails["subtype"]],
            user_id=account_response["attributes"]["id"]))

        # Error checking
        if "errors" in server_creation_response:
            ERROR_CHANNEL = self.bot.get_channel(ERROR_CHANNEL_ID)
            if not ERROR_CHANNEL:
                await self.bot.fetch_channel(ERROR_CHANNEL_ID)
            await ERROR_CHANNEL.send(embed=Embed(
                title="An error occured while creating a server",
                description=str(server_creation_response),
                color=Color.red()
            ).add_field(name="User ID", value=int(interaction.user.id)))

            embed = Embed(
                title="Error",
                description="There was an error creating your server! Staff "
                "will be notified",
                color=Color.red())
            return await msg.edit(embed=embed)

        # Generate a random password
        pwd = ''.join(secret_choice(ascii_letters + digits) for _ in range(12))
        await self.api.Users.update_user_password(
            id=account_response["attributes"]["id"],
            email=UserDetails["email"],
            username=username,
            first_name=UserDetails["name"],
            last_name=UserDetails["surname"],
            password=pwd
        )

        view = ui.View()
        view.add_item(
            ui.Button(
                label="Panel",
                url="https://panel.fissionhost.org"))

        await msg.edit(embed=(Embed(
            title="Success",
            description="Press the button below to arrive at our panel,"
            " where you can enter your username and password to gain "
            "access to your own server panel.",
            color=Color.green()
        ).add_field(name="Username", value=username)
        ).add_field(name="Password", value=f"||{pwd}||")
        )

        APPLICATION_SUCCESS_CHANNEL = self.bot.get_channel(
            APPLICATION_SUCCESS_CHANNEL_ID
        )

        embed = Embed(
            title="Server created!",
            description=f"<@{int(interaction.user.id)}>"
                        " successfully made a server",
            color=Color.green()
        )
        embed.add_field(
            name="Account ID",
            value=account_response["attributes"]["id"])
        await APPLICATION_SUCCESS_CHANNEL.send(embed=embed)

        try:
            await self.HandleReferral(interaction, UserDetails["referrer"])
        except Exception as e:
            await interaction.followup.send(embed=Embed(
                title="Note",
                description="Referrals through the bot "
                            "currently aren't working.",
                color=Color.orange()
            ).add_field(
                name="How do they claim invite rewards?",
                value="Ask them to create a ticket"
            ))

            return self.bot.logger.warning(
                f"Expected Exception in Referral: {e}"
            )

    async def HandleReferral(self, interaction: Interaction, referrer_name):
        GUILD = self.bot.get_guild(981206488540389386)
        if not GUILD:
            referrer = await self.bot.fetch_guild(981206488540389386).get_member_named(  # noqa: E501
                referrer_name)
        else:
            referrer = GUILD.get_member_named(referrer_name)  # noqa: E501

        cursor = await self.bot.db.execute("SELECT COUNT FROM referrals WHERE "
                                           "referrer_id = ?", (referrer.id,))
        data = await cursor.fetchone()
        if data is None:
            await self.bot.db.execute(
                "INSERT INTO referrals VALUES (?, ?)",
                (referrer.id, 1))

            return await interaction.followup.send(embed=Embed(
                title="Referral Successful",
                description="Your referral has been successful! "
                "They have been rewarded with additional resources "
                "on their server if they meet the requirements.",
                color=Color.green()
            ).add_field(name="Referrer", value=f"{referrer.name}",
                        inline=False))
        else:
            await self.bot.db.execute(
                "UPDATE referrals SET COUNT = ? WHERE referrer_id = ?",
                (data[0] + 1, referrer.id))

        await self.bot.db.commit()

        count = data[0] + 1

        pterodactyl_id = await self.api.Users.get_id(await self.api.Users.mop(
            referrer.name))
        if pterodactyl_id is None:
            return self.bot.logger.warning(
                f"Could not find Pterodactyl ID for user {referrer.name}.")

        servers_data = loads(await self.api.Users.get_servers(pterodactyl_id))
        servers_relationships = servers_data["attributes"]["relationships"]
        servers = servers_relationships["servers"]["data"]
        server = servers[0] if servers else None
        if server is None:
            return self.bot.logger.warning("No servers found for user "
                                           f"{referrer.name}.")

        server_attribs = server["attributes"]

        payload = {
            "allocation": server_attribs["allocation"],
            "memory": server_attribs["limits"]["memory"],
            "swap": server_attribs["limits"]["swap"],
            "disk": server_attribs["limits"]["disk"],
            "io": server_attribs["limits"]["io"],
            "cpu": server_attribs["limits"]["cpu"],
            "threads": None if server_attribs["limits"]["memory"] == "null"
            else server_attribs["limits"]["memory"],
            "feature_limits": server_attribs["feature_limits"],
        }

        reward: list[int, int, int] = await self.invite_rewards(
            invites=count,
            egg=server_attribs["egg"]
        )
        payload["memory"] += reward[0]
        payload["cpu"] += reward[1]
        payload["disk"] += reward[2]

        if reward != [0, 0, 0]:
            await self.api.Servers.edit_server_build(server_attribs["id"],
                                                     payload)
        else:
            self.bot.logger.info(
                f"No rewards to apply for this referral. {referrer.name} is at"
                " invites: {count}")

        if reward != [0, 0, 0]:
            embed = Embed(
                title="Referral Successful",
                description="You have successfully been referred by"
                            f" {interaction.user.name}!"
                "You have been rewarded with additional resources on your "
                "server.",
                color=Color.green())

            embed.add_field(name="Memory", value=f"{reward[0]}MB")
            embed.add_field(name="CPU", value=f"{reward[1]}%")
            embed.add_field(name="Disk", value=f"{reward[2]}MB")
            await referrer.send(embed=embed)

            embed.description = f"{interaction.user.name} referred "
            f"{referrer.name}"
            await APPLICATION_SUCCESS_CHANNEL_ID.send(embed=embed)

    async def AccountCreationModal(self, interaction: Interaction):
        modal = ui.Modal(
            title="Account Details",
            timeout=None
        )
        modal.add_item(ui.TextInput(
            label="First Name",
            placeholder="Example: John",
            required=True
        ))
        modal.add_item(ui.TextInput(
            label="Surname",
            placeholder="Example: Doe",
            required=True,
        ))
        modal.add_item(ui.TextInput(
            label="Who referred you?",
            placeholder=f"eg. {interaction.user.name}",
            required=False
        ))
        modal.callback = self.AccountCreationCallback
        return await interaction.response.send_modal(modal)

    async def accept_callback(self, interaction: Interaction):
        if int(interaction.user.id) not in ADMIN_IDS:
            return await interaction.response.send_message(
                "Only admins can do this!"
            )

        for field in interaction.message.embeds[0].fields:  # Embed
            if field.name == "Applicant":
                applicant = field.value
                break

        user = await self.bot.fetch_user(str(applicant).replace("<", "")
                                         .replace("@", "")
                                         .replace(">", ""))

        create_server_button = ui.Button(
            label="Create Server",
            style=ButtonStyle.success,
            custom_id="create_server")

        view = ui.View()
        view.add_item(create_server_button)
        create_server_button.callback = None

        await user.send(embed=Embed(
            title="Your application was accepted!",
            description="Please press the button below to create your "
            "server and show credentials.",
            color=Color.green()
        ).set_footer(text="From Fissionhost"), view=view)

        # Changing staff embed
        embed = interaction.message.embeds[0]
        embed.title = "Application Accepted"
        embed.color = Color.green()
        return await interaction.message.edit(embed=embed, view=None)

    async def deny_callback(self, interaction: Interaction):
        if int(interaction.user.id) not in ADMIN_IDS:
            return await interaction.response.send_message(
                "Only admins can do this!"
            )

        msg = interaction.message
        applicant = None
        for field in msg.embeds[0].fields:
            if field.name == "Applicant":
                applicant = field.value
                break

        user = await self.bot.fetch_user(
            str(applicant).replace("<", "").replace("@", "").replace(">", "")
        )

        await user.send(embed=Embed(
            title="Your application was denied!",
            description="Unfortunately your application had faults "
            "we couldn't ignore. Sorry about this!",
            color=Color.red()
        ).set_footer(
            text="If you think this is a mistake, please contact us!"
        ))

        embed = msg.embeds[0]
        embed.title = "Application Denied"
        embed.color = Color.red()
        return await msg.edit(embed=embed, view=None)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        if interaction.type == InteractionType.component:
            if interaction.data.get("custom_id") == "accept_btn":
                return await self.accept_callback(interaction)
            elif interaction.data.get("custom_id") == "deny_btn":
                return await self.deny_callback(interaction)
            elif interaction.data.get("custom_id") == "create_server":
                await self.AccountCreationModal(interaction)

        pass


def setup(bot):
    apply = Apply(bot)
    bot.add_cog(apply)
