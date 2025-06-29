import os
import datetime
import random
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")  # تأكد أن المتغير TOKEN موجود في Railway

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة عملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc", "EURNZD_otc", "EURGBP_otc", "CADCHF_otc"
]

# أوقات الدخول الثابتة
ENTRY_TIMES = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]
last_signal_time = None

@bot.event
async def on_ready():
    print(f"✅ Aurix-style bot is active: {bot.user}")
    aurix_loop.start()

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
                    return

async def send_aurix_signal(channel):
    symbol = random.choice(OTC_SYMBOLS)
    decision = random.choice(["📈 صعود", "📉 هبوط"])
    now = datetime.datetime.utcnow().strftime('%H:%M:%S')

    await channel.send(
        f"🧠 **إشارة Aurix AI**\n"
        f"💱 العملة: `{symbol}`\n"
        f"🕒 الوقت: `{now}`\n"
        f"📊 القرار: **{decision}**\n"
        f"📂 النظام: تكرار ذكي يعتمد على التوقيت الثابت"
    )

bot.run(TOKEN)
