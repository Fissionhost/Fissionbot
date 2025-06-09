from config import DEVELOPER_ID
from nextcord import Embed, Interaction, Color
from colorama import Fore


async def HandleError(interaction: Interaction, error, ErrorChannel):
    print(f"{Fore.RED}[Critical Error] {error}{Fore.RESET}")
    if interaction: 
        await interaction.response.send_message(embed=Embed(
        title="An error occured",
        description="Unfortunately an error occured and your application has been stopped. Staff have been notified!",
        color=Color.red()
    ), ephemeral=True)
    return await ErrorChannel.send(f"<@{DEVELOPER_ID}>", embed=Embed(
        title="Critical Error",
        description=str(error),
        color=Color.red()
    ))
    