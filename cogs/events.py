from nextcord.ext import commands
from utilities import baseUtils, dcDatabase

class EventsCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader, database: dcDatabase.DB):
        self.client = client
        self.config = config
        self.database = database

    @commands.Cog.listener()
    async def on_ready(self):
        db_guild_ids = self.database.get_all_forward_guilds()

        added_count = 0
        for guild in self.client.guilds:
            if guild.id not in db_guild_ids:
                self.database.add_forward_guild(guild.id)
                added_count += 1
                print(f" > Guild synchronized: {guild.name} ({guild.id})")

        removed_count = 0
        for db_id in db_guild_ids:
            if not self.client.get_guild(db_id):
                self.database.remove_forward_guild(db_id)
                removed_count += 1

        if added_count > 0 or removed_count > 0:
            print(f" > Synchronization completed. Added: {added_count}, Removed: {removed_count}")
        else:
            print(" > The server database is up to date.")

        print(" >>> Client is ready.")
        print(f" > Bot name: {self.client.user.name}")
        print(f" > Bot id: {self.client.user.id}")
        print(f" > App id: {self.config.get_bot_id()} - (config file)")
        print(f" > https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=bot")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.database.add_forward_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.database.remove_forward_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        self.database.remove_forward_role(role.guild.id, role.id)