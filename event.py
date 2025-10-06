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
            logger.info("Message: %s:%s",message.author, message.content)
            if message.channel.id != BOT_CHANNEL:
                bot.data.addMessage(message.author.id)
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
                bot.data.updateVoice(member.id, False)
        except Exception as e:
            logger.error('Something wrong with on_voice_state_update')
            logger.error(e)
    
    @bot.event
    async def on_reaction_add(reaction : discord.Reaction, user: discord.User):
        try:
            if user.bot:
                return
            logger.info("Member react: %s", user)
            bot.data.addReaction(user.id, True)
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