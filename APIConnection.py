import requests
import json
from Player import Player
from urllib.parse import urlparse


class APIConnection:
    @staticmethod
    def getGameBattleTeam(url):
        """
        Call's GameBattle's internal API to get team member data given a team url.
        """

        # https://gamebattles.majorleaguegaming.com/pc/overwatch/team/34994979
        urlObj = urlparse(url)
        strippedPath = urlObj.path.rstrip("/")
        teamID = strippedPath[strippedPath.rfind("/") + 1:]

        response = requests.get(f"https://gb-api.majorleaguegaming.com/api/web/v1/team-members-extended/team/{teamID}")
        data = json.loads(response.text)

        return data

    @staticmethod
    def getUpdatedSR(player):
        """
        The method makes a call to the API to get up-to-date data, then returns the current SR of the player
        """

        if player != None:
            # get btag
            btag = player.getBattletag().split('#')
            response = APIConnection.SendRequest(btag)
            if response != None:
                return APIConnection.__ParseResponse(player, response)
            else:
                return -500

        else:
            print('getUpdatedSR(): player is null')
            return -99

    @staticmethod
    def SendRequest(battletag):
        # form & send request, then return response
        url = f'https://ow-api.com/v1/stats/pc/us/{battletag[0]}-{battletag[1]}/profile'
        response = requests.get(url)

        # check if the response code is OK
        if(response.status_code == 200):
            return response.text
        else:
            print('SendRequest() has returned ' + str(response.status_code))
            return None

    @staticmethod
    def __ParseResponse(player, response):
        # convert response to json
        data = json.loads(response)

        # get the rank of the player in their role, if it exists
        if data != None:
            if data['private'] == False:
                if data['rating'] != 0:
                    for item in data['ratings']:
                        if item['role'] == player.getRole():
                            return item['level']
                    print('ParseResponse(): ' + player.getBattletag() + ' is unranked in their role ' + player.getRole() + '.')
                    return -3
                else:
                    print('ParseResponse(): ' + player.getBattletag() + ' did not do any placements.')
                    return -2
            else:
                print('ParseResponse(): ' + player.getBattletag() + ' has a private profile.')
                return -1


"""Driver testing code
#test that it works
assert APIConnection.getUpdatedSR(Player('Kevin', 'SparkRush#1938', 'discord', 'support', 3500, 3600, 3550)) >= 0, "Should be positive"

#test private profile
assert APIConnection.getUpdatedSR(Player('Jakub', 'Colaguypepsi#1309', 'discord', 'tank', 3500, 3600, 3550)) == -1, "Should be private"

#test unranked
assert APIConnection.getUpdatedSR(Player('Wael', 'Shenanigans#21340', 'discord', 'support', 3500, 3600, 3550)) == -2, "Should be unranked for all roles"

#test unranked in their role
assert APIConnection.getUpdatedSR(Player('Kevin', 'techtank#11528', 'discord', 'damage', 3500, 3600, 3550)) == -3, "Should be unranked in their role"
"""


"""
--ERROR CODES--
>=0 is correct SR
-1 is private profile
-2 is unranked this season
-3 is unranked in their role within the team
-98 is no records
-99 is internal error
-500 is API error
"""
