import discord
from discord.ext import commands
from discord import app_commands

# إعداد intents للسماح بقراءة الرسائل
intents = discord.Intents.default()
intents.message_content = True

# إعداد البوت
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة العملات OTC
OTC_SYMBOLS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "MAD/USD OTC",
    "USD/RUB OTC", "USD/EGP OTC"
]

# الفريمات الزمنية المتوفرة
TIMEFRAMES = ["S5", "S10", "S15", "M1", "M2", "M3", "M5"]

# مدد الصفقات المتاحة
DURATIONS = ["15s", "30s", "1m", "2m", "3m"]

# تخزين اختيارات المستخدم مؤقتًا
user_choices = {}

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# أمر /start لبدء استخدام البوت
@bot.tree.command(name="start", description="ابدأ استخدام البوت الآن")
async def start_command(interaction: discord.Interaction):
    await interaction.response.send_message("🎯 مرحبًا! أرسل صورة من الشارت أو اختر العملة والفريم لبدء التحليل.", ephemeral=True)
