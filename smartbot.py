import os
import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة العملات
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDCAD_otc", "EURJPY_otc",
    "GBPJPY_otc", "NZDUSD_otc", "EURNZD_otc", "EURGBP_otc", "CADCHF_otc"
]

# قائمة الفريمات
TIMEFRAMES = ["5s", "15s", "30s", "1m", "2m", "5m"]

# إشارات وهمية لكل زوج عملة وفريم (يجب تعديلها لاحقًا بإشارات حقيقية)
signals = {
    (symbol, tf): [random.choice(["📈 صعود", "📉 هبوط"]) for _ in range(50)]
    for symbol in OTC_SYMBOLS
    for tf in TIMEFRAMES
}

# الجلسات النشطة
user_sessions = {}

@bot.event
async def on_ready():
    print(f"✅ Bot is running as {bot.user}")

@bot.command(name="start")
async def start(ctx):
    keyboard = discord.ui.View()
    for symbol in OTC_SYMBOLS:
        keyboard.add_item(discord.ui.Button(label=symbol, style=discord.ButtonStyle.primary, custom_id=f"symbol:{symbol}"))
    await ctx.send("اختر عملة OTC:", view=keyboard)

class ButtonHandler(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="-", style=discord.ButtonStyle.secondary, disabled=True)
    async def placeholder(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass  # فقط كـ placeholder

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user_id

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["component_type"] != 2:
        return

    custom_id = interaction.data["custom_id"]

    if custom_id.startswith("symbol:"):
        selected_symbol = custom_id.split(":")[1]
        user_sessions[interaction.user.id] = {"symbol": selected_symbol}
        # قائمة الفريمات
        view = discord.ui.View()
        for tf in TIMEFRAMES:
            view.add_item(discord.ui.Button(label=tf, style=discord.ButtonStyle.success, custom_id=f"timeframe:{tf}"))
        await interaction.response.send_message(f"✅ تم اختيار العملة: `{selected_symbol}`\nاختر الفريم الزمني:", view=view, ephemeral=True)

    elif custom_id.startswith("timeframe:"):
        selected_tf = custom_id.split(":")[1]
        session = user_sessions.get(interaction.user.id)
        if not session or "symbol" not in session:
            await interaction.response.send_message("❌ لم تقم باختيار العملة أولًا. ابدأ من جديد بـ !start", ephemeral=True)
            return

        symbol = session["symbol"]
        await interaction.response.send_message(f"✅ جاري إرسال الإشارات لـ `{symbol}` على فريم `{selected_tf}` كل دقيقة...")

        # إرسال الإشارات كل 60 ثانية
        async def signal_loop():
            for signal in signals[(symbol, selected_tf)]:
                await interaction.followup.send(f"إشارة جديدة ({symbol} - {selected_tf}): {signal}")
                await asyncio.sleep(60)

        bot.loop.create_task(signal_loop())

bot.run(TOKEN)
