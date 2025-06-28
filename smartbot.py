import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تحميل المتغيرات البيئية (إذا كان .env موجود)
load_dotenv()

# جلب التوكن من المتغير البيئي المسمى TOKEN
TOKEN = os.getenv("TOKEN")

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True  # مهم لتفعيل استلام الرسائل

bot = commands.Bot(command_prefix="!", intents=intents)

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# أمر ping لاختبار البوت
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# أمر !start للترحيب
@bot.command()
async def start(ctx):
    await ctx.send("🤖 البوت شغال! مرحباً بك!")

# تشغيل البوت باستخدام التوكن من المتغير البيئي
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ لم يتم العثور على التوكن! تأكد من ضبط المتغير البيئي باسم TOKEN.")
