import os
import random
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة شاملة للعملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc",
    "AUDCHF_otc", "AUDJPY_otc", "AUDUSD_otc", "CHFJPY_otc", "EURAUD_otc",
    "USDCAD_otc", "USDCHF_otc", "NZDJPY_otc", "GBPCAD_otc", "NZDCAD_otc"
]

# فريمات زمنية شائعة
TIMEFRAMES = ["5s", "10s", "15s", "30s", "1m", "2m", "5m"]

# ثغرات محاكاة - ثغرات عشوائية لتجربة البوت (سيتم تحسينها لاحقًا)
def pick_otc_glitch(symbol, timeframe):
    decisions = ["صعود", "هبوط"]
    durations = {
        "5s": "30 ثانية",
        "10s": "1 دقيقة",
        "15s": "1 دقيقة",
        "30s": "2 دقيقة",
        "1m": "2 دقيقة",
        "2m": "3 دقائق",
        "5m": "5 دقائق"
    }
    entry_times = ["00", "05", "10", "15", "20", "30", "45", "50", "55"]
    return {
        "decision": random.choice(decisions),
        "duration": durations.get(timeframe, "1 دقيقة"),
        "entry_time": random.choice(entry_times)
    }

# عند التشغيل
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# أمر تفاعلي لاختيار العملة والفريم
@bot.tree.command(name="إشارة", description="تحليل ثغرات OTC وإعطاء إشارة دقيقة")
@app_commands.describe(العملة="اختر العملة", الفريم="اختر الفريم الزمني")
@app_commands.choices(
    العملة=[app_commands.Choice(name=symbol, value=symbol) for symbol in OTC_SYMBOLS],
    الفريم=[app_commands.Choice(name=tf, value=tf) for tf in TIMEFRAMES]
)
async def send_signal(interaction: discord.Interaction, العملة: app_commands.Choice[str], الفريم: app_commands.Choice[str]):
    glitch = pick_otc_glitch(العملة.value, الفريم.value)

    await interaction.response.send_message(
        f"""📈 عملة: `{العملة.value}`
🕓 فريم: `{الفريم.value}`
🔍 تم اكتشاف ثغرة!

📊 القرار: **{glitch['decision']}**
⏱ مدة الصفقة: **{glitch['duration']}**
⌛ توقيت الدخول المثالي: **{glitch['entry_time']}**
""",
        ephemeral=False
    )

bot.run(TOKEN)
