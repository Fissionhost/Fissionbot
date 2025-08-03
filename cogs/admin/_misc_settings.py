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

async def miscSettings(interaction: nextcord.Interaction):
    return interaction.response.send_message(
        embed=nextcord.Embed(
            title='No settings for you here',
            description='Please suggest some misc settings!'
        ).add_field(
            name='Looking to create a server?',
            value='Use /create_server'
        ), ephemeral=True
    )
