from discord.ext import commands, tasks
from .userClass import UserClass as User
from .beatmapClass import BeatmapClass as Beatmap
from .databaseClass import DatabaseClass as Database
from .osuClass import OsuClass as Osuclass
from .matchCosts import mcformula
from .suijisim import ssim
import importlib
import datetime
import asyncio
import discord

CACHE_FILE_PATH = '/home/bot/Kogomi-disc-TE/cogs/osu/data/cache'

class Osu(commands.Cog):
    """Commands relating to the rhythm game osu!"""

    def __init__(self, bot):
        self.bot = bot
        self.REFRESH_CYCLE = 0
        self.LOG_CHANNEL_ID = 840415135034114068
        self.user = User()
        self.beatmap = Beatmap()
        self.db = Database()
        self.osu = Osuclass()
        self.refreshdb.start()

    def cog_unload(self):
        self.refreshdb.cancel()

    @commands.command()
    async def suijisim(self,ctx):
        code = ssim()
        await ctx.send(file=discord.File(f'{CACHE_FILE_PATH}/sim_{code}.png'))

    @commands.command(aliases=['sf'])
    async def sformat(self, ctx, mapid, mods = "NM"):
        mods = mods.lower()
        modnum = 0
        if mods == "hr": modnum = 16
        elif mods == "dt": modnum = 64
        ptnko, api = await self.beatmap.getBeatmap(mapid=mapid, mods=modnum)
        if mods == "dt":
            lnth = round(float(api[0]['total_length']) / 1.5)
            bpm = str(round(float(api[0]['bpm']) * 1.5,2)).rstrip("0")
        else:
            lnth = float(api[0]['total_length'])
            bpm = str(round(float(api[0]['bpm']),2)).rstrip("0")
        if bpm.endswith("."):
            bpm = bpm[:-1]
        length = str(datetime.timedelta(seconds=lnth))
        if length[:1] == "0":
            length = length[2:]
        ar = str(round(ptnko['ar'],2)).rstrip("0")
        if bpm.endswith("."):
            bpm = bpm[:-1]
        if ar.endswith("."):
            ar = ar[:-1]
        od = str(round(ptnko['od'],2)).rstrip("0")
        if od.endswith("."):
            od = od[:-1]
        cs = str(round(ptnko['cs'],2)).rstrip("0")
        if cs.endswith("."):
            cs = cs[:-1]
        f = []
        f.append("```")
        f.append(f"=HYPERLINK(\"https://osu.ppy.sh/b/{mapid}\",\"{api[0]['artist']} - {api[0]['title']} [{api[0]['version']}]\")")
        f.append(f"{mapid}")
        if mods == "fm":
            ptnkohr = await self.beatmap.get_pyttanko(mapid=mapid,mods=16)
            ar2 = str(round(ptnkohr['ar'],2)).rstrip("0")
            if ar2.endswith("."):
                ar2 = ar2[:-1]
            od2 = str(round(ptnkohr['od'],2)).rstrip("0")
            if od2.endswith("."):
                od2 = od2[:-1]
            cs2 = str(round(ptnkohr['cs'],2)).rstrip("0")
            if cs2.endswith("."):
                cs2 = cs2[:-1]
            f.append(f"{round(float(ptnko['stars']),2)} ★ | {round(float(ptnkohr['stars']),2)} ★")
            f.append(f"{bpm}")
            f.append(f"{length}")
            f.append(f"CS {cs}/{cs2}")
            f.append(f"OD {od}/{od2}")
            f.append(f"AR {ar}/{ar2}")
        else:
            f.append(f"{round(float(ptnko['stars']),2)} ★")
            f.append(f"{bpm}")
            f.append(f"{length}")
            f.append(f"CS {cs}")
            f.append(f"OD {od}")
            f.append(f"AR {ar}")
        f.append("```")
        await ctx.send("\n".join(f))

    @commands.command()
    async def osuset(self, ctx, *username_list):
        """Set your osu! username."""
        username = " ".join(username_list)
        if username == "":
            await ctx.send_help(ctx.command)
            return
        user = User(user=username_list,discid=ctx.author.id)
        json = await user.getUser()
        if not json:
            await ctx.send("User not found in the osu! database. :x:")
            return
        print(json)
        res = self.db.change_osuid(ctx.author.id,json[0]['user_id'],json[0]['username'])
        if res:
            await ctx.send(f"Added, your osu! username is set to {json[0]['username']}. ✅")
        else:
            await ctx.send("Something went wrong. Contact Dain for help.")

    @commands.command()
    async def osu(self, ctx, *username_list):
        """Shows an osu user!"""
        user = User(username_list, ctx.author.id)
        if not user.user:
            await ctx.send("**User not set, please set your osu! username using -osuset [Username]. ❌**")
            return

        res = await user.getUser()
        if res:
            await ctx.send(embed=user.embed(res))
        else:
            await ctx.send("No results.")

    @commands.command(aliases=['mc'])
    async def match_costs(self, ctx, url, warmups = 2):
        """Shows how well each player did in a multi lobby."""
        if 'https://osu.ppy.sh/community/matches' in url:
            try:
                url = url.split("matches/")
            except:
                await ctx.send("Invalid URL! :x:")
                return
            url = url[1]
        elif 'https://osu.ppy.sh/mp' in url:
            try:
                url = url.split('mp/')
            except:
                await ctx.send("Invalid URL! :x:")
                return
            url = url[1]
        async with ctx.typing():
            res = await self.osu.getMatch(mp=url)
            if not res:
                await ctx.send("Invalid URL! :x:")
                return
            embed = await mcformula(self, url, res, warmups)
            await ctx.send(embed=embed)

    @commands.command()
    async def acc(self,ctx,c300,c100,c50,cMisses):
        """Calculates your accuracy! Format: -acc [300s] [100s] [50s] [misses]"""
        temp = {
            'count300' : c300,
            'count100' : c100,
            'count50' : c50,
            'countmiss' : cMisses
        }
        await ctx.send("Your accuracy for [**{}**/**{}**/**{}**/**{}**] is **{}%**.".format(c300,c100,c50,cMisses,round(self.osu.calculate_acc(temp),2)))

    @commands.command()
    async def bws(self,ctx,rank,bcount):
        """Check your Badge Weighted Seeding rank. -bws [rank] [badgecount]"""
        bcount = int(bcount)
        rank = int(rank)
        newrank = bcount ** 2
        newrank = 0.9937 ** newrank
        newrank = rank ** newrank
        newrank = round(newrank)
        await ctx.send("Previous Rank: **{}**    Badge Count: **{}**".format(rank,bcount))
        await ctx.send("Rank after BWS: **{}**".format(newrank))

    @commands.command()
    async def petbws(self,ctx,rank,bcount):
        """Check your Badge Weighted Seeding rank for Pls Enjoy Tournament. -petbws [rank] [badgecount]"""
        bcount = int(bcount)
        rank = int(rank)
        newrank = 1 + bcount
        newrank **= 1.06
        newrank = 0.7 ** newrank
        newrank = (0.09 * rank) ** newrank
        newrank = (0.9 * rank) / newrank
        newrank = rank - newrank
        newrank = round(newrank)
        await ctx.send("Previous Rank: **{}**    Badge Count: **{}**".format(rank,bcount))
        await ctx.send("Rank after BWS: **{}**".format(newrank))

    @tasks.loop(hours=1.0)
    async def refreshdb(self):
        logChannel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        debugMsg = await logChannel.send("Refreshing DB...")
        await self.db.refresh()
        self.REFRESH_CYCLE += 1
        await debugMsg.edit(content=f"Refreshing DB... Complete. Cycled {self.REFRESH_CYCLE} time(s). ")



def setup(bot):
    bot.add_cog(Osu(bot))
