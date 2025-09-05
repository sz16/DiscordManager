import discord
from datetime import datetime
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MyBot

logger = logging.getLogger(__name__)

channelID = 1389554769634398299
serverID = 760008091827306498

def setup_task(bot: "MyBot"):
    async def chat(message):
        channel = bot.get_channel(channelID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)
    
    @tasks.loop(minutes=10)
    async def check():
        logger.debug("Start check user in-server")
        data = bot.data.getData()
        # --- Check user valid
        server = bot.get_guild(serverID)
        if server is None:
            logger.error("Server is None")
            return
        bot.data.verifyData(list((str(i.id), i.name, i.display_name) for i in server.members if i.bot == False))
        
        tz_vn = ZoneInfo("Asia/Ho_Chi_Minh")
        now_vn = datetime.now(tz_vn)
        
        if now_vn.hour != 19:
            logger.debug("This is not 7pm, stop auto check")
            return
        # --- Check user last react
        logger.debug("Auto check user react")
        for id, user in data.items():
            #Check amount of day from LAST_REACT to today
            delta = (datetime.now() - datetime.strptime(user['TIMELINE']["LAST_REACT"], '%Y-%m-%d')).days
            #print(user["NAME"], delta)
            if (datetime.now() - datetime.strptime(user['TIMELINE']['LAST_REMINDED'], '%Y-%m-%d')).days == 0:
                continue
            if delta == 14:
                await chat(f"<@{id}> Hmmm, bro chưa hoạt động được 14 ngày rồi. Sớm quay lại server nhá")
                bot.data.getWarn(id)
            elif delta != 0 and delta % 24 == 0:
                await chat(f"<@{id}> Chưa hoạt động gì được {delta} ngày rồi. Chúng tôi sẽ xem xét việc kick bạn")
                bot.data.getWarn(id)

    check.start()