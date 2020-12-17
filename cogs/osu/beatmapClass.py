import os
from decouple import config
import pyttanko
import asyncio
import aiohttp
import discord
import datetime
import json

class BeatmapClass:

    def __init__(self):
        self.apiurl = 'https://osu.ppy.sh/api'
        self.mapurl = 'https://osu.ppy.sh/osu'
        self.key = config('OSUAPI')
        self.cache = config('CACHE_FILE_PATH')
        self.header = { "content-type": "application/json", "user-key": self.key }

    # Fetches a generated embed message for any beatmap
    async def beatmap_embed(self, mapid: str):
        ptnko, api = await self.getBeatmap(mapid, accs=[95, 99, 100])
        mapper = api[0]['creator']
        mapperlink = f"https://osu.ppy.sh/users/{api[0]['creator_id']}"
        dllink = f"https://osu.ppy.sh/d/{api[0]['beatmapset_id']}"
        bclink = f"https://bloodcat.com/osu/s/{api[0]['beatmapset_id']}"
        preview = f"https://bloodcat.com/osu/preview.html#{api[0]['beatmap_id']}"
        embed = discord.Embed(description=f'by [{mapper}]({mapperlink})\nDownload: [official]({dllink}) ([no vid]({dllink}n)) [bloodcat]({bclink}), [Map Preview]({preview})', color=0x83CDE4)
        embed.set_author(name=f"{api[0]['artist']} - {api[0]['title']}",
                         url=f"https://osu.ppy.sh/beatmapsets/{api[0]['beatmapset_id']}#osu/{api[0]['beatmap_id']}")
        embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{api[0]['beatmapset_id']}l.jpg")
        len = float(api[0]['total_length'])
        bpm = str(round(float(api[0]['bpm']), 2)).rstrip("0")
        if bpm.endswith("."): bpm = bpm[:-1]
        length = str(datetime.timedelta(seconds=len))
        if length[:1] == "0": length = length[2:]
        ar = str(round(ptnko['ar'], 2)).rstrip("0")
        if bpm.endswith("."): bpm = bpm[:-1]
        if ar.endswith("."): ar = ar[:-1]
        od = str(round(ptnko['od'], 2)).rstrip("0")
        if od.endswith("."): od = od[:-1]
        cs = str(round(ptnko['cs'], 2)).rstrip("0")
        if cs.endswith("."): cs = cs[:-1]
        hp = str(round(ptnko['hp'], 2)).rstrip("0")
        if hp.endswith("."): hp = hp[:-1]
        f = []
        f.append(f"◆ {round(float(ptnko['stars']), 2)}***** ◆ **Length:** {length} ◆ {round(float(bpm), 2)} **BPM**")
        f.append(f"◆ **AR** {ar} ◆ **OD** {od} ◆ **HP** {hp} ◆ **CS** {cs}")
        f.append(f"◆ **{round(float(ptnko['pp'][0]), 2)}pp** for 95% ◆ **{round(float(ptnko['pp'][1]), 2)}pp** for 99% ◆ **{round(float(ptnko['pp'][2]), 2)}pp** for SS")
        embed.add_field(name=f"**{api[0]['version']}**", value="\n".join(f), inline=False)
        return embed

    async def mrank(self, mapID, mapScore, user):
        res = await self.fetch_json("get_scores",f"b={mapID}&limit=100")
        idx = 1
        for score in res:
            if score['user_id'] == user:
                if score['score'] == mapScore:
                    return idx
            idx += 1
        return None

    async def bloodcat(self, search, params):
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get(f"https://bloodcat.com/osu/?mod=json&q={search}{params}") as channel:
                    res = await channel.json()
                    return res
            except Exception as e:
                return {}

    async def getBeatmap(self, mapid, accs=[100], mods=0, misses=0, combo=None, completion=None, fc=None):
        # try:
        ptnko = await self.get_pyttanko(mapid,accs,mods,misses,combo,completion,fc)
        # except Exception as e:
            # print(e)
            # ptnko = False
        res = await self.fetch_json("get_beatmaps",f"b={mapid}")
        return ptnko, res # First json from pyttanko, second json from osu! API

    async def get_pyttanko(self, mapid: str, accs=[100], mods=0, misses=0, combo=None, completion=None, fc=None):
        file_path = self.cache + f'/{mapid}.osu'
        await self.download_file(self.mapurl + f'/{mapid}', file_path)
        bmap = pyttanko.parser().map(open(file_path))
        _, ar, od, cs, hp = pyttanko.mods_apply(mods, ar=bmap.ar, od=bmap.od, cs=bmap.cs, hp=bmap.hp)
        stars = pyttanko.diff_calc().calc(bmap,mods=mods)
        bmap.stars = stars.total
        bmap.aim_stars = stars.aim
        bmap.speed_stars = stars.speed

        if not combo:
            combo = bmap.max_combo()

        bmap.pp = []
        bmap.aim_pp = []
        bmap.speed_pp = []
        bmap.acc_pp = []

        bmap.acc = accs

        for acc in accs:
            n300, n100, n50 = pyttanko.acc_round(acc, len(bmap.hitobjects), misses)
            pp, aim_pp, speed_pp, acc_pp, _ = pyttanko.ppv2(
                bmap.aim_stars, bmap.speed_stars, bmap=bmap, mods=mods,
                n300=n300, n100=n100, n50=n50, nmiss=misses, combo=combo)
            bmap.pp.append(pp)
            bmap.aim_pp.append(aim_pp)
            bmap.speed_pp.append(speed_pp)
            bmap.acc_pp.append(acc_pp)
        if fc:
            n300, n100, n50 = pyttanko.acc_round(fc, len(bmap.hitobjects), 0)
            fc_pp, _, _, _, _ = pyttanko.ppv2(
                bmap.aim_stars, bmap.speed_stars, bmap=bmap, mods=mods,
                n300=n300 + misses, n100=n100, n50=n50, nmiss=0, combo=bmap.max_combo())

        pyttanko_json = {
            'version': bmap.version,
            'title': bmap.title,
            'artist': bmap.artist,
            'creator': bmap.creator,
            'combo': combo,
            'max_combo': bmap.max_combo(),
            'misses': misses,
            'mode': bmap.mode,
            'stars': bmap.stars,
            'aim_stars': bmap.aim_stars,
            'speed_stars': bmap.speed_stars,
            'pp': bmap.pp,  # list
            'aim_pp': bmap.aim_pp,
            'speed_pp': bmap.speed_pp,
            'acc_pp': bmap.acc_pp,
            'acc': bmap.acc,  # list
            'cs': cs,
            'od': od,
            'ar': ar,
            'hp': hp
        }

        if completion:
            try:
                pyttanko_json['map_completion'] = (completion / len(bmap.hitobjects)) * 100
            except:
                pyttanko_json['map_completion'] = "Error"

        os.remove(file_path)
        return pyttanko_json

    async def fetch_json(self, type, params = ""):
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get(f'{self.apiurl}/{type}?k={self.key}&{params}') as channel:
                    res = await channel.json()
                    return res
            except Exception as e:
                return {} # Return nothing if no json was found. I don't like this kind of error handling, probably will change later

    async def download_file(self, url, filepath):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with open(filepath, 'wb') as f: # Creates a file in filepath, opens it as f
                    while True:
                        chunk = await response.content.read(1024) # Reads current chunk
                        if not chunk: # If there is no chunk, that means we've read the whole file. Break out of the loop.
                            break
                        f.write(chunk) # Write the chunk onto file
                return await response.release() # Returns the file downloaded
