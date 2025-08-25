import os
import logging
import setup_log
from dotenv import load_dotenv
from data import Data

# --- Setup keep_alive
import keep_alive
keep_alive.keep_alive()

# --- Setup logging TRƯỚC KHI import discord ---
setup_log.setup_logging()
logger = logging.getLogger(__name__)

# --- Load token ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN is None:
    raise Exception("Missing DISCORD_BOT_TOKEN in .env file")

# --- Import discord sau khi đã setup log ---
import discord
from discord.ext import commands

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.voice_states = True

class MyBot(commands.Bot):
    data: Data
bot = MyBot(command_prefix="c!", intents=intents, help_command=None)
bot.data = Data()

    
# --- Setup event and commands
import event
import command
import task
event.setup_event(bot)
command.setup_command(bot)

@bot.event
async def on_ready():
    logger.info("Bot is ready as %s", bot.user)
    task.setup_task(bot)
    
bot.run(TOKEN)
