import discord
from discord.ext import commands
import json
from APIConnection import APIConnection
from emotes import Emotes
from tespateam import TespaTeam


class Tespa(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.emotes = Emotes()

    def getHighestRole(self, ratingsData):
        return max(ratingsData, key=lambda r: r["level"])["role"]

    # NOTE the following line takes care of usernames with unicode in them (ex: Phönix#11157)
    # the API returns them formatted wrong (PhÃ¶nix#11157)
    # encoding to 'windows-1252' instead of 'ascii' just works
    def unicodeFix(self, str):
        return str.encode('windows-1252').decode("utf-8")

    @commands.command(aliases=["tespa"])
    @commands.guild_only()
    async def _tespa(self, ctx, url):
        await ctx.send('Getting team profile...')
        data = APIConnection.getGameBattleTeam(url)
        team = TespaTeam()
     
        embed = discord.Embed(
            title="__Team Information__",
            color=16746752,
        )
        if "body" in data:
            for teamMember in data["body"]:
                currentGamerTag = teamMember["teamMember"]["gamertag"]
                print('teamMember: ' + currentGamerTag)

                if "userGamertag" in teamMember:
                    currentGamerTag = teamMember["userGamertag"]["gamertag"]

                embedName = ""
                if(teamMember["teamMember"]["status"] != "ELIGIBLE"):
                    embedName += " (⚠️ Not Eligible) "
                
                # GameBattles assigns ID 3 to BattleTag gamertags
                if (currentGamerTag):
                    #NOTE I left the rest of the code unchanged except for these couple of lines for the future in case we need to change it
                    #fixedGamerTag = self.unicodeFix(currentGamerTag)
                    fixedGamerTag = currentGamerTag
                    battleTag = fixedGamerTag

                    btag = battleTag.split('#')
                    
                    response = APIConnection.SendRequest(btag)
                    embedName += battleTag

                    if response != None:
                        currentPlayer = json.loads(response)

                        output = ""

                        if (currentPlayer["private"]):
                            output = "🔒 Private profile."
                            output += "\n"
                        elif (not currentPlayer["ratings"]):
                            output = "❌ No placements."
                            output += "\n"
                        else:
                            for roleData in currentPlayer["ratings"]:
                                output += self.emotes.getRoleEmote(roleData["role"])
                                output += " "
                                output += self.emotes.getRankEmote(roleData["level"])
                                output += " "
                                output += str(roleData["level"])

                                if(self.getHighestRole(currentPlayer["ratings"]) == roleData["role"]):
                                    output += " ⭐"
                                    team.addPlayer(roleData["level"], roleData["role"])

                                output += "\n"
                        output += f"[View Profile ↗️](https://playoverwatch.com/en-us/career/pc/{battleTag.replace('#', '-')})"

                        embed.add_field(name=embedName, value=output, inline=False)

                    else:
                        embed.add_field(name=embedName, value="❔ Couldn't get player data.", inline=False)
                else:
                    embedName += teamMember["teamMember"]["guid"]
                    embed.add_field(name=embedName, value="❔❔ This GameBattles user doesn't have a valid GamerTag.", inline=False)

            topAvg = team.getTopSixAverage()
            overallAvg = team.getTeamAverage()

            output = ""
            output += "Top 6 (top 2 per role): "
            output += self.emotes.getRankEmote(topAvg)
            output += " "
            if(topAvg > 0):
                output += str(topAvg)
            output += "\n"
            output += "Overall team: "
            output += self.emotes.getRankEmote(overallAvg)
            output += " "
            if(overallAvg > 0):
                output += str(overallAvg)
            embed.insert_field_at(index=0, name='Team Average', value=output, inline=False)
        else:
            embed.add_field(name="Error.", value="❔ Couldn't get team data. Make sure the link is the team's page.", inline=False)
        
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Tespa(client))
