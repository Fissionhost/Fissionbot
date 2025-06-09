from nextcord import Interaction, TextInputStyle, ui

async def ServerTypeCallback(interaction: Interaction) -> None:
	application_details[interaction.user.id].append(interaction.data["values"][0])
	
	modal = nextcord.ui.Modal(
		title="Server Application",
		timeout=None
	)
	modal.add_item(ui.TextInput(
		label="Why do you want a server?",
		placeholder="Explain your motivation...",
		required=True,
		style=TextInputStyle.paragraph
	))
	modal.add_item(ui.TextInput(
		label="How did you find us?",
		placeholder="Describe your connection...",
		required=True,
		style=TextInputStyle.paragraph
	))
	modal.add_item(ui.TextInput(
		label="Email",
		placeholder="*****@*******.com",
		required=True
	))
	modal.callback = None # Next stage
	await interaction.response.send_modal(modal)