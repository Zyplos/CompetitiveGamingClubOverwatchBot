import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
from Player import Player
from DatabaseConnection import DatabaseConnection
from APIConnection import APIConnection
from emotes import Emotes
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = "ow;"
DB = DatabaseConnection()
PLAYERS = DB.getAllPlayers()
PLAYERS = sorted(PLAYERS, key=lambda p: p.getImprovement(), reverse=True)
UPDATE_CHANNEL_ID = "804071646763155516"

client = commands.Bot(command_prefix=PREFIX, help_command=None)


def calculateMidnight():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    midnight = tomorrow.replace(hour=0, minute=0, second=0)
    secondsUntilMidnight = (midnight - now).total_seconds()

    return secondsUntilMidnight


def getPlayerLeader(playerList):
    return max(playerList, key=lambda p: p.getImprovement())


"""Updates the database, as well as PLAYERS"""


async def updateData(fetch):
    global PLAYERS
    global lastUpdateTime

    newPLAYERS = DB.getAllPlayers()
    

    if(fetch):
        for player in newPLAYERS:
            returnVal = APIConnection.getUpdatedSR(player)
            player.setNewSR(returnVal)
            print('updateData: ' + player.getBattletag() + ' ' + str(player.getNewSR()))
            DB.updateNewSR(player)

    # sort players by improvement rate
    lastUpdateTime = DB.getLastUpdateTime()
    newPLAYERS = sorted(newPLAYERS, key=lambda p: p.getImprovement(), reverse=True)

    currentLeader = getPlayerLeader(PLAYERS)
    newLeader = getPlayerLeader(newPLAYERS)
    
    # Send new leader update to channel
    if(currentLeader.getdiscordId() != newLeader.getdiscordId()):
        
        currentLeaderUser = await client.fetch_user(currentLeader.getdiscordId())
        newLeaderUser = await client.fetch_user(newLeader.getdiscordId())
        urlBattletag = newLeader.getBattletag().replace("#", "-")

        embed = discord.Embed(
            color=16746752
        )
        embed.set_author(
            name=f"{newLeader.getName()} ({newLeaderUser.display_name}) is now in the lead! [View ↗️]",
            url=f"https://playoverwatch.com/en-us/career/pc/{urlBattletag}/",
            icon_url=newLeaderUser.avatar_url
        )
        embed.set_footer(text=f"{currentLeader.getName()} ({currentLeaderUser.display_name}) was previously 1st.", icon_url=currentLeaderUser.avatar_url)
        
        updateChannel = await client.fetch_channel(UPDATE_CHANNEL_ID)

        await updateChannel.send(embed=embed)

    PLAYERS = newPLAYERS
    


def makeLeaderboard():
    output = ""

    index = 1
    for player in PLAYERS:
        output += f'*{index}. {player.getName()} <@{player.getdiscordId()}> ({ player.getBattletag() })*'
        output += "\n"
        if(player.getNewSR() == -3):
            output += f"❌ No placements placements in their role ({player.getRole()}) this season."
        elif (player.getNewSR() == -2):
            output += "❌ No placements this season."
        elif (player.getNewSR() == -1):
            output += "🔒 Private profile"
        elif (player.getNewSR() < 0):
            output += "❔ API Error"
        else:
            output += f'Improvement Rate: **{round(player.getImprovement())}**\nRaw SR Change: **{player.getRawSRDiff()}**'

        output += "\n\n"
        index += 1

    return output


def leaderboardEmbed(currentLeader, leaderUser):
    urlBattletag = currentLeader.getBattletag().replace("#", "-")

    embed = discord.Embed(
        title="__Improvement Leaderboard__",
        description=makeLeaderboard(),
        timestamp=DB.getLastUpdateTime() + timedelta(hours=6),
        color=16746752,
    )

    embed.set_footer(text="Updated", icon_url="https://i.imgur.com/Wm39xwq.png")
    embed.set_author(
        name=f"Currently Leading: {currentLeader.getName()} ({leaderUser.display_name}) [View ↗️]",
        url=f"https://playoverwatch.com/en-us/career/pc/{urlBattletag}/",
        icon_url=leaderUser.avatar_url
    )

    return embed


@client.event
async def on_ready():
    # ===== ONREADY EVENT
    # Initial data update
    await updateData(False)

    botGame = discord.Activity(name=f"Overwatch | {PREFIX}help", type=discord.ActivityType.competing)
    await client.change_presence(status=discord.Status.online, activity=botGame)
    print(f'{client.user} has connected to Discord.')

    # Start loop in "calculateMidnight()" seconds so it fires every 24 hours at midnight
    await asyncio.sleep(calculateMidnight())
    autoUpdateData.start()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Only Overwatch Team members can do this command in their respective channels.")


