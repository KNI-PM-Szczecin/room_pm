import io
import re
import nextcord
from utilities import baseUtils
from nextcord.ext import commands

class BroadcastCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader):
        self.client = client
        self.config = config

    @nextcord.message_command(
        name="Przekaż",
    )
    async def forward(self,
        interaction: nextcord.Interaction,
        message: nextcord.Message,
    ):
        await interaction.response.defer(ephemeral=True)

        temp_forward_roles = [1481667679566958662, 1481667730410176644]

        all_members = [member async for member in interaction.guild.fetch_members(limit=None)]
        target_members = [
            member for member in all_members
            if any(role.id in temp_forward_roles for role in member.roles) and not member.bot
        ]

        if not target_members:
            await interaction.followup.send("Nie znaleziono użytkowników z wybranymi rolami.", ephemeral=True)
            return

        content = message.content
        clean_content = re.sub(r"<@&[0-9]+>\s*", "", message.content)
        if not content and not message.attachments:
            await interaction.response.send_message(
                "Ta wiadomość jest pusta (może to sam embed lub wiadomość systemowa?",
                ephemeral=True
            )
            return

        attachment_data = []
        for attachment in message.attachments:
            attachment_data.append({
                "bytes": await attachment.read(),
                "filename": attachment.filename
            })

        success_count = 0
        fail_count = 0

        for member in target_members:
            try:
                current_files = [
                    nextcord.File(io.BytesIO(data["bytes"]), filename=data["filename"])
                    for data in attachment_data
                ]

                await member.send(
                    content=f"Przesłana wiadomość autorstwa **{message.author.display_name}**\nZ **{interaction.guild.name}**:\n\n{clean_content}",
                    files=current_files
                )
                success_count += 1
            except nextcord.Forbidden:
                fail_count += 1
            except Exception as e:
                print(f"Błąd wysyłania do {member.name}: {e}")
                fail_count += 1

        await interaction.followup.send(
            f"Zakończono! Wysłano do: {success_count} osób. Nie udało się (zablokowane DM): {fail_count}.",
            ephemeral=True
        )