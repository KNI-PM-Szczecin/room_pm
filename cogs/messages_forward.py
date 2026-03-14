import io
import re
import nextcord
from utilities import baseUtils, dcDatabase
from nextcord.ext import commands, application_checks

class MessagesForwardCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader, database: dcDatabase.DB):
        self.client = client
        self.config = config
        self.database = database

    @nextcord.message_command(
        name="Przekaż"
    )
    @application_checks.has_permissions(administrator=True)
    async def forward(self,
        interaction: nextcord.Interaction,
        message: nextcord.Message,
    ):
        await interaction.response.defer(ephemeral=True)

        forward_role = self.database.get_forward_roles(guild_id=interaction.guild.id)
        active_ids = baseUtils.ListCommon([forward_role, [role.id for role in message.role_mentions]])
        all_members = [member async for member in interaction.guild.fetch_members(limit=None)]

        target_members = [
            member for member in all_members
            if any(role.id in active_ids for role in member.roles) and not member.bot
        ]
        mentioned_roles = [role.name for role in message.role_mentions if role.id in active_ids]

        if not target_members:
            await interaction.followup.send("Nie znaleziono użytkowników z wspomnianymi rolami.", ephemeral=True)
            return

        content = message.content
        clean_content = re.sub(r"<@&[0-9]+>\s*", "", message.content)

        if not content and not message.attachments:
            await interaction.followup.send(
                "Ta wiadomość jest pusta (może to embed lub wiadomość systemowa?)",
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

                content = (
                    f"Przesłana wiadomość autorstwa **{message.author.display_name}**\n"
                    f"Z **{interaction.guild.name}**\n\n"
                    f"{clean_content}\n\n"
                    f"_Otrzymujesz tę wiadomość ponieważ została przekazana przez administratora,_\n"
                    f"_oraz posiadasz jedną z tych ról: {', '.join(mentioned_roles)}_"
                )

                await member.send(
                    content=content,
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

    @nextcord.slash_command(
        name="dodaj_do_przekazania",
        description="Dodaje rolę do listy odbiorców przekazywanych wiadomości"
    )
    @application_checks.has_permissions(administrator=True)
    @application_checks.guild_only()
    async def add_to_forward(self,
         interaction: nextcord.Interaction,
         role: nextcord.Role = nextcord.SlashOption(
             name="rola",
             description="Wybierz rolę do dodania",
             required=True
         )):
        await interaction.response.defer(ephemeral=True)

        self.database.add_forward_role(guild_id=interaction.guild.id, role_id=role.id)

        roles_ids = self.database.get_forward_roles(guild_id=interaction.guild.id)
        all_forward = [f"<@&{r_id}>" for r_id in roles_ids]

        content = (
            f"Dodano {role.mention} do funkcji przekazywania.\n\n"
            "**Wszystkie role w konfiguracji:**\n"
            f"{', '.join(all_forward)}"
        )

        await interaction.followup.send(content=content, ephemeral=True)

    @nextcord.slash_command(
        name="usun_z_przekazania",
        description="Usuwa rolę z listy odbiorców przekazywanych wiadomości",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    @application_checks.has_permissions(administrator=True)
    @application_checks.guild_only()
    async def remove_from_forward(self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(
            name="rola",
            description="Wybierz rolę do usunięcia",
            required=True
        )):
        await interaction.response.defer(ephemeral=True)

        current_roles = self.database.get_forward_roles(guild_id=interaction.guild.id)

        if role.id not in current_roles:
            return await interaction.followup.send(
                f"Rola {role.mention} nie znajduje się na liście do przekazywania.",
                ephemeral=True
            )
        self.database.remove_forward_role(guild_id=interaction.guild.id, role_id=role.id)

        updated_roles = self.database.get_forward_roles(guild_id=interaction.guild.id)

        if updated_roles:
            all_forward = [f"<@&{r_id}>" for r_id in updated_roles]
            list_display = f"Pozostałe role:\n{', '.join(all_forward)}"
        else:
            list_display = "Lista ról jest teraz **pusta**."

        content = (
            f"Usunięto {role.mention} z funkcji przekazywania.\n\n"
            f"{list_display}"
        )

        await interaction.followup.send(content=content, ephemeral=True)
