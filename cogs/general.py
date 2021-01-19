import discord
import random
from discord.ext import commands


"""A simple cog example with simple commands. Showcased here are some check decorators, and the use of events in cogs.
For a list of inbuilt checks:
http://dischttp://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#checksordpy.readthedocs.io/en/rewrite/ext/commands/api.html#checks
You could also create your own custom checks. Check out:
https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L689
For a list of events:
http://discordpy.readthedocs.io/en/rewrite/api.html#event-reference
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#event-reference
"""


class General(commands.Cog):
    """General"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['gvoice'])
    async def generatevoice(self,ctx):
        try:
            vcid = ctx.message.author.voice.channel.id
            serverid = ctx.message.guild.id
            url = f"https://streamkit.discord.com/overlay/voice/{serverid}/{vcid}?icon=true&online=true&logo=white&text_color=%23ffffff&text_size=14&text_outline_color=%23000000&text_outline_size=0&text_shadow_color=%23000000&text_shadow_size=0&bg_color=%231e2124&bg_opacity=0.95&bg_shadow_color=%23000000&bg_shadow_size=0&invite_code=&limit_speaking=true&small_avatars=false&hide_names=false&fade_chat=0"
            async with ctx.typing():
                embed = discord.Embed()
                embed.title = "Voice Channel Stream Kit Link"
                embed.description = f"```{url}```\n\n[Test]({url})"
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("You're not in a voice channel! :x:")
            print(e)

    @commands.command()
    async def roll(self, ctx, num = 100):
        """Roll the Dice! (Defaults up to 100)"""
        messageAuthor = ctx.message.author
        rolledNumber = random.randint(1,num)
        await ctx.send(f"{messageAuthor.mention} rolled a {rolledNumber}.")

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(General(bot))
