import cogs._pterodapi as _pterodapi
from nextcord.ext import commands
from nextcord import Interaction, Embed, Color, slash_command
from json import loads

# flake8: noqa: E501

class ServerInfo(commands.Cog):
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

    @slash_command(
        name="server_info",
        description="Get details about your server"
    )
    async def server_info(self, interaction: Interaction):
        msg = await interaction.response.send_message(
            embed=Embed(
                title="Gathering server information",
                description="Please wait while we send a request to the API to gather your server details",
                color=Color.orange()
            ), ephemeral=True
        )

        username = self.api.Users.mop(interaction.user.name)
        user_data = await self.api.Users.get_details(username)
        user_id_data = loads(user_data)["data"]

        if user_id_data == []:
            self.bot.logger.warning(f"User failed to fetch server info: {user_data} ")
            return await msg.edit(embed=Embed(
                title="Error",
                description="User not found!"
                            " Are you sure you have an account?",
                color=Color.red()))

        user_id = user_id_data[0]["attributes"]["id"]
        servers_data = await self.api.Users.get_servers(user_id)
        servers = loads(servers_data)["attributes"]["relationships"]["servers"]["data"]

        if len(servers) == 0:
            return await msg.edit(embed=Embed(
                title="We couldn't fufill this request",
                description="You don't have a server!",
                color=Color.red()
            ))

        for server in servers:
            attribs = server["attributes"]
            embed = Embed(
                title="Server Details",
                color=Color.blue())

            embed.add_field(name="Server Name", value=attribs.get("name") or "None", inline=True)
            embed.add_field(name="Description", value=attribs.get("description") or "None", inline=True)
            embed.add_field(name="Status", value=attribs.get("status") or "None", inline=True)
            embed.add_field(name="Suspended", value=attribs.get("suspended") or "False", inline=True)
            
            memory = attribs.get("limits", {}).get("memory")
            if memory is not None and int(memory) < 1024:
                memory_gb = f"{int(memory)} MB"
            elif memory is not None:
                memory_gb = f"{int(memory) / 1024:.2f} GB"
            else:
                memory_gb = "None"
            embed.add_field(name="Memory", value=memory_gb, inline=True)

            swap = attribs.get("limits", {}).get("swap")
            if swap is not None:
                swap_gb = f"{int(swap) / 1024:.2f} GB"
            else:
                swap_gb = "None"
            embed.add_field(name="Swap", value=swap_gb, inline=True)

            disk = attribs.get("limits", {}).get("disk")
            if disk is not None:
                disk_gb = f"{int(disk) / 1024:.2f} GB"
            else:
                disk_gb = "None"
            embed.add_field(name="Disk", value=disk_gb, inline=True)

            embed.add_field(name="IO", value=attribs.get("limits", {}).get("io") or "None", inline=True)
            cpu = attribs.get("limits", {}).get("cpu")
            cpu_str = f"{cpu}%" if cpu is not None else "None"
            embed.add_field(name="CPU", value=cpu_str, inline=True)
            embed.add_field(name="Databases", value=attribs.get("feature_limits", {}).get("databases") or "None", inline=True)
            embed.add_field(name="Allocations", value=attribs.get("feature_limits", {}).get("allocations") or "None", inline=True)
            embed.add_field(name="Backups", value=attribs.get("feature_limits", {}).get("backups") or "None", inline=True)
            embed.add_field(name="Server Type", value=_pterodapi.id_eggs.get(attribs.get("egg")) or "None", inline=True)

            await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(ServerInfo(bot))
