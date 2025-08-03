import nextcord


async def serverSettings(interaction: nextcord.Interaction):
    return interaction.response.send_message(
        embed=nextcord.Embed(
            title='No settings for you here',
            description='The only setting that will be here'
            ' in the future is the ability to modify CPU, RAM and Disk'
        ).add_field(
            name='Looking to create a server?',
            value='Use /create_server'
        ), ephemeral=True
    )
