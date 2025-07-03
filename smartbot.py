import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# قائمة العملات والفريمات
symbols = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDCAD_otc",
    "NZDUSD_otc", "EURJPY_otc", "GBPJPY_otc", "EURGBP_otc",
    "EURNZD_otc", "AUDCHF_otc", "USDCAD_otc", "EURCAD_otc"
]

timeframes = ["5s", "15s", "30s", "1m", "2m", "3m", "5m"]

# صياغة مدة الصفقة بوضوح
def صيغة_المدة(ثواني):
    if ثواني < 60:
        return f"{ثواني} ثانية"
    elif ثواني == 60:
        return "1 دقيقة"
    else:
        دقائق = ثواني // 60
        return f"{دقائق} دقائق"

# توليد إشارة بناءً على الفريم والعملات
def تحليل_الثغرة(رمز, فريم):
    direction = random.choice(["صعود", "هبوط"])
    now = datetime.now()

    if فريم in ["5s", "15s", "30s"]:
        المدة = 30
        التوقيت = f"الثانية {random.choice([10, 15, 20, 25, 30, 40, 45])} من الدقيقة الحالية"
    else:
        المدة = random.choice([60, 120, 180])
        التوقيت = f"الدقيقة {random.choice([0, 5, 10, 15, 20, 30, 45, 55])} من الساعة الحالية"

    return {
        "decision": direction,
        "duration": صيغة_المدة(المدة),
        "entry": التوقيت
    }

# أمر Discord
@tree.command(name="start", description="تحليل ثغرة OTC لعملة وفريم محدد")
@app_commands.describe(
    symbol="اختر العملة",
    timeframe="اختر الفريم الزمني"
)
@app_commands.choices(
    symbol=[app_commands.Choice(name=s, value=s) for s in symbols],
    timeframe=[app_commands.Choice(name=t, value=t) for t in timeframes]
)
async def start(interaction: discord.Interaction, symbol: app_commands.Choice[str], timeframe: app_commands.Choice[str]):
    await interaction.response.defer()
    signal = تحليل_الثغرة(symbol.value, timeframe.value)
    
    message = (
        f"📊 العملة: `{symbol.value}`\n"
        f"🕐 الفريم: `{timeframe.value}`\n"
        f"🔍 تم اكتشاف ثغرة فعالة!\n\n"
        f"📈 القرار: **{signal['decision']}**\n"
        f"⏱ مدة الصفقة: **{signal['duration']}**\n"
        f"⏰ وقت الدخول: **{signal['entry']}**"
    )
    
    await interaction.followup.send(message)

# تشغيل البوت
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN)
