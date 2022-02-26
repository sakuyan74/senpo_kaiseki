from discord.ext import commands
import discord


class ReadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def neko(self, ctx):
        await ctx.send('にゃーん♡')


def setup(bot):
    bot.add_cog(ReadCog(bot))
