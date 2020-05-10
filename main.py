# Imports
import logging
from dotenv import load_dotenv
import dotenv
import os
import discord
from discord.ext import commands
import json
import random
import requests
import time
import datetime
from datetime import date
import math

# Reddit
import praw
r = praw.Reddit(
    client_id='7VN5TAvLSUEMig',
    client_secret='tNGyfEDSTZrKucum16H3AEbgIuI',
    user_agent="lexibot")


# Dotenv token business
load_dotenv()
token = os.getenv("TOKEN")
weathertoken = os.getenv("WEATHERTOKEN")

# word split function for regional command


def split(word):
    return [":regional_indicator_" + char + ":" for char in word]


SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='./botfiles/discord.log',
    encoding='utf-8',
    mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Per-server prefixes


def get_prefix(client, message):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


# Client initialization
client = commands.Bot(command_prefix=get_prefix)

# Ready event
@client.event
async def on_ready():
    print("Ready")
    print("Logged in as:", client.user.name, "(" + str(client.user.id) + ")")


async def on_message(self, message):
    if message.author == client.user:
        return

# Owner check


def am_owner(ctx):
    return ctx.author.id == 464733215903580160, 465702500146610176, 465662909645848577

# Everything that happens when the bot joins a guild
@client.event
async def on_guild_join(guild):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = ','

    with open('./botfiles/prefixes.json', 'r') as f:
        json.dump(prefixes, f, indent=4)

