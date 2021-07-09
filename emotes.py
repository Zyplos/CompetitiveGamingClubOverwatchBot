class Emotes():
    def __init__(self):
        self.owEmoteDict = {
            "bronze": "<:owBronzeRank:790364925721313280>",
            "silver": "<:owSilverRank:790364926061445160>",
            "gold": "<:owGoldRank:790364925880827954>",
            "platinum": "<:owPlatinumRank:790364925901799464>",
            "diamond": "<:owDiamondRank:790364925746479114>",
            "masters": "<:owMastersRank:790364925922246696>",
            "grandmasters": "<:owGrandmastersRank:790364925863919626>",
            "tank": "<:owTank:790364925939286036>",
            "damage": "<:owDamage:790364925436362784>",
            "support": "<:owSupport:790364925952131113>",
        }

    def between(self, num, minNum, maxNum):
        return num >= minNum and num <= maxNum

    def getRoleEmote(self, role):
        return self.owEmoteDict[role]

    def getRankEmote(self, sr):
        if (not sr):
            return "❌"

        if (self.between(sr, 0, 1500)):
            return self.owEmoteDict["bronze"]
        elif (self.between(sr, 1500, 1999)):
            return self.owEmoteDict["silver"]
        elif (self.between(sr, 2000, 2499)):
            return self.owEmoteDict["gold"]
        elif (self.between(sr, 2500, 2999)):
            return self.owEmoteDict["platinum"]
        elif (self.between(sr, 3000, 3499)):
            return self.owEmoteDict["diamond"]
        elif (self.between(sr, 3500, 3999)):
            return self.owEmoteDict["masters"]
        elif (self.between(sr, 4000, 5000)):
            return self.owEmoteDict["grandmasters"]
