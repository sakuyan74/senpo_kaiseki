
# from . import senpo_kaiseki
from senpo_kaiseki import discordbot
import os
import json

TOKEN = os.environ["DISCORD_BOT_TOKEN"]


if __name__ == '__main__':
    # 設定ファイル読み込み
    with open("./settings.json", "r", encoding="utf-8_sig") as f:
        settings = json.load(f)
    # 設定ファイル読み込み
    with open("./errorcode.json", "r", encoding="utf-8_sig") as f2:
        errorcode = json.load(f2)
    bot = discordbot.DiscordBot(settings=settings, errorcode=errorcode, command_prefix='!')]
    cog = bot.get_cog('ReadCog')
    commands = cog.get_commands()
    print([c.name for c in commands])
    bot.run(TOKEN)
