import os
import random
import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands

# إعداد البوت
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة عملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc", "EURNZD_otc", "EURGBP_otc", "CADCHF_otc"
]

# قائمة توقيتات الدخول
ENTRY_TIMES = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]
last_signal_time = None

# ✅ عند التشغيل
@bot.event
async def on_ready():
    print(f"✅ Aurix-style bot active as: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🟢 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
    aurix_loop.start()

# ✅ أمر /start من نوع سلاش
@bot.tree.command(name="start", description="ابدأ تحليل Aurix")
async def start(interaction: discord.Interaction):
    view = AurixButton()
    await interaction.response.send_message("👋 مرحبًا بك في نظام إشارات Aurix\nاضغط على الزر أدناه لبدء التحليل ⬇️", view=view)

# ✅ الزر التفاعلي
class AurixButton(discord.ui.View):
    @discord.ui.button(label="ابدأ التحليل", style=discord.ButtonStyle.success)
    async def start_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_aurix_signal(interaction.channel)

# ✅ إشارات تلقائية كل 5 دقائق
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

# ✅ إرسال إشارة
async def send_aurix_signal(channel):
    symbol = random.choice(OTC_SYMBOLS)
    decision = random.choice(["📈 صعود", "📉 هبوط"])
    now = datetime.datetime.utcnow().strftime('%H:%M:%S')

    await channel.send(
        f"🧠 **إشارة Aurix**\n"
        f"💱 العملة: `{symbol}`\n"
        f"🕒 الوقت: `{now}`\n"
        f"📊 القرار: **{decision}**\n"
        f"📂 [نظام التكرار الزمني مفعل ✅]"
    )

# ✅ تشغيل البوت باستخدام التوكن من المتغير البيئي
bot.run(os.getenv("TOKEN"))