def overwatch_team_check(ctx):
    # ===== Checks if user has Overwatch Team A/B roles and if it's in the locked channels.
    # ===== Testing server: 790726191988211753, 790726770340790332, CGC Server: 223530819615064064, 674126402840297473, Board: 533067570019041330
    acceptedRoles = [790726191988211753, 790726770340790332, 223530819615064064, 674126402840297473, 533067570019041330]

    userRoles = ctx.author.roles

    roleCheck = False
    for role in userRoles:
        if role.id in acceptedRoles:
            roleCheck = True
            break

    return roleCheck


def overwatch_channels_check(ctx):
    # ===== Testing server: 787495556632412160, 790727304040677418, 790726714543177798, 790727016495185942, 791088541638983731
    # ===== CGC: 491439293739302932, 674129902957494272, 674126774011166730, 804071646763155516
    acceptedChannels = [787495556632412160, 790727304040677418, 790726714543177798, 790727016495185942, 791088541638983731, 491439293739302932, 674129902957494272, 674126774011166730, 804071646763155516]

    return ctx.channel.id in acceptedChannels


@client.command(aliases=['leaderboard', "lb"])
@commands.guild_only()
@commands.check(overwatch_team_check)
@commands.check(overwatch_channels_check)
async def _leaderboard(ctx):
    await updateData(False)
    currentLeader = getPlayerLeader(PLAYERS)
    leaderUser = await client.fetch_user(currentLeader.getdiscordId())
    await ctx.send(embed=leaderboardEmbed(currentLeader, leaderUser))


@client.command(aliases=['update'])
@commands.guild_only()
@commands.check(overwatch_team_check)
@commands.check(overwatch_channels_check)
async def _update(ctx):
    await ctx.send('Updating...')
    await updateData(True)
    currentLeader = getPlayerLeader(PLAYERS)
    leaderUser = await client.fetch_user(currentLeader.getdiscordId())
    await ctx.send(embed=leaderboardEmbed(currentLeader, leaderUser))


@client.command(aliases=['sr'])
@commands.guild_only()
async def _sr(ctx, battletag):
    await ctx.send('Getting ' + battletag + "'s profile...")
    btag = battletag.split('#')
    response = APIConnection.SendRequest(btag)
    emotes = Emotes()

    embed = discord.Embed(
        #title="__Player Profile__",
        color=16746752,
    )

    embed.set_author(
        name=f"{battletag} [View ↗️]",
        url=f"https://playoverwatch.com/en-us/career/pc/{battletag.replace('#', '-')}/",
        icon_url="https://i.imgur.com/Wm39xwq.png"
    )

    if response == None:
        embed.add_field(name="Error.", value="❔ Couldn't get player data.", inline=False)
    else:
        currentPlayer = json.loads(response)

        embed.set_author(
            name=f"{battletag} [View ↗️]",
            url=f"https://playoverwatch.com/en-us/career/pc/{battletag.replace('#', '-')}/",
            icon_url=currentPlayer["icon"]
        )

        output = ""

        if (currentPlayer["private"]):
            output = "🔒 Private profile."
        elif (not currentPlayer["ratings"]):
            output = "❌ No placements."
        else:
            for roleData in currentPlayer["ratings"]:
                output += emotes.getRoleEmote(roleData["role"])
                output += " "
                output += emotes.getRankEmote(roleData["level"])
                output += " "
                output += str(roleData["level"])
                output += "\n"

        embed.add_field(name=f'Average: {emotes.getRankEmote(currentPlayer["rating"])} {currentPlayer["rating"]}', value=output, inline=False)

    await ctx.send(embed=embed)


