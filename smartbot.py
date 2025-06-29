import os
import discord
import datetime
import random
from discord.ext import commands, tasks

# توكن البوت من متغير البيئة
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة عملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc", "EURNZD_otc", "EURGBP_otc", "CADCHF_otc"
]

# الفريمات والصفقات (لتنظيم الرسالة فقط)
TIMEFRAMES = ["5s", "10s", "15s", "30s", "1m"]
DURATIONS = ["30s", "1m", "2m", "3m", "5m"]

# قائمة أوقات الدخول الثابتة
ENTRY_TIMES = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]
last_signal_time = None

# بدء البوت
@bot.event
async def on_ready():
    print(f"✅ Aurix-style bot active as: {bot.user}")
    aurix_loop.start()

# نظام التكرار الزمني
@tasks.loop(seconds=1.0)
async def aurix_loop():
    global last_signal_time

    now = datetime.datetime.utcnow()
    minute = now.strftime("%M")
    second = now.strftime("%S")

    if second == "00" and minute in ENTRY_TIMES:
        if last_signal_time == now.strftime("%H:%M"):
            return
        last_signal_time = now.strftime("%H:%M")

        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await send_aurix_signal(channel)
                    return  # إرسال إشارة واحدة فقط

# إرسال الإشارة
async def send_aurix_signal(channel):
    symbol = random.choice(OTC_SYMBOLS)
    decision = random.choice(["📈 صعود", "📉 هبوط"])
    timeframe = random.choice(TIMEFRAMES)
    duration = random.choice(DURATIONS)
    now = datetime.datetime.utcnow().strftime('%H:%M:%S')

    await channel.send(
        f"🧠 **إشارة Aurix**\n"
        f"💱 العملة: `{symbol}`\n"
        f"🕒 الوقت: `{now}`\n"
        f"⏱️ الفريم: `{timeframe}` | الصفقة: `{duration}`\n"
        f"📊 القرار: **{decision}**\n"
        f"📂 [نظام التكرار الزمني مفعل]"
    )

bot.run(TOKEN)
