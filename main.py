from utilities import baseUtils
baseUtils.Requirements()

try:
    from nextcord.ext import commands
    import nextcord
    from utilities import dcDatabase
except:
    raise RuntimeError('\n > Failed to load libraries!\n')

def main():
    config = baseUtils.ConfigReader('config.json')
    database = dcDatabase.DB('./data', 'roompm.db')

    intents = nextcord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.messages = True
    intents.members = True
    intents.guilds = True

    client = commands.Bot(intents=intents)

    payload = {
        'client': client,
        'config': config,
        'database': database
    }

    baseUtils.Loader(payload)

    client.run(config.get_bot_token())

if __name__ == "__main__":
    main()