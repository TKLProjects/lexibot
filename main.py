# Imports
import os
import discord
from discord.ext import commands
import json

# Dotenv token business
import dotenv
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TOKEN")

# Logging
import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./botfiles/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Per-server prefixes
def get_prefix(client, message):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix = get_prefix)

@client.event
async def on_ready():
    print("Ready")
    print("Logged in as:", client.user.name, "(" + str(client.user.id) + ")")

def am_owner(ctx):
    return ctx.author.id == 464733215903580160, 465702500146610176, 465662909645848577

@client.event
async def on_guild_join(guild):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = ','

    with open('./botfiles/prefixes.json', 'r') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes.pop(str(guild.id))

    with open('./botfiles/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments!')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('This command doesn\'t seem to exist. Please see `,help` for a list!')
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send('It seems I\'m lacking permissions to perform this action...')
    if isinstance(error, commands.CommandError):
        await ctx.send(f'An error occured!\n```{error}```')
    if isinstance(error, commands.NSFWChannelRequired):
        await ctx.send('This command requires a channel to be marked as NSFW!')

# purge
@client.command()
async def purge(ctx, amount=0):
    if amount == 0:
        await ctx.send("Please provide a number.")
    else:
        await ctx.channel.purge(limit=amount+1)

# Change prefix
@client.command()
@commands.check(am_owner)
async def chprefix(ctx, prefix):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes[str(ctx.guild.id)] = prefix

    with open('./botfiles/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    
    await ctx.send(f'Prefix changed to: {prefix}')

@client.command()
@commands.check(am_owner)
async def status(ctx, status):
    if status == "online":
        await client.change_presence(status=discord.Status.online)
        await ctx.send(f"Changed bot presence to: online.")
    if status == "idle":
        await client.change_presence(status=discord.Status.idle)
        await ctx.send(f"Changed bot presence to: idle.")
    if status == 'dnd': 
        await client.change_presence(status=discord.Status.dnd)
        await ctx.send(f"Changed bot presence to: do not disturb.")
    if status == "invisible":
        await client.change_presence(status=discord.Status.invisible)
        await ctx.send(f"Changed bot presence to: invisible.")

# create channel
@client.command()
@commands.check(am_owner)
async def create(ctx, cname):
    guild = ctx.message.guild
    await guild.create_text_channel(cname)
client.run(token)