# Everything that happens when the bot leaves a guild
@client.event
async def on_guild_remove(guild):
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('./botfiles/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

# Everything that happens when a command errors
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

# Purge command
@client.command()
async def purge(ctx, amount=0):
    """Purge a specified amount of messages. Usage: ?purge <amount>"""
    if amount == 0:
        await ctx.send("Please provide a number.")
    else:
        await ctx.channel.purge(limit=amount + 1)

# Change prefix
@client.command()
@commands.check(am_owner)
async def chprefix(ctx, prefix):
    """Change the server prefix. Usage: ?chprefix <prefix>"""
    with open('./botfiles/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('./botfiles/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'Prefix changed to: {prefix}')

# Status command
@client.command()
@commands.check(am_owner)
async def status(ctx, status):
    """Change the bot's status. Usage: ?status <status>"""
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

# Create channel command
@client.command()
@commands.check(am_owner)
async def create(ctx, type="text", *, cname):
    """Create a new channel. Usage: ?create <name> <type>"""
    if type == "text":
        guild = ctx.message.guild
        await guild.create_text_channel(cname)
    elif type == "voice":
        guild = ctx.message.guild
        await guild.create_voice_channel(cname)
    else:
        await ctx.send("Invalid type!")


# Weather command
@client.command(name="weather")
async def _weather(ctx, city_name):
    """Get weather information about a location. Usage: ?weather <location>"""
    base_url = "http://api.weatherapi.com/v1/current.json?"
    complete_url = base_url + "key=" + weathertoken + "&q=" + city_name
    try:
        response = requests.get(complete_url)
    except BaseException:
        await ctx.send("no")
    res = response.json()
    weather = res["current"]
    location = res["location"]
    condition = weather["condition"]

    current_temperature = str(int(weather["temp_c"])) + "°C"
    current_pressure = str(weather["pressure_mb"])[-3:] + "mBar"
    current_humidity = str(weather["humidity"]) + "%"
    image = "https:" + condition["icon"]
    weather_timezone = location["localtime"]
    weather_location = location["name"]
    weather_description = "Description: " + condition["text"]
    weather_wind_kph = str(weather["wind_kph"])
    weather_wind_dir = str(weather["wind_dir"])

    weatherembed = discord.Embed(
        title="Weather for " +
        weather_location,
        color=0x7ac5c9)
    weatherembed.set_author(
        name=f"{client.user.name}",
        icon_url=client.user.avatar_url)
    weatherembed.set_footer(text="https://weatherapi.com")
    weatherembed.add_field(name="Temperature:", value=current_temperature)
    weatherembed.add_field(name="Pressure:", value=current_pressure)
    weatherembed.add_field(name="Humidity:", value=current_humidity)
    weatherembed.add_field(
        name="Wind:",
        value=weather_wind_kph +
        " km/h " +
        weather_wind_dir)
    weatherembed.add_field(name="Time:", value=weather_timezone)
    weatherembed.set_thumbnail(url=image)
    await ctx.send(embed=weatherembed)

# Calc command
@client.command()
async def calc(ctx, n1, op, n2=0):
    """Calculate a mathematical expression. Usage: ?calc <num> <operator> <num>"""
    if op == "+":
        answer = int(n1) + int(n2)
        equation = f"```{n1}{op}{n2}```"
    elif op == "-":
        answer = int(n1) - int(n2)
        equation = f"```{n1}{op}{n2}```"
    elif op == "*":
        answer = int(n1) * int(n2)
        equation = f"```{n1}{op}{n2}```"
    elif op == "/":
        answer = int(n1) / int(n2)
        equation = f"```{n1}{op}{n2}```"
    elif op == "!" or op == "fac":
        answer = str(math.factorial(int(n1)))
        equation = f'```!{n1}```'
    elif op == "pow":
        answer = math.pow(int(n1), int(n2))
        equation = f"```{n1}" + f"{n2}".translate(SUP) + "```"
    elif op == "sqrt":
        answer = math.sqrt(int(n1))
        equation = f"```√{n1}```"
    else:
        await ctx.send("Invalid operator!")

    calcembed = discord.Embed(title="Calculator", color=0x7ac5c9)
    calcembed.add_field(name="Math equation:", value=equation)
    calcembed.add_field(name="Answer:", value=f"```{answer}```")
    await ctx.send(embed=calcembed)

# Eval command
@client.command(name='eval', hidden=True)
@commands.check(am_owner)
async def _eval(ctx, *, code):
    """A bad example of an eval command"""
    evalembed = discord.Embed(title="Code Evaluation", color=0x7ac5c9)
    evalembed.add_field(name="Input:", value=f"```{code}```")
    evalembed.add_field(name="Output:", value=f"```{eval(code)}```")
    await ctx.send(embed=evalembed)


# word to regional text [uses split function]
@client.command()
async def regional(ctx, *, regio):
    """Turn text into regional emojis. Usage: ?regional <text>"""
    if " " in regio:
        saferegio = regio.replace(" ", '')
        regchar = split(saferegio)
    else:
        regchar = split(regio)
    upreg = ''.join(regchar)
    lowreg = upreg.lower()
    if "regional_indicator_b" in lowreg:
        send = lowreg.replace("regional_indicator_b", 'b')
        await ctx.send(send)
    else:
        await ctx.send(lowreg)

# Reddit command
@client.command()
async def reddit(ctx, subname):
    """Fetch a random post from a subreddit. Usage: ?reddit <sub>"""
    try:
        submission = r.subreddit(f"{subname}").random()
        posttime = submission.created_utc
        realtime = datetime.datetime.utcfromtimestamp(
            posttime).strftime('%Y-%m-%d %H:%M:%S')
        redditembed = discord.Embed(
            title=submission.title,
            url=submission.url,
            color=0x7ac5c9)
        redditembed.set_image(url=submission.url)
        redditembed.set_footer(text="r/" + subname + " | " + realtime)
        await ctx.send(embed=redditembed)
    except BaseException:
        await ctx.send("This subreddit might be private or non-existant.")

# Avatr command
@client.command()
async def avatar(ctx):
    """Sends you your avatar."""
    avi_url = ctx.author.avatar_url
    aviembed = discord.Embed(title="Avatar of " + ctx.author.name, url=avi_url)
    aviembed.set_image(url=avi_url)
    await ctx.send(embed=aviembed)

# Userinfo command
@client.command()
async def userinfo(ctx):
    """Displays info about author."""
    currentDate = datetime.datetime.now()
    avi_url = ctx.author.avatar_url
    infoembed = discord.Embed()
    infoembed.set_author(
        name=ctx.author.name +
        "#" +
        ctx.author.discriminator,
        icon_url=avi_url)
    infoembed.add_field(name="Status", value=ctx.author.status)
    infoembed.add_field(name="Joined at", value=str(ctx.author.joined_at.day) +
                        "-" +
                        str(ctx.author.joined_at.month) +
                        "-" +
                        str(ctx.author.joined_at.year) +
                        " " +
                        str(ctx.author.joined_at.hour) +
                        ":" +
                        str(ctx.author.joined_at.minute))
    infoembed.add_field(name="Registered at", value=str(ctx.author.created_at.day) +
                        "-" +
                        str(ctx.author.created_at.month) +
                        "-" +
                        str(ctx.author.created_at.year) +
                        " " +
                        str(ctx.author.created_at.hour) +
                        ":" +
                        str(ctx.author.created_at.minute))
    infoembed.add_field(name="Nickname", value=ctx.author.display_name)
    infoembed.set_footer(text=str(currentDate.day) +
                         "-" +
                         str(currentDate.month) +
                         "-" +
                         str(currentDate.year) +
                         " " +
                         str(currentDate.hour) +
                         ":" +
                         str(currentDate.minute) +
                         ":" +
                         str(currentDate.second))
    infoembed.set_thumbnail(url=avi_url)
    await ctx.send(embed=infoembed)

# VC Rename command
@client.command()
async def desc(ctx, *, channelname):
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send("ok")

# Client login
client.run(token)
