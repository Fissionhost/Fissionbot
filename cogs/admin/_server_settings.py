import nextcord


async def serverSettings(interaction: nextcord.Interaction):
    options = [
        nextcord.SelectOption(
            label="Delete a server",
            value="Delete a user's server"
        ),
        nextcord.SelectOption(
            label="Manage sever",
            value="Modify a user's server"
        ),
    ]

    select = nextcord.ui.Select(
        placeholder="Choose your setting...",
        options=options,
        min_values=1,
        max_values=1,
    )

    async def select_callback(interaction: nextcord.Interaction):
        selected_value = select.values[0]
        await interaction.response.send_message(
            f"You selected: {selected_value}",
            ephemeral=True
        )

    select.callback = select_callback

    view = nextcord.ui.View()
    view.add_item(select)
    await interaction.response.send_message(
        "Choose your user setting...",
        view=view,
        ephemeral=True
    )
