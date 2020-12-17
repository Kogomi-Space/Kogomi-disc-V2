from decouple import config
from .databaseClass import DatabaseClass as DB
import discord
import asyncio
import aiohttp

class UserClass:

    def __init__(self, user = "", discid = None):
        self.db = DB()
        username = " ".join(user)
        self.user = self.db.fetch_osuname(discid) if username == "" else username
        self.id = self.db.fetch_osuid(discid)
        self.discid = discid
        self.url = "https://osu.ppy.sh/api"
        self.key = config('OSUAPI')
        self.cache = config('CACHE_FILE_PATH')
        self.header = { "content-type": "application/json", "user-key": self.key }

    def embed(self, json):
        embed = discord.Embed()
        embed.title = json[0]["username"]
        embed.url = "https://osu.ppy.sh/u/{}".format(json[0]["user_id"])
        embed.set_footer(text="Powered by osu!")
        embed.add_field(name="Join date", value=json[0]["join_date"][:10])
        embed.add_field(name="Accuracy", value=json[0]["accuracy"][:6])
        embed.add_field(name="Level", value=json[0]["level"][:5])
        embed.add_field(name="Ranked score", value=json[0]["ranked_score"])
        embed.add_field(name="Rank", value=json[0]["pp_rank"])
        embed.add_field(name="Country rank ({})".format(json[0]["country"]), value=json[0]["pp_country_rank"])
        embed.add_field(name="Playcount", value=json[0]["playcount"])
        embed.add_field(name="Total score", value=json[0]["total_score"])
        embed.add_field(name="Total seconds played", value=json[0]["total_seconds_played"])
        # try:
        #     file, rankgraph = await osu.rank_graph(0)
        #     embed.set_image(url='attachment://{}'.format(rankgraph))
        #     embed.set_thumbnail(url="https://a.ppy.sh/{}".format(res[0]["user_id"]))
        #     await ctx.send(file=file,embed=embed)
        # except:
        embed.set_thumbnail(url="https://a.ppy.sh/{}".format(json[0]["user_id"]))
        return embed

    async def getUser(self, user = False, userCheck = False):
        if not user:
            user = self.id
        json = await self.fetch_json('get_user',f'u={user}')
        if len(json) == 0:
            return False
        if self.discid:
            print("hey")
            res = self.db.change_osuname(self.discid, json[0]['username'])
        if not userCheck: return json
        return user

    async def getUserBest(self, user = False):
        user = getUser(user=user, userCheck=True)
        json = await self.fetch_json('get_user_best',f'u={user}&m=0&limit=100')
        if len(json) == 0:
            return False
        return json

    async def getUserRecent(self, user = False):
        user = getUser(user=user, userCheck=True)
        json = await self.fetch_json('get_user_recent',f'u={user}&m=0&limit=50')
        if len(json) == 0:
            return False
        return json

    async def fetch_json(self, type, params = ""):
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get(f'{self.url}/{type}?k={self.key}&{params}') as channel:
                    res = await channel.json()
                    return res

            except Exception as e:
                return {}
