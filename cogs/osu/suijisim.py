import pandas as pd
import random
import matplotlib.pyplot as plt
from pandas.plotting import table

CACHE_FILE_PATH = '/home/bot/Kogomi-disc/cogs/osu/data/cache'
PLAYER_LIST_PATH = '/home/bot/Kogomi-disc/cogs/osu/data/suijilist.txt'

def ssim():
    users = []
    with open(PLAYER_LIST_PATH) as f:
        for line in f:
            users.append(line[:-1])

    seeds = []
    for seed in ['A', 'B', 'C', 'D']:
        for num in range(64):
            seeds.append(seed)

    nums_a = list(range(1, 65))
    nums_b = list(range(1, 65))
    nums_c = list(range(1, 65))
    nums_d = list(range(1, 65))

    for num in [nums_a, nums_b, nums_c, nums_d]:
        random.shuffle(num)

    team_order = nums_a + nums_b + nums_c + nums_d

    players_df = pd.DataFrame({'player': users, 'seed': seeds, 'team': team_order})

    players_df['seed'] = players_df.apply(lambda x: x['seed'] + '1' if x['team'] < 33 else x['seed'] + '2', axis=1)
    players_df['team'] = (players_df['team'] % 32) + 1

    teams_df = players_df.pivot(index='team', columns='seed', values='player')
    tableColLength = len(teams_df)
    tableRowLength = len(teams_df.columns)

    fig, ax = plt.subplots(frameon=False)

    tablee = table(ax, teams_df, loc='center')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.axis('off')
    tablee.auto_set_font_size(False)
    tablee.set_fontsize(14)
    tablee.scale(4,4)

    desiredBgColor = (0.75,0.75,0.75)
    for cIx in range(0, tableColLength+1):
        for rIx in range(0, tableRowLength):
            if cIx > 0:
                c = tablee.get_celld()[(cIx, rIx)]
                cellText = c.get_text()
                if (cellText.get_text() == 'nan'):
                    cellText.set_text('')
                c.set_color(desiredBgColor)
                c.set_edgecolor('black')
            else:
                c = tablee.get_celld()[(cIx, rIx)]
                c.set_text_props(**{
                    'size' : 24,
                })
    code = random.randint(100000000,999999999)
    plt.savefig(f'{CACHE_FILE_PATH}/sim_{code}.png', bbox_inches='tight')
    return code
