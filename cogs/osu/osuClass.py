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
