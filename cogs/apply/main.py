from nextcord.ext import commands
from nextcord import (
	Interaction,
	SlashOption,
	SelectOption,
	TextInputStyle,
	Embed,
	Color,
	ui,
	Button,
	ButtonStyle,
	slash_command
)
from cogs import _pterodapi
from cogs._errors import HandleError
from config import ERROR_CHANNEL, APPLICATION_CHANNEL_ID


class Apply(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.api = _pterodapi.API(
			address="https://panel.fissionhost.org",
			application_token=(
				"ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp"
			), # Flake8's fault
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
					description="Python is a versatile, high-level programming "
								"language known for its readability and ease of "
								"use.",
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
				description="Your application is going through some pre-screens. Thank you for your patience!",
				color=Color.orange()
			).add_field(name="Stuck here?",value="Please tell a member of staff!"),
		ephemeral=True)

		print("[Debug]", (self.bot.application_details[interaction.user.id]))

		embed = Embed(
			title="Application Submitted",
			description="Your application has been submitted successfully!",
			color=Color.green()
		)
	
		idx_to_fieldname = {0:"Reasoning",1:"Where from",2:"Email"}
		idx_to_keyname = {0:"reasoning",1:"origination",2:"email"}
		for idx, item in enumerate(interaction.data["components"]):
			value = item["components"][0]["value"]
			embed.add_field(name=idx_to_fieldname[idx], value=value, inline=False)
			await self.bot.SaveDetails(
				interaction.user.id,
				idx_to_keyname[idx],
				value=value
			)

		if len(self.bot.application_details[interaction.user.id]) != 5:
			self.bot.application_details[interaction.user.id] = None
			return await msg.edit(embed=Embed(
				title="Application Details are malformed",
				description="I've reset your application. Try again!",
				color=Color.red()
			))
		
		servertype, serversubtype, reasoning, origination, email = self.bot.application_details[interaction.user.id].values()
		embed.add_field(name="Server Type",value=servertype)
		embed.add_field(name="Server Subtype",value=serversubtype)

		await msg.edit(embed=embed)

		embed = Embed(
			title="New application",
			color=Color.blue()
		)
			
		embed.add_field(name="Applicant",value=interaction.user.mention)
		embed.add_field(name="Server Type",value=servertype)
		embed.add_field(name="Server Subtype",value=serversubtype)
		embed.add_field(name="Reasoning",value=reasoning)
		embed.add_field(name="Origination",value=origination)
		embed.add_field(name="Email",value=email)

		APPLICATION_CHANNEL = self.bot.get_channel(APPLICATION_CHANNEL_ID)
		if not APPLICATION_CHANNEL: await self.bot.fetch_channel(APPLICATION_CHANNEL_ID)
		view = ui.View()
		accept_button = ui.Button(label="Accept", style=ButtonStyle.success)
		deny_button = ui.Button(label="Deny", style=ButtonStyle.danger)
		# accept_button.callback = accept_callback
		# deny_button.callback = deny_callback

		view.add_item(accept_button)
		view.add_item(deny_button)

		if APPLICATION_CHANNEL:
			msg = await APPLICATION_CHANNEL.send(embed=embed, view=view)
		else:
			print(f"[Error] Staff channel not found!")

		return


def setup(bot):
	bot.add_cog(Apply(bot))
