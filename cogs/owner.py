from discord.ext import commands
import discord

class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'Loaded {cog}.')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'Unloaded {cog}.')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'Reloaded {cog}.')

    @commands.command(name='list', hidden=True)
    @commands.is_owner()
    async def list(self, ctx):
        """Shows a list of all loaded cogs."""
        cogs = self.bot.cogs
        f = []
        for cog in cogs:
            f.append(cog)
        await ctx.send(",".join(f))

    @commands.command(name='makeannounce', hidden=True)
    @commands.is_owner()
    async def makeannounce(self, ctx):
        announceChannel = self.bot.get_channel(800328080291397673)
        await ctx.send("OK! Ready. First tell me the title of this announcement.")
        title = await self.wait_for_message(ctx)
        await ctx.send("Perfect. Now the GitHub push URL. ")
        githubUrl = await self.wait_for_message(ctx)
        await ctx.send("If there's an image you'd like to include, post it now. If not, say \"none\".")
        imageUrl = await self.wait_for_message(ctx)
        if imageUrl.lower() == "none":
            imageUrl = None
        await ctx.send("Now tell me the actual changes.")
        body = await self.wait_for_message(ctx)
        embed=discord.Embed(color=0x83CDE4)
        embed.set_author(name=title, url=githubUrl)
        if imageUrl:
            embed.set_image(url=imageUrl)
        embed.add_field(name="-------------------------", value=body, inline=False)
        embed.set_thumbnail(url="https://i.imgur.com/UPetfcF.png")
        await ctx.send(embed=embed)
        await ctx.send("Is this correct?")
        res = await self.wait_for_message(ctx)
        if res.lower() == "y":
            await announceChannel.send(embed=embed)
        else:
            await ctx.send("please try again by sending the command again.")

    async def wait_for_message(self, ctx):
        def check(m):
            return m.channel == ctx.message.channel and m.author == ctx.message.author
        msg = await self.bot.wait_for('message', check=check)
        return msg.content

def setup(bot):
    bot.add_cog(Owner(bot))
