import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

'''
    data.json
    {
        "id": {
            "NAME": str,
            "DISPLAY": str,
            "TIMELINE":{
                "FIRST_UPDATE": datetime,
                "LAST_REACT": datetime,
                "LAST_REMINDED": datetime,
            },
            "ACTION":{
                "MESSAGE": int, # Số tin nhắn
                "VOICE_TIME": int, #Số phút người dùng voice
                "REACTION": int #Số lần reaction
            }
            "LVL":{
                "LEVEL": int, #Level hiện tại
                "EXP": int, #Số exp hiện tại
                "LEVEL_EXP": int, #Số exp cần để lên level tiếp theo
                "TOTAL_EXP": int, #Tổng số exp
            }
        }
    }
'''
if True: #Setup typing
    from typing import TypedDict
    from datetime import datetime

    class TimelineDict(TypedDict):
        FIRST_UPDATE: str
        LAST_REACT: str
        LAST_REMINDED: str

    class ActionDict(TypedDict):
        MESSAGE: int       # số tin nhắn
        VOICE_TIME: int    # số phút voice
        REACTION: int      # số lần reaction

    class LevelDict(TypedDict):
        LEVEL: int
        EXP: int
        LEVEL_EXP: int
        TOTAL_EXP: int

    class UserData(TypedDict):
        NAME: str
        DISPLAY: str
        TIMELINE: TimelineDict
        ACTION: ActionDict
        LVL: LevelDict

    # dict chính: id (chuỗi) -> UserData
    DataJson = dict[str, UserData]

MESSAGE_EXP = 2 #per message
REACTION_EXP = 5 #per reaction
VOICE_EXP = 1 #Minute per exp

BASE_EXP = 100
ADD_EXP = 25

