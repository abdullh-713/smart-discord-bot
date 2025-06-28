import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن من البيئة (أو يمكنك وضع التوكن يدويًا إن لم تستخدم .env)
TOKEN = "MTM0ODU3Mj...kAkk0"  # <-- ضع التوكن الجديد الكامل هنا

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

# يمكنك إضافة أوامر أخرى هنا

bot.run(TOKEN)
