from decouple import config
import asyncio
import aiohttp
import json

class OsuClass:

    def __init__(self):
        self.apiurl = 'https://osu.ppy.sh/api'
        self.key = config('OSUAPI')
        self.header = { "content-type": "application/json", "user-key": self.key }

    async def getMatch(self, mp):
        json = await self.fetch_json("get_match", f'mp={mp}')
        if len(json) == 0:
            return False
        return json

    async def fetch_json(self,type,params = ""):
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get(f'{self.apiurl}/{type}?k={self.key}&{params}') as channel:
                    res = await channel.json()
                    return res
            except Exception as e:
                return {}

    def calculate_acc(self,beatmap):
        total_unscale_score = float(beatmap['count300'])
        total_unscale_score += float(beatmap['count100'])
        total_unscale_score += float(beatmap['count50'])
        total_unscale_score += float(beatmap['countmiss'])
        total_unscale_score *=300
        user_score = float(beatmap['count300']) * 300.0
        user_score += float(beatmap['count100']) * 100.0
        user_score += float(beatmap['count50']) * 50.0
        return (float(user_score)/float(total_unscale_score)) * 100.0
