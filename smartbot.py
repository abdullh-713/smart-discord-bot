import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن من المتغير البيئي
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready and logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# يمكنك إضافة المزيد من الأوامر هنا

bot.run(TOKEN)
