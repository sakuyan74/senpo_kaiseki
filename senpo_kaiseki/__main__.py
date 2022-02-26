
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
    # 名前正誤表読み込み
    with open("./errata_list.json", "r", encoding="utf-8_sig") as f2:
        errata_list = json.load(f2)
    # 戦法武将名対照表読み込み
    with open("./heroname.json", "r", encoding="utf-8_sig") as f2:
        heroname = json.load(f2)
    bot = discordbot.DiscordBot(settings=settings, errorcode=errorcode, errata_list=errata_list, heroname=heroname, command_prefix='!')
    cog = bot.get_cog('ReadCog')
    commands = cog.get_commands()
    print([c.name for c in commands])
    print("PREFIX:" + str(bot.command_prefix))
    bot.run(TOKEN)
