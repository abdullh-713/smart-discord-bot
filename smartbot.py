import discord
from discord.ext import commands
from discord import app_commands
import os

# إعدادات intents
intents = discord.Intents.default()
intents.message_content = True

# إنشاء البوت
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة العملات OTC
OTC_SYMBOLS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC",
    "MAD/USD OTC", "USD/RUB OTC", "USD/EGP OTC"
]

# قائمة الفريمات الزمنية
TIMEFRAMES = ["S5", "S10", "S15", "M1", "M2", "M3"]

# قائمة مدد الصفقات
DURATIONS = ["15s", "30s", "1m", "2m", "3m"]

# تخزين اختيارات المستخدم مؤقتًا
user_choices = {}

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# تشغيل البوت باستخدام التوكن من متغير البيئة
bot.run(os.getenv("TOKEN"))
