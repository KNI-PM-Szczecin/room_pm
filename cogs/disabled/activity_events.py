import nextcord
from datetime import datetime
from nextcord.ext import commands
from utilities import baseUtils, dcDatabase

class ActivityCog(commands.Cog):
    POINT_MAP = {
        "new_message": 1.0,
        "edit_message": 0.0,
        "delete_message": 0.0,
        "reaction_add": 1.0,
        "interaction": 0.0,
        "system_message": 1.0,
        "voice_per_minute": 0.1
    }

    def __init__(self, client, config: baseUtils.ConfigReader, database: dcDatabase.DB):
        self.client = client
        self.config = config
        self.database = database
        self.voice_start_times = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" > Logged in as {self.client.user}. Activity Tracking System is now ONLINE.")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if not message.guild:
            return

        if message.is_system():
            if message.author and not message.author.bot:
                self.database.add_activity_points(
                    message.author.id,
                    message.guild.id,
                    self.POINT_MAP["system_message"]
                )
            return

        if message.author.bot:
            return

        self.database.add_activity_points(
            message.author.id,
            message.guild.id,
            self.POINT_MAP["new_message"]
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if after.author.bot or not after.guild:
            return

        self.database.add_activity_points(
            after.author.id,
            after.guild.id,
            self.POINT_MAP["edit_message"]
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        if message.author.bot or not message.guild:
            return

        self.database.add_activity_points(
            message.author.id,
            message.guild.id,
            self.POINT_MAP["delete_message"]
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if payload.member and payload.member.bot:
            return

        if not payload.guild_id:
            return

        self.database.add_activity_points(
            payload.user_id,
            payload.guild_id,
            self.POINT_MAP["reaction_add"]
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if not interaction.guild or (interaction.user and interaction.user.bot):
            return

        self.database.add_activity_points(
            interaction.user.id,
            interaction.guild.id,
            self.POINT_MAP["interaction"]
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState
    ):
        if member.bot:
            return

        user_id = member.id
        guild_id = member.guild.id
        session_key = (user_id, guild_id)
        afk_channel = member.guild.afk_channel

        if before.channel is not None and (after.channel is None or after.channel == afk_channel):
            if session_key in self.voice_start_times:
                start_time = self.voice_start_times.pop(session_key)
                duration = datetime.now() - start_time
                minutes = duration.total_seconds() / 60

                points = minutes * self.POINT_MAP["voice_per_minute"]
                if points > 0:
                    self.database.add_activity_points(user_id, guild_id, points)

        elif after.channel is not None and after.channel != afk_channel:
            if before.channel is not None and session_key in self.voice_start_times:
                start_time = self.voice_start_times.pop(session_key)
                duration = datetime.now() - start_time
                minutes = duration.total_seconds() / 60
                self.database.add_activity_points(
                    user_id,
                    guild_id,
                    minutes * self.POINT_MAP["voice_per_minute"]
                )

            self.voice_start_times[session_key] = datetime.now()