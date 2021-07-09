import sqlite3
from sqlite3 import Error
from Player import Player
import datetime
from APIConnection import APIConnection

class DatabaseConnection:
    def __init__(self):
        try:
            self.__db = sqlite3.connect('OverwatchDB.db')
        except Error as e:
            print(e)

    def getAllPlayers(self):
        # init
        playersList = []
        cursor = self.__db.cursor()

        # get list of players from database
        cursor.execute('SELECT * FROM players')
        result = cursor.fetchall()
        cursor.close()

        # construct players list
        for item in result:
            playersList.append(
                Player(item[0], item[1], item[2], item[3], item[4], item[5], None))

        # update newSR
        for player in playersList:
            newSR = self.getNewSR(player)
            if newSR == -98:
                print('getAllPlayers(): no records for ' + player.getBattletag() + '. newSR: ' + str(newSR))
                newSR = APIConnection.getUpdatedSR(player)
                player.setNewSR(newSR)
                self.updateNewSR(player) 
            else:
                player.setNewSR(newSR)
                
        return playersList

    def getNewSR(self, player):
        # init
        cursor = self.__db.cursor()

        # get the latest id for a certain btag
        sql = "SELECT newSR FROM records WHERE battletag='{}' ORDER BY id DESC".format(
            player.getBattletag())
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()

        if result != None:
            return result[0]
        else:
            print('getNewSR(): No records for ' + player.getBattletag())
            return -98

    def updateNewSR(self, player):
        # init
        cursor = self.__db.cursor()

        # get the latest id
        cursor.execute('SELECT id FROM records ORDER BY id DESC')
        result = cursor.fetchone()

        # insert command
        d = datetime.datetime.now()
        rounded = d - datetime.timedelta(microseconds=d.microsecond)
        sql = "INSERT INTO records (id,battletag,newSR,datetime) VALUES ({}, '{}', '{}', '{}')".format(
            result[0]+1, player.getBattletag(), player.getNewSR(), rounded)
        cursor.execute(sql)
        self.__db.commit()
        cursor.close()

    def getLastUpdateTime(self):
        # init
        cursor = self.__db.cursor()

        # get the latest id for a certain btag
        sql = "SELECT datetime FROM records ORDER BY id DESC"
        cursor.execute(sql)
        result = cursor.fetchone()
        # close
        cursor.close()

        if result != None:

            return datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        else:
            print('getLastUpdateTime(): cannot get time')
            return datetime.datetime.now()

        

    def getRecordsByDiscordId(self, discordId):
        # init
        cursor = self.__db.cursor()

        #get battletag from players table
        sql = "SELECT battletag FROM players WHERE discordId='{}'".format(discordId)
        cursor.execute(sql)
        result = cursor.fetchone()

        #check if battletag is found
        if result == None:
            print('getRecordsByDiscordId(): cannot find battletag for discordId ' + discordId)
            return (None, [])
        else:
             records = self.getRecordsByBattleTag(result[0])
             if records != None:
                 return (result[0], records)
             else:
                 print('getRecordsByDiscordId(): cannot find records for discordId ' + discordId)
                 return (None, [])

    def getRecordsByBattleTag(self, battletag): 
        # init
        cursor = self.__db.cursor()

        # get the latest id for a certain btag
        sql = "SELECT newSR, datetime FROM records WHERE battletag='{}'".format(battletag)
        cursor.execute(sql)
        result = cursor.fetchall()

        # close
        cursor.close()

        if result == None:
            return None
        else:
            return result

    def updateBattletag(self, oldBattletag, newBattletag):
        # init
        cursor = self.__db.cursor()

        # update players table
        sql = "UPDATE players SET battletag = '{}' WHERE battletag = '{}'".format(newBattletag, oldBattletag)
        cursor.execute(sql)
        
        #update records table
        sql = "UPDATE records SET battletag = '{}' WHERE battletag = '{}'".format(newBattletag, oldBattletag)
        cursor.execute(sql)

        # commit
        self.__db.commit()

        # close
        cursor.close()


"""Driver testing code
connection = DatabaseConnection()
connection.updateBattletag('MuckyPoo#11217', 'Dëgeneracy#1152')"""



