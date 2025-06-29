from discord.ext import tasks
import datetime
import random

# قائمة عملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc", "EURNZD_otc", "EURGBP_otc", "CADCHF_otc"
]

ENTRY_TIMES = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]
last_signal_time = None

@bot.event
async def on_ready():
    print(f"✅ Aurix-style logic active under: {bot.user}")
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

        # قناة Discord (نفس القناة التي يعمل فيها البوت الحالي)
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await send_aurix_signal(channel)
                    return  # نرسل لإحدى القنوات فقط

async def send_aurix_signal(channel):
    symbol = random.choice(OTC_SYMBOLS)
    decision = random.choice(["📈 صعود", "📉 هبوط"])
    now = datetime.datetime.utcnow().strftime('%H:%M:%S')

    await channel.send(
        f"🧠 **إشارة Aurix**\n"
        f"💱 العملة: `{symbol}`\n"
        f"🕒 الوقت: `{now}`\n"
        f"📊 القرار: **{decision}**\n"
        f"📂 [نظام التكرار الزمني مفعل]"
    )
