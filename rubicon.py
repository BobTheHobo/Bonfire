# bot.py
import os
import random
import string

from dotenv import load_dotenv
import discord
from discord.ext import commands
import datetime

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
    else:
        print(error)

@bot.command(name='setup-rubicon', help=f"sets up channels for rubicon raids (requires admin). \n (Default setup): [[setup-rubicon \n (Setup with already precreated channels, replace startRaidChannelName and activeRaidChannelName): [[setup-rubicon \"startRaidChannelName\" \"activeRaidChannelName\"")
@commands.has_permissions(administrator=True)
async def initialSetup(ctx):
    guild = ctx.guild
    existing_start_chan = discord.utils.get(guild.channels, name = "start-rubicon-party") #checks if start-rubicon-party is already a channel
    existing_active_chan = discord.utils.get(guild.channels, name = 'active-rubicon-parties') #checks if active-rubicon-parties is already a channel

    if not existing_start_chan and not existing_active_chan: #if both channels not created, create them
        print(f'Setting up Rubicon channels')
        await guild.create_category("RUBICON CHANNELS") #creates rubicon category
        rcategory = discord.utils.get(ctx.guild.categories, name="RUBICON CHANNELS") #get rubicon category object
        await guild.create_text_channel("start rubicon party", category=rcategory)
        await guild.create_text_channel("active rubicon parties", category=rcategory)
    
    elif existing_start_chan and existing_active_chan: #if both channels already created, don't
        await ctx.send("Rubicon setup already complete. If you'd like to reset it, please delete any current channels named \"start-rubicon-party\" or \"active-rubicon-parties\" and run this command again")
        return

    elif existing_start_chan: #if only start channel is created, make other one
        print(f'Setting up Rubicon active chat')
        curCategory = existing_start_chan.category #if the user has moved the channel into another category, create the new channel there too
        await guild.create_text_channel("active rubicon parties", category=curCategory)

    elif existing_active_chan: #if only active channel is created, make other one
        print(f'Setting up Rubicon party create chat')
        curCategory = existing_active_chan.category #if the user has moved the channel into another category, create the new channel there too
        await guild.create_text_channel("start rubicon party", category=curCategory)

    await ctx.send("Rubicon setup complete") #setup complete

@bot.command(name="party", help="creates a new active party. name is optional")
async def partyCreate(ctx, *args):
    guild = ctx.guild

    author = ctx.message.author
    partyName = [author.name+"s", "party"]
    message = ""

    if len(args) > 0:
        partyName = list(args) #makes sure partyName is a list
    
    for i, name in enumerate(partyName):
        name = name.lower() #clears capitalization
        for char in string.punctuation: 
            name = name.replace(char, '') #replaces all punctuation in the name in attempt to keep as close to discord's channel naming schemes as possible
        partyName[i] = name 

    nameLen = len(partyName)
    pname = "-".join(partyName)
        
    existingParty = discord.utils.get(guild.channels, name = "-".join(partyName)) #checks if there is already a channel with the party name
    i=1 #holds number of duplicate channels

    if(existingParty):
        partyName.append(f"{i}")
        existingParty = discord.utils.get(guild.channels, name = "-".join(partyName))

        while existingParty: #if there are existing party names, keep on adding numbers until an open name is found
            i+=1
            partyName[nameLen] = str(i)
            existingParty = discord.utils.get(guild.channels, name = "-".join(partyName))

        pname = "-".join(partyName)

        message = f"Party name already exists, created new channel with name: **{pname}**"
    else:
        message = f"**{pname}** party created!"

    rcategory = discord.utils.get(ctx.guild.categories, name="RUBICON PARTIES") #get rubicon parties category object
    if not rcategory:
        await guild.create_category("RUBICON PARTIES") #creates category for rubicon parties
        rcategory = discord.utils.get(ctx.guild.categories, name="RUBICON PARTIES")

    await guild.create_text_channel(f"{pname}", category=rcategory) #creates channel
    channel = discord.utils.get(guild.channels, name = f"{pname}") #gets channel just created
    chanID = channel.id

    #formatting
    message = message + f"\nhere: <#{chanID}>"

    embed=discord.Embed(title="", description="", color=0x109319)

    # Add author, thumbnail, fields, and footer to the embed
    embed.set_author(name=pname, icon_url=ctx.author.avatar_url)

    embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRr36wnkIue62uS_ScvqQaYc0e3VAR-IJrVPA&usqp=CAU")
 
    embed.add_field(name="Members", value="WIP", inline=True)
    embed.add_field(name="Creator", value=ctx.author.display_name, inline=True)

    embed.timestamp = datetime.datetime.utcnow()


    embed.set_footer(text="⚔️ to join, ☠️ to delete party \u200b")

    await ctx.send(message)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("⚔️")
    await msg.add_reaction("☠️")


@bot.command(name="delete-parties", help="deletes all active parties ONLY in RUBICON PARTIES category and the category itself")
@commands.has_permissions(administrator=True)
async def deleteParties(ctx):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name = "RUBICON PARTIES") #gets category name
    for channel in category.channels:
        await channel.delete()
    
    await category.delete()
    await ctx.send("Deleted RUBICON PARTIES category and all channels under it")

@bot.event
async def on_reaction_add(reaction, user):
    emoji = reaction.emoji

    if user.bot:
        return

    if emoji == "⚔️":
        print("sword")
        print(reaction.message.id)
        #if(reaction.message.id == ):

    elif emoji == "☠️":
        print("death")
    else:
        return


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