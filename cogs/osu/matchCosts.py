import discord
import random
from collections import OrderedDict

async def mcformula(self, url, res, warmups):
    if res['match'] == 0:
        return False
    if warmups <= 0:
        pass
    else:
        try:
            for i in range(warmups):
                del res['games'][0]
        except Exception as e:
            pass
    if int(res['games'][0]['team_type']) == 2:
        teamVS = True
    else:
        teamVS = False
    res['games'], playerlist = parse_match(res['games'], teamVS)
    try:
        if ":" in res['match']['name']:
            name = res['match']['name'].split(":")
        else:
            name = res['match']['name'].split("(", 1)
    except:
        name = res['match']['name']
    try:
        tname = name[0]
        team1 = name[1].split("vs")
        team2 = team1[1]
        team1 = team1[0]
        team1 = ''.join(c for c in team1 if c not in ' ()')
        team2 = ''.join(c for c in team2 if c not in ' ()')
    except:
        try:
            del team1
            del team2
            del tname
        except:
            pass
        name = res['match']['name']

    if teamVS:
        userlist0, pointlist0 = sortdict(playerlist[1])
        userlist1, pointlist1 = sortdict(playerlist[2])
        f = []
        f.append(":blue_circle: **Blue Team** :blue_circle:")
        for index, player in enumerate(userlist0):
            try:
                username = await self.user.getUser(user=player)
                username = username[0]['username']
            except:
                username = player + " (Banned)"
            f.append("**{}**: {:15} - **{:0.2f}**".format(index + 1, username, pointlist0[index]))
        f.append("")
        f.append(":red_circle: **Red Team** :red_circle:")
        for index, player in enumerate(userlist1):
            try:
                username = await self.user.getUser(user=player)
                username = username[0]['username']
            except:
                username = player + " (Banned)"
            f.append("**{}**: {:15} - **{:0.2f}**".format(index + 1, username, pointlist1[index]))
        f = "\n".join(f)
        try:
            embed = discord.Embed(
                title="<a:mLoading:529680784194404352> {}: {} vs {}".format(tname, team1, team2),
                url="https://osu.ppy.sh/mp/" + url,
                description=f)
        except:
            embed = discord.Embed(title="<a:mLoading:529680784194404352> {}".format(name),
                                  url="https://osu.ppy.sh/mp/" + url,
                                  description=f)
    else:
        userlist, pointlist = sortdict(playerlist)
        f = []
        for index, player in enumerate(userlist):
            try:
                username = await self.user.getUser(user=player)
                username = username[0]['username']
            except Exception as e:
                print(e)
                username = player + " (Banned)"
            f.append("**{}**: {:15} - **{:0.2f}**".format(index + 1, username, pointlist[index]))
        f = "\n".join(f)
        try:
            embed = discord.Embed(
                title="<a:mLoading:529680784194404352> {}: {} vs {}".format(tname, team1, team2),
                url="https://osu.ppy.sh/mp/" + url,
                description=f)
        except:
            embed = discord.Embed(title="<a:mLoading:529680784194404352> {}".format(name),
                                  url="https://osu.ppy.sh/mp/" + url,
                                  description=f)
    footer = ['o_o','oh god','O _o','why can\'t I hit any of the fucking notes','it\'s so doomed','hey good job guys']
    embed.set_footer(text=footer[random.randint(0,5)])
    return embed

def parse_match(games,teamVS):
    plist = {}
    for game in games:
        try:
            del game['game_id']
        except:
            pass
        try:
            del game['play_mode']
        except:
            pass
        try:
            del game['match_type']
        except:
            pass
        try:
            del game['team_type']
        except:
            pass
        try:
            starttime = datetime.datetime.strptime(game['start_time'],"%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(game['end_time'],"%Y-%m-%d %H:%M:%S")
            timediff = endtime - starttime
            game["time_taken"] = str(timediff)
        except:
            pass
        try:
            del game['start_time']
            del game['end_time']
            del game['scoring_type']
        except:
            pass
        scoresum = 0
        game['newscores'] = []
        game['playercount'] = 0
        for score in game['scores']:
            try:
                if 'EZ' in num_to_mod(int(score['enabled_mods'])):
                    score['score'] = int(score['score'])
                    score['score'] *= 2
            except:
                pass
            g = {}
            if int(score['score']) < 1000:
                continue
            g['user_id'] = score['user_id']
            if teamVS:
                try:
                    plist[int(score['team'])][g['user_id']] = 0
                except:
                    plist[int(score['team'])] = {}
                    plist[int(score['team'])][g['user_id']] = 0

            else:
                plist[g['user_id']] = 0
            g['score'] = score['score']
            g['maxcombo'] = score['maxcombo']
            g['acc'] = calculate_acc(score)
            g['enabled_mods'] = score['enabled_mods']
            scoresum += int(score['score'])
            game['playercount'] += 1
            game['newscores'].append(g)
        game['scoresum'] = scoresum
        try:
            del game['scores']
        except:
            pass
        for newscore in game['newscores']:
            avg = int(game['scoresum']) / game['playercount']
            pointcost = (int(newscore['score']) / avg) + 0.4
            newscore['point_cost'] = pointcost
    k = 0.4
    if teamVS:
        for player,point in plist[1].items():
            pointlist = []
            for game in games:
                for score in game['newscores']:
                    if player == score['user_id']:
                        pointlist.append(score['point_cost'])
            pointmax = 0
            for i in range(0,len(pointlist)):
                pointmax += pointlist[i]
            plist[1][player] = pointmax / len(pointlist) - 0.1
            plist[1][player] *= 1.2 ** ((len(pointlist)/len(games))**k)
        for player,point in plist[2].items():
            pointlist = []
            for game in games:
                for score in game['newscores']:
                    if player == score['user_id']:
                        pointlist.append(score['point_cost'])
            pointmax = 0
            for i in range(0,len(pointlist)):
                pointmax += pointlist[i]
            plist[2][player] = pointmax / len(pointlist) - 0.1
            plist[2][player] *= 1.2 ** ((len(pointlist)/len(games))**k)
    else:
        for player,point in plist.items():
            pointlist = []
            for game in games:
                for score in game['newscores']:
                    if player == score['user_id']:
                        pointlist.append(score['point_cost'])
            pointmax = 0
            for i in range(0,len(pointlist)):
                pointmax += pointlist[i]
            plist[player] = pointmax / len(pointlist)

    return games, plist

def sortdict(main_list):
    list1 = []
    list2 = []
    try:
        od = OrderedDict(sorted(main_list.items(),key=lambda x:x[1], reverse=True))
    except:
        od = sorted(main_list.items(),key=lambda x:x[1], reverse=True)
    for key,value in od.items():
        list1.append(key)
        list2.append(value)
    return list1, list2

def calculate_acc(beatmap):
    total_unscale_score = float(beatmap['count300'])
    total_unscale_score += float(beatmap['count100'])
    total_unscale_score += float(beatmap['count50'])
    total_unscale_score += float(beatmap['countmiss'])
    total_unscale_score *=300
    user_score = float(beatmap['count300']) * 300.0
    user_score += float(beatmap['count100']) * 100.0
    user_score += float(beatmap['count50']) * 50.0
    return (float(user_score)/float(total_unscale_score)) * 100.0
