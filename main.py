from utilities import baseUtils
baseUtils.Requirements()

try:
    from nextcord.ext import commands
    import nextcord
except:
    raise RuntimeError('\n > Failed to load libraries!\n')

def main():
    config = baseUtils.ConfigReader('config.json')

    intents = nextcord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.guilds = True

    client = commands.Bot(intents=intents)

    payload = {
        'client': client,
        'config': config
    }

    baseUtils.Loader(payload)

    client.run(config.get_bot_token())

if __name__ == "__main__":
    main()