import discord
from discord.ext import commands

client = commands.Bot(command_prefix = ',')
@client.command()
async def test(ctx):
    await ctx.send('no')
client.run('no')
print('Ready')

# test