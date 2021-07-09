import statistics

class TespaTeam:
    def __init__(self):
        self.__damageList = []
        self.__tankList = []
        self.__supportList = []

    def addPlayer(self, sr, role):
        if role == 'damage':
            self.__damageList.append(sr)
        elif role == 'tank':
            self.__tankList.append(sr)
        elif role == 'support':
            self.__supportList.append(sr)

    def getTopSixAverage(self):
        self.__damageList.sort(reverse=True)
        self.__tankList.sort(reverse=True)
        self.__supportList.sort(reverse=True)

        team = self.__damageList[:2] + self.__tankList[:2] + self.__supportList[:2]
        print('top 6: ' + str(team))
        if team == []:
            return 0
        else: 
            return round(statistics.mean(team))

    def getTeamAverage(self):
        team = self.__damageList + self.__tankList + self.__supportList
        if team == []:
            return 0
        else: 
            return round(statistics.mean(team))