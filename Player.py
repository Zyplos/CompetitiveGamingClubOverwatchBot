import sys
import math 

class Player:

    def __init__(self, name, battletag, discordId, role, beginSR, peakSR, newSR):
        self.__Name = name
        self.__Battletag = battletag
        self.__discordId = discordId
        self.__Role = role
        self.__BeginSR = beginSR
        self.__PeakSR = peakSR
        self.__NewSR = newSR

    #Getters & Setters
    def getName(self):
        return self.__Name

    def setName(self, name):
        self.__Name = name

    def getBattletag(self):
        return self.__Battletag

    def setBattletag(self, battletag):
        self.__Battletag = battletag

    def getdiscordId(self):
        return self.__discordId

    def setdiscordId(self, discordId):
        self.__discordId = discordId

    def getRole(self):
        return self.__Role

    def setRole(self, role):
        self.__Role = role

    def getBeginSR(self):
        return self.__BeginSR

    def setBeginSR(self, beginSR):
        self.__BeginSR = beginSR

    def getPeakSR(self):
        return self.__PeakSR

    def setPeakSR(self, peakSR):
        self.__PeakSR = peakSR

    def getNewSR(self):
        return self.__NewSR

    def setNewSR(self, newSR):
        self.__NewSR = newSR

    # Methods
    def getImprovement(self):
        """
        Calculates the overall improvement relative to Peak SR and rank
        """
        if (self.__PeakSR == 0 or self.__NewSR < 0):
            return -sys.maxsize

        exponent = 1.075
        rankFactor = 1

        if (self.__NewSR >= 4200):
            rankFactor = 2.5
        elif (self.__NewSR >= 4000):
            rankFactor = 2
        elif (self.__NewSR >= 3750):
            rankFactor = 1.75
        elif(self.__NewSR >= 3500):
            rankFactor = 1.5
        elif(self.__NewSR >= 3250):
            rankFactor = 1.25

        ratio = self.__BeginSR / self.__PeakSR
        improvement = ratio * (self.getRawSRDiff()**exponent) * rankFactor

        return improvement.real

    def getRawSRDiff(self):
        # Calculates Raw SR Improvement

        return self.__NewSR - self.__BeginSR
