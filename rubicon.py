# bot.py
import os
import random

from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='[[')

quotes = ['hello', 'sup', 'hola']

@bot.event #bot has connected to discord successfully
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="greet", help="responds with a random greeting when $greet is used")
async def greet_user(ctx):
    response = random.choice(quotes)
    await ctx.send(response)

@bot.command(name="roll", help="rolls a dice with specified number of sides and number of rolls")
async def roll_dice(ctx, sides: int, numrolls: int):
    dice = [
        str(random.choice(range(1, sides+1)))
        for i in range(numrolls)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='create-channel', help="creates a channel, but only if you're an admin")
@commands.has_role('admin')
async def createChanel(ctx, name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=name)
    if not existing_channel:
        print(f'Creating a new channel: {name}')
        await guild.create_text_channel(name)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.command(name='setup-rubicon', help=f"sets up channels for rubicon raids (requires admin). \n (Default setup): [[setup-rubicon \n (Setup with already precreated channels, replace startRaidChannelName and activeRaidChannelName): [[setup-rubicon \"startRaidChannelName\" \"activeRaidChannelName\"")
@commands.has_permissions(administrator=True)
async def initialSetup(ctx):
    guild = ctx.guild
    existing_start_chan = discord.utils.get(guild.channels, name = "start-rubicon-party") #checks if start-rubicon-party is already a channel
    existing_active_chan = discord.utils.get(guild.channels, name = 'active-rubicon-parties') #checks if active-rubicon-parties is already a channel
    existing_category = discord.utils.get(guild.categories, name = "RUBICON CHANNELS") #checks if rubicon is already a category

    if not existing_category:
        print('Creating Rubicon category')
        await guild.create_category("RUBICON CHANNELS")

    rcategory = discord.utils.get(ctx.guild.categories, name="RUBICON CHANNELS") #get rubicon category object

    if not existing_start_chan and not existing_active_chan: #if both channels not created, create them
        print(f'Setting up Rubicon channels')
        await guild.create_text_channel("start rubicon party", category=rcategory)
        await guild.create_text_channel("active rubicon parties", category=rcategory)
    
    elif existing_start_chan and existing_active_chan: #if both channels already created, don't
        await ctx.send("Rubicon setup already complete. If you'd like to reset it, please delete any current channels named \"start-rubicon-party\" or \"active-rubicon-parties\" and run this command again")
        return

    elif existing_start_chan: #if only start channel is created, make other one
        print(f'Setting up Rubicon active chat')
        await guild.create_text_channel("active rubicon parties", category=rcategory)

    elif existing_active_chan: #if only active channel is created, make other one
        print(f'Setting up Rubicon party create chat')
        await guild.create_text_channel("start rubicon party", category=rcategory)

    await ctx.send("Rubicon setup complete") #setup complete

bot.run(TOKEN)







'''
@bot.event #responds with a greeting when user says hello
async def on_message(message):
    if message.author == bot.user:
        return

    if 'hello' in message.content:
        response = random.choice(quotes)
        await message.channel.send(response)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == 'what':
        response = random.choice(quotes)
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)
'''