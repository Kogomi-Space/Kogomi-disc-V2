from discord.ext import commands
from .userClass import UserClass as User
from .beatmapClass import BeatmapClass as Beatmap
from .databaseClass import DatabaseClass as Database
import datetime
import asyncio

class Osu(commands.Cog):
    """Commands relating to the rhythm game osu!"""

    def __init__(self, bot):
        self.bot = bot
        self.user = User()
        self.beatmap = Beatmap()
        self.db = Database()

    @commands.command(name='sf')
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
            await ctx.send("Username can't be blank! :x:")
            return
        user = User(user=username,discid=ctx.author.id)
        json = await user.getUser(user=username)
        if not json:
            await ctx.send("User not found in the osu! database. :x:")
            return
        res = self.db.change_osuid(ctx.author.id,json[0]['user_id'],json[0]['username'])
        if res:
            await ctx.send(f"Added, your osu! username is set to {json[0]['username']}. ✅")
        else:
            await ctx.send("Something went wrong. Contact Dain for help.")

    @commands.command()
    async def osu(self, ctx,*username_list):
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

def setup(bot):
    bot.add_cog(Osu(bot))