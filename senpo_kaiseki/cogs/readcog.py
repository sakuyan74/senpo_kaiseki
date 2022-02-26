from discord.ext import commands


class ReadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("init ReadCog")

    @commands.command()
    async def neko(self, ctx):
        print("neko")
        await ctx.send('にゃーん♡')


def setup(bot):
    bot.add_cog(ReadCog(bot))
