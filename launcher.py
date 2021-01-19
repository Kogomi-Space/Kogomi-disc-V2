import discord
from discord.ext import commands

import os, sys, traceback
from subprocess import call
from random import randrange

call(['python3', '-m', 'pip', 'install', '--upgrade', 'discord.py[voice]'])

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['-']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_extensions = ['cogs.general',
                      'cogs.owner',
                      'cogs.errorhandler',
                      'cogs.osu.osu']

bot = commands.Bot(command_prefix=get_prefix, description='Kogomi--The Virtual Assistant')

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone join my server: https://discord.gg/hFWKxmD27Z"))
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    print(f'Successfully logged in and booted...!')


bot.run(os.environ['KOGOMI_TOKEN'], bot=True, reconnect=True)
