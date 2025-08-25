import json
import os
from datetime import datetime
from typing import Literal

'''
    data.json
    {
        "id": {
            "NAME": str,
            "FIRST_UPDATE": datetime,
            "LAST_REACT": datetime,
            "LAST_REMINDED": datetime,
            "EXP": int,
            "LEVEL": int,
            "MESSAGE": int, # Số tin nhắn
            "VOICE": int, #Số phút người dùng voice
            "REACTION": int #Số lần reaction
        }
    }
'''

MESSAGE_EXP = 2 #per message
REACTION_EXP = 5 #per reaction
VOICE_EXP = 1 #per minute

BASE_EXP = 100
ADD_EXP = 25

def expToLevel(exp):
    level = 1
    expLv = BASE_EXP
    while exp >= expLv:
        level += 1
        exp -= expLv
        expLv += ADD_EXP
    return level

def levelToExp(level):
    #Amount of exp needed for that level
    return BASE_EXP * (level - 1) + ADD_EXP * (level - 1) * level // 2

class Data:
    def __init__(self, folder = 'data.json'):
        self.folder = folder
        if os.path.exists(folder):
            self.loadJson()
        else:
            self.data = {}
            self.saveJson()
    
    def loadJson(self):
        with open(self.folder, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def saveJson(self):
        with open(self.folder, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
        
    def getData(self):
        return self.data
    
    def getScoreboard(self):
        board = sorted(self.data.items(), key=lambda x: x[1]["EXP"], reverse=True)
        res = {}
        oldExp = board[0][1]["EXP"]
        rank = 1
        for i in board:
            if i[1]["EXP"] != oldExp:
                rank += 1
                oldExp = i[1]["EXP"]
            res[i[0]] = ({
                "NAME": i[1]["NAME"],
                "LEVEL": i[1]["LEVEL"],
                "EXP": i[1]["EXP"],
                "RANK": rank
            })
        return res

    def getRank(self, id):
        id = str(id)
        return self.getScoreboard()[id]["RANK"]
    
    def getUser(self, id):
        id = str(id)
        user = self.data[id]
        user["LEVEL_EXP"] = BASE_EXP + ADD_EXP * (user["LEVEL"] - 1)
        user["NOW_EXP"] = user["EXP"] - levelToExp(user["LEVEL"])
        user["RANK"] = self.getRank(id)
        return user

    def verifyData(self, users):
        '''
        users: [(id, name), ...]
        '''
        for id, name in users:
            self.addUser(id, name)
            self.updateName(id, name)
        ids = set(str(i[0]) for i in users)
        for id in self.data.keys():
            if id not in ids:
                self.deleteUser(id)
    
    def addUser(self, id, name):
        id = str(id)
        if id in self.data.keys():
            return
            
        self.data[id] = {
            "NAME": name,
            "FIRST_UPDATE": datetime.now().strftime("%Y-%m-%d"),
            "LAST_REACT": datetime.now().strftime("%Y-%m-%d"),
            "LAST_REMINDED": datetime.now().strftime("%Y-%m-%d"),
            "EXP": 0,
            "LEVEL": 1,
            "MESSAGE": 0,
            "VOICE": 0,
            "VOICE_JOIN_TIME": 0,
            "REACTION": 0
        }
        
    def checkUser(self, id):
        id = str(id)
        if not id in self.data:
            self.addUser(id, "SOMETHING_WENT_WRONG")
    
    def updateName(self, id, name):
        id = str(id)
        self.data[id]["NAME"] = name
        
    def deleteUser(self, id):
        id = str(id)
        del self.data[id]
        self.saveJson()
    
    def updateLast(self, id):
        id = str(id)
        self.checkUser(id)
        self.data[id]["LAST_REACT"] = datetime.now().strftime("%Y-%m-%d")
        self.data[id]["LAST_REMINDED"] = datetime.now().strftime("%Y-%m-%d")
        self.data[id]["LEVEL"] = expToLevel(self.data[id]["EXP"])
        self.saveJson()
    
    def addMessage(self, id):
        id = str(id)
        self.checkUser(id)
        self.data[id]["MESSAGE"] += 1
        self.data[id]["EXP"] += MESSAGE_EXP
        self.updateLast(id)
    
    def addReaction(self, id, add = True):
        id = str(id)
        self.checkUser(id)
        self.data[id]["REACTION"] += 1 if add else -1
        self.data[id]["EXP"] += REACTION_EXP if add else -REACTION_EXP
        self.updateLast(id)
    
    def updateVoice(self, id, join):
        id = str(id)
        self.checkUser(id)
        if join:
            # Lưu timestamp chính xác đến giây
            self.data[id]["VOICE_JOIN_TIME"] = datetime.now().isoformat(timespec="seconds")
        else:
            # Parse lại timestamp
            join_time = datetime.fromisoformat(self.data[id].get("VOICE_JOIN_TIME", 0))
            voice_minutes = abs(int((datetime.now() - join_time).total_seconds() // 60))
            if voice_minutes < 60 * 72: #Voice 3 ngày => Vô lý
                self.data[id]["VOICE"] += voice_minutes
                self.data[id]["EXP"] += voice_minutes * VOICE_EXP
        self.updateLast(id)
    
    def getWarn(self, id):
        id = str(id)
        self.checkUser(id)
        self.data[id]["LAST_REMINDED"] = datetime.now().strftime("%Y-%m-%d")

        self.saveJson()