class Data:
    def __init__(self, folder = 'data.json'):
        self.folder = folder
        self.inVoice : dict[str, datetime] = {}
        if os.path.exists(folder):
            self.loadJson()
        else:
            self.data = {}
            self.saveJson()
    
    def loadJson(self):
        with open(self.folder, 'r', encoding='utf-8') as f:
            self.data : DataJson = json.load(f)
            
    def updateNewData(self, newdata):
        self.data = newdata
        self.saveJson()

    def saveJson(self):
        with open(self.folder, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        
    def getData(self) -> DataJson:
        return json.loads(json.dumps(self.data))
    
    def getScoreboard(self):
        board = sorted(self.data.items(), key=lambda x: x[1]['LVL']["TOTAL_EXP"], reverse=True)
        res = {}
        oldExp = board[0][1]["LVL"]["EXP"]
        rank = 1
        for i in board:
            if i[1]["LVL"]["EXP"] != oldExp:
                rank += 1
                oldExp = i[1]["LVL"]["EXP"]
            res[i[0]] = ({
                "NAME": i[1]["NAME"],
                "DISPLAY": i[1]["DISPLAY"],
                "LEVEL": i[1]["LVL"]["LEVEL"],
                "EXP": i[1]["LVL"]["EXP"],
                "RANK": rank
            })
        return res

    def getRank(self, id):
        id = str(id)
        return self.getScoreboard()[id]["RANK"]
    
    def getUser(self, id) -> dict[str, str]:
        id = str(id)
        user = self.data[id]
        res = {}
        res["NAME"] = user["NAME"]
        res["LEVEL"] = user["LVL"]["LEVEL"]
        res["NOW_EXP"] = user["LVL"]["EXP"]
        res["LEVEL_EXP"] = user["LVL"]["LEVEL_EXP"]
        res["RANK"] = self.getRank(id)
        return res

    def verifyData(self, users):
        '''
        users: [(id, name, display_name), ...]
        '''
        for id, name, display_name in users:
            self.addUser(id, name, display_name)
            self.updateName(id, name, display_name)
        need_delete = []
        ids = set(str(id[0]) for id in users)
        for id in self.data.keys():
            if id not in ids:
                need_delete.append(id)
        for id in need_delete:
            logger.debug(f"Delete user {id}")
            self.deleteUser(id)
    
    def addUser(self, id, name, display_name):
        id = str(id)
        if id in self.data.keys():
            return
        logger.debug(f"Add user {id}")
        self.data[id] = {
            "NAME": name,
            "DISPLAY": display_name,
            "TIMELINE": {
                "FIRST_UPDATE": datetime.now().strftime("%Y-%m-%d"),
                "LAST_REACT": datetime.now().strftime("%Y-%m-%d"),
                "LAST_REMINDED": datetime.now().strftime("%Y-%m-%d"),
            },
            "ACTION": {
                "MESSAGE": 0,
                "VOICE_TIME": 0,
                "REACTION": 0 
            },
            "LVL": {
                "LEVEL": 1,
                "EXP": 0,
                "LEVEL_EXP": BASE_EXP,
                "TOTAL_EXP": 0,
            }
        }
        
    def checkUser(self, id):
        id = str(id)
        if not id in self.data:
            self.addUser(id, "SOMETHING_WENT_WRONG", "SOMETHING_WENT_WRONG")
    
    def updateName(self, id, name, display_name):
        id = str(id)
        self.data[id]["NAME"] = name
        self.data[id]["DISPLAY"] = display_name
        
    def deleteUser(self, id):
        id = str(id)
        if not id in self.data:
            return
        del self.data[id]
        self.saveJson()
    
    def updateLevel(self, id, amount):
        id = str(id)
        self.checkUser(id)
        
        userlvl = self.data[id]["LVL"]
        userlvl["EXP"] += amount
        if userlvl["EXP"] < 0:
            userlvl["EXP"] = 0
        userlvl["TOTAL_EXP"] += amount
        
        upgraded = False
        while userlvl["EXP"] >= userlvl["LEVEL_EXP"]:
            userlvl["EXP"] -= userlvl["LEVEL_EXP"]
            userlvl["LEVEL"] += 1
            userlvl["LEVEL_EXP"] += ADD_EXP
            upgraded = True
        
        self.data[id]["TIMELINE"]["LAST_REACT"] = datetime.now().strftime("%Y-%m-%d")
        self.data[id]["TIMELINE"]["LAST_REMINDED"] = datetime.now().strftime("%Y-%m-%d")
        self.saveJson()
        if upgraded and userlvl["LEVEL"] % 10 == 0:
            return userlvl["LEVEL"]
        else:
            return 0
    
    def addMessage(self, id):
        id = str(id)
        self.checkUser(id)
        self.data[id]["ACTION"]["MESSAGE"] += 1
        return self.updateLevel(id, MESSAGE_EXP)
    
    def addReaction(self, id, add = True):
        id = str(id)
        self.checkUser(id)
        self.data[id]["ACTION"]["REACTION"] += 1 if add else -1
        return self.updateLevel(id, REACTION_EXP if add else -REACTION_EXP)
    
    def updateVoice(self, id, join):
        id = str(id)
        self.checkUser(id)
        if join:
            self.inVoice[id] = datetime.now()
            return 0
        else:
            if id in self.inVoice:
                inVoiceTime = (datetime.now() - self.inVoice[id]).seconds // 60
                self.data[id]["ACTION"]["VOICE_TIME"] += inVoiceTime
                del self.inVoice[id]
                return self.updateLevel(id, inVoiceTime // VOICE_EXP)
                
    def getWarn(self, id):
        id = str(id)
        self.checkUser(id)
        self.data[id]["TIMELINE"]["LAST_REMINDED"] = datetime.now().strftime("%Y-%m-%d")

        self.saveJson()

    def dataSync(self, cloud: DataJson):
        ans = {}
        local = self.getData()
        # Lấy tất cả ID xuất hiện trong cả 2 dict
        all_ids = set(local.keys()) | set(cloud.keys())

        for uid in all_ids:
            if uid in local and uid not in cloud:
                ans[uid] = local[uid]
                logger.debug(f"New user {uid} from cloud")
            elif uid in cloud and uid not in local:
                ans[uid] = cloud[uid]
                logger.debug(f"New user {uid} from local")
            else:
                # Cả hai đều có uid → cần so sánh theo thứ tự ưu tiên
                a = local[uid]
                b = cloud[uid]

                # --- Ưu tiên theo thứ tự: FIRST_UPDATE sớm hơn → LAST_REMINDED mới hơn → TOTAL_EXP cao hơn ---
                fa = datetime.fromisoformat(a["TIMELINE"]["FIRST_UPDATE"])
                fb = datetime.fromisoformat(b["TIMELINE"]["FIRST_UPDATE"])
                la = datetime.fromisoformat(a["TIMELINE"]["LAST_REMINDED"])
                lb = datetime.fromisoformat(b["TIMELINE"]["LAST_REMINDED"])
                ea = a["LVL"]["TOTAL_EXP"]
                eb = b["LVL"]["TOTAL_EXP"]

                if fa < fb:
                    ans[uid] = a
                    logger.debug(f"Update user {uid} from cloud because of FIRST_UPDATE")
                elif fa > fb:
                    ans[uid] = b
                    logger.debug(f"Update user {uid} from local because of FIRST_UPDATE")
                else:
                    # FIRST_UPDATE bằng nhau → xét LAST_REMINDED (cái mới hơn thắng)
                    if la > lb:
                        ans[uid] = a
                        logger.debug(f"Update user {uid} from cloud because of LAST_REMINDED")
                    elif la < lb:
                        ans[uid] = b
                        logger.debug(f"Update user {uid} from local because of LAST_REMINDED")
                    else:
                        # Cuối cùng, chọn TOTAL_EXP cao hơn
                        if ea >= eb:
                            ans[uid] = a
                            logger.debug(f"Update user {uid} from cloud because of TOTAL_EXP")
                        else:
                            ans[uid] = b
                            logger.debug(f"Update user {uid} from local because of TOTAL_EXP")
        
        self.updateNewData(ans)
