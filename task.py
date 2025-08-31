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
            elif delta == 24:
                await chat(f"<@{id}> Hmmm, bro chưa hoạt động gì được 24 ngày rồi. Bot sẽ xem xét việc kick các thành viên không hoạt động trong thời gian dài")
                bot.data.getWarn(id)
            elif delta == 25:
                #Kick user
                logger.info(f"Kick user {id} for not active for 25 days")
                member = server.get_member(int(id))
                if member is None:
                    logger.error("Member is None")
                    continue
                bot.data.getWarn(id)
                try:
                    await chat(f"<@{id}> Dựa vào lịch sử được ghi nhận bởi bot, chúng tôi nhận thấy bạn đã không hoạt động trong 25 ngày. Vì vậy, bot sẽ thực hiện kick người dùng để giúp server không bị loãng thành viên.")
                    await member.kick(reason="Not active for 25 days")
                    logger.info(f"Kick user {member} for not active for 25 days")
                except discord.Forbidden:
                    await chat(f"Có lỗi đã xảy ra. Bot không đủ quyền hạn để thực hiện kick user này.")
                except Exception as e:
                    logger.error(e)


    check.start()    