def _plotall():
    allBattletag = []
    allResult = []
    dateAxisAll = {}
    lastSrDict = {}
    ct = 0
    colors = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20']
    
    # Get all battletags and results
    for player in PLAYERS:
        result = DB.getRecordsByBattleTag(player.getBattletag())
        allBattletag.append(player.getBattletag())
        allResult.append(result)
        dateAxisAll[player.getBattletag()] = []

    #This is to make the graph grow dynamically. Numbers are arbiturary, may adjust later.
    maxNumDates = 0
    for results in allResult:
        maxNumDates = max(maxNumDates, len(results))
    
    plt.figure(figsize=(maxNumDates/5, 8))   

    # Plots SR improvement for each Battletag   
    for results in allResult:
        dateAxis = []
        srAxis = []

        for elem in results:
            (sr, date) = elem

            if(sr > 0):
                dateObj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                #NOTE avoid feeding strings to numpy, as it will not sort them and may give unsorted axes
                #dateFormatted = dateObj.strftime("%m/%d")
                dateAxis.append(dateObj)
                srAxis.append(sr)
    
        plt.plot(dateAxis, srAxis, color=colors[ct], label=allBattletag[ct])
        
        if len(srAxis) > 0:
            lastSrDict[f"{allBattletag[ct]}"] = srAxis[-1]  # Add Btag + last SR to dict
            dateAxisAll[allBattletag[ct]] = dateAxis
        ct += 1
    
    
    plt.title('SR Change Overview', fontstyle='oblique', fontsize='xx-large')
    plt.xlabel('Time', fontsize='large')
    plt.ylabel('SR', fontsize='large')
    #plt.legend(bbox_to_anchor=(1, 0.8, 0.2, 0.1), loc='center left',borderaxespad=0,fontsize='medium')

    # Annonate last point
    lastSrDict = dict(sorted(lastSrDict.items(), key=lambda item: item[1]))
    plotLastSr = list(lastSrDict.values())
    plotBattletag = list(lastSrDict.keys())
    
    for i in range(len(plotLastSr)):
        if i == 0:
            plt.annotate(f' {plotBattletag[i]}', (dateAxisAll[plotBattletag[i]][-1], plotLastSr[i]-20), fontsize='small', bbox=dict(boxstyle='round', fc='0.9'))  # lowest SR
        elif i == len(plotLastSr)-1:
            plt.annotate(f' {plotBattletag[i]}', (dateAxisAll[plotBattletag[i]][-1], plotLastSr[i]), fontsize='small', bbox=dict(boxstyle='round', fc='0.9'))  # highest SR

        else:
            diff_next = plotLastSr[i+1] - plotLastSr[i]
            diff_prev = plotLastSr[i] - plotLastSr[i-1]

            if (diff_next < 50) and (diff_prev < 60):
                plt.annotate(f' {plotBattletag[i]}', (dateAxisAll[plotBattletag[i]][-3], plotLastSr[i]), fontsize='small', bbox=dict(boxstyle='round', fc='0.9'))  # shifts between value inward
            elif (diff_next < 30):
                plt.annotate(f' {plotBattletag[i]}', (dateAxisAll[plotBattletag[i]][-1], plotLastSr[i]-30), fontsize='small', bbox=dict(boxstyle='round', fc='0.9'))
            else:
                plt.annotate(f' {plotBattletag[i]}', (dateAxisAll[plotBattletag[i]][-1], plotLastSr[i]), fontsize='small', bbox=dict(boxstyle='round', fc='0.9'))
    
    plt.savefig('plot.png')
    plt.clf()


@client.command(aliases=['plot'])
@commands.guild_only()
@commands.check(overwatch_team_check)
@commands.check(overwatch_channels_check)
async def _plot(ctx, arg):
    
    if arg == 'all':
        _plotall()
    else:
        arg = arg[:-1]
        arg = arg[3:]
        (battletag, result) = DB.getRecordsByDiscordId(arg)

        dateAxis = []
        srAxis = []

        for elem in result:
            (sr, date) = elem

            if(sr > 0):
                dateObj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                #dateFormatted = dateObj.strftime("%m/%d")
                dateAxis.append(dateObj)
                srAxis.append(sr)

        plt.figure(figsize=(len(dateAxis)/5, 8)) 
        plt.plot(dateAxis, srAxis)
        plt.title(battletag + "'s SR Change")
        plt.ylabel('SR')
        plt.xlabel('Time')
        #plt.ylim(2000, 4500)
        plt.savefig('plot.png')
        plt.clf()
    await ctx.send(file=discord.File('plot.png'))

# ===== Help command


@client.command(aliases=['help'])
@commands.guild_only()
async def _help(ctx):
    output = "**- ow;sr <Battletag>** : Shows SR for all roles and the average \n"
    output += " **- ow;tespa <game battles team URL>** : Shows entire team's SR for each role and profile link"
    output += "\n\n"
    output += "__Commands below only available for Overwatch Team Members__\n"
    output += " **- ow;lb or ow;leaderboard** : Shows last updated improvement leaderboard \n"
    output += " **- ow;update** : Updates and shows current improvement leaderboard \n"
    output += " **- ow;plot @DiscordTag** : Plots SR improvement graph over time \n"
    output += " **- ow;plot all** : Plots SR improvement graph over time for everyone"
    output += "\n\n"
    output += "*Leaderboard is updated automatically every 24 hours*"
    output += "\n\n"
    output += "**Devs **: <@275244327205339136>, <@204620732259368960>, <@103850885578260480>, <@226824796690841600>"

    embed = discord.Embed(
        title="__Help__",
        description=output,
        timestamp=DB.getLastUpdateTime() + timedelta(hours=6),
        color=16746752,
    )

    embed.set_footer(text="Updated", icon_url="https://i.imgur.com/Wm39xwq.png")

    await ctx.send(embed=embed)


# 86400 = 24 hours
@tasks.loop(seconds=86400)
async def autoUpdateData():
    print("=== Task loop: Updating data.")
    await updateData(True)

client.load_extension("tespa")


client.run(TOKEN)
