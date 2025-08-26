import discord
from discord.ext import commands
import os
import logging
from random import choice

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MyBot

logger = logging.getLogger(__name__)
'''
Setup các event có liên quan đến user
'''
BOT_CHANNEL = 1389554769634398299

async def upgradeChat(bot : "MyBot", level: int, id: int, message : discord.Message | None = None):
    if message is None: # Default message on bot channel
        cha = bot.get_channel(BOT_CHANNEL)
        if isinstance(cha, discord.TextChannel):
            await cha.send(f"Chúc mừng <@{id}> vừa lên cấp {level}", delete_after=60)
    else:
        await message.channel.send(f"Chúc mừng <@{id}> vừa lên cấp {level}", delete_after=60)
    
def setup_event(bot : "MyBot"):
    @bot.event
    async def on_member_join(member : discord.Member):
        try:
            if member.bot:
                return
            logger.info("Member joined: %s", member)
            bot.data.addUser(member.id, member.name, member.display_name)
        except Exception as e:
            logger.error('Something wrong with on_member_join')
            logger.error(e)
        
    @bot.event
    async def on_member_remove(member : discord.Member):
        try:
            if member.bot:
                return
            logger.info("Member REMOVE: %s", member)
            bot.data.deleteUser(member.id)
        except Exception as e:
            logger.error('Something wrong with on_member_remove')
            logger.error(e)
    
    @bot.event
    async def on_message(message : discord.Message):
        try:
            if message.author.bot:
                return
            logger.info("Message: %s", message.content)
            if message.channel.id != BOT_CHANNEL:
                val = bot.data.addMessage(message.author.id)
                if val:
                    await upgradeChat(bot, val, message.author.id, message)
            await bot.process_commands(message)
        except Exception as e:
            logger.error('Something wrong with on_message')
            logger.error(e)
    
    @bot.event
    async def on_voice_state_update(member : discord.Member, before, after):
        try:
            if member.bot:
                return
            if before.channel is None and after.channel is not None:
                logger.info("Member joined voice channel: %s", member)
                bot.data.updateVoice(member.id, True)
            elif before.channel is not None and after.channel is None:
                logger.info("Member left voice channel: %s", member)
                val = bot.data.updateVoice(member.id, False)
                if val:
                    await upgradeChat(bot, val, member.id)
        except Exception as e:
            logger.error('Something wrong with on_voice_state_update')
            logger.error(e)
    
    @bot.event
    async def on_reaction_add(reaction : discord.Reaction, user: discord.User):
        try:
            if user.bot:
                return
            logger.info("Member react: %s", user)
            val = bot.data.addReaction(user.id, True)
            if val:
                await upgradeChat(bot, val, user.id)
        except Exception as e:
            logger.error('Something wrong with on_reaction_add')
            logger.error(e)
    
    @bot.event
    async def on_reaction_remove(reaction : discord.Reaction, user):
        try:
            if user.bot:
                return
            logger.info("Member remove react: %s", user)
            bot.data.addReaction(user.id, False)
        except Exception as e:
            logger.error('Something wrong with on_reaction_remove')
            logger.error(e) 