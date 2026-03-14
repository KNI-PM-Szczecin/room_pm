import nextcord
from datetime import datetime
from nextcord.ext import commands
from utilities import baseUtils, dcDatabase

class ActivityEventsCog(commands.Cog):
    POINT_MAP = {
        "new_message": 1.0,
        "edit_message": 0.0,
        "delete_message": 0.0,
        "reaction_add": 1.0,
        "interaction": 0.1,
        "voice_per_minute": 0.1,
        #system message points
        "member_join": 5.0,          # Point for the user who just joined
        "server_boost": 1.5,         # High reward for boosting the server
        "server_boost_tier": 3.0,    # Reward for reaching a new boost tier
        "pinned_message": 2.0,       # Points for the user who pinned a message
        "thread_started": 2.0,       # Points for starting a new thread
        "generic_system": 1.0        # Fallback for other system messages
    }

    def __init__(self, client, config: baseUtils.ConfigReader, database: dcDatabase.DB):
        self.client = client
        self.config = config
        self.database = database
        self.voice_start_times = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f" > Activity Tracking System is now ONLINE.")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if not message.guild:
            return

        if message.is_system():
            await self._handle_system_message(message)
            return

        if message.author.bot:
            return

        self.database.add_activity_points(
            message.author.id,
            message.guild.id,
            self.POINT_MAP["new_message"]
        )

    async def _handle_system_message(self, message: nextcord.Message):
        if not message.author or message.author.bot:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        m_type = message.type
        points = 0.0

        if m_type == nextcord.MessageType.new_member:
            points = self.POINT_MAP["member_join"]

        elif m_type == nextcord.MessageType.premium_guild_subscription:
            points = self.POINT_MAP["server_boost"]

        elif m_type in [
            nextcord.MessageType.premium_guild_tier_1,
            nextcord.MessageType.premium_guild_tier_2,
            nextcord.MessageType.premium_guild_tier_3
        ]:
            points = self.POINT_MAP["server_boost_tier"]

        elif m_type == nextcord.MessageType.pins_add:
            points = self.POINT_MAP["pinned_message"]

        elif m_type in [
            nextcord.MessageType.thread_created,
            nextcord.MessageType.thread_starter_message
        ]:
            points = self.POINT_MAP["thread_started"]

        else:
            points = self.POINT_MAP["generic_system"]

        if points > 0:
            self.database.add_activity_points(user_id, guild_id, points)

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if after.author.bot or not after.guild:
            return
        self.database.add_activity_points(after.author.id, after.guild.id, self.POINT_MAP["edit_message"])

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        if message.author.bot or not message.guild:
            return
        self.database.add_activity_points(message.author.id, message.guild.id, self.POINT_MAP["delete_message"])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if (payload.member and payload.member.bot) or not payload.guild_id:
            return
        self.database.add_activity_points(payload.user_id, payload.guild_id, self.POINT_MAP["reaction_add"])

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if not interaction.guild or (interaction.user and interaction.user.bot):
            return
        self.database.add_activity_points(interaction.user.id, interaction.guild.id, self.POINT_MAP["interaction"])

    @commands.Cog.listener()
    async def on_voice_state_update(self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState
    ):
        if member.bot: return

        user_id, guild_id = member.id, member.guild.id
        session_key = (user_id, guild_id)
        afk_channel = member.guild.afk_channel

        def process_voice_session(start_time):
            duration = datetime.now() - start_time
            full_minutes = int(duration.total_seconds() // 60)

            if full_minutes > 0:
                raw_points = full_minutes * self.POINT_MAP["voice_per_minute"]
                final_points = round(raw_points, 2)
                self.database.add_activity_points(user_id, guild_id, final_points)

        if before.channel is not None and (after.channel is None or after.channel == afk_channel):
            if session_key in self.voice_start_times:
                start_time = self.voice_start_times.pop(session_key)
                process_voice_session(start_time)

        elif after.channel is not None and after.channel != afk_channel:
            if before.channel is not None and session_key in self.voice_start_times:
                start_time = self.voice_start_times.pop(session_key)
                process_voice_session(start_time)

            self.voice_start_times[session_key] = datetime.now()