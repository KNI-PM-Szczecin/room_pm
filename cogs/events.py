from nextcord.ext import commands
from utilities import baseUtils

class EventsCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader):
        self.client = client
        self.config = config

    @commands.Cog.listener()
    async def on_ready(self):
        print("Client is ready.")
        print(f"Bot name: {self.client.user.name}")
        print(f"Bot id: {self.client.user.id}")
        print(f"App id: {self.config.get_bot_id()} - (config file)")