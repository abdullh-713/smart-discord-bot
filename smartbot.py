import os
import discord
from discord.ext import commands
from discord import app_commands
import json

# تحميل جدول الإشارات المدمج
with open("full_signal_table.json", "r", encoding="utf-8") as f:
    SIGNALS = json.load(f)

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc"
]

TIMEFRAMES = ["1min", "2min", "3min", "5min"]

@tree.command(name="start", description="ابدأ البوت واختر العملة")
async def start_command(interaction: discord.Interaction):
    options = [discord.SelectOption(label=symbol) for symbol in OTC_SYMBOLS]

    select = discord.ui.Select(placeholder="اختر العملة ⬇️", options=options)

    async def select_callback(select_interaction: discord.Interaction):
        selected_symbol = select.values[0]
        await ask_timeframe(select_interaction, selected_symbol)

    view = discord.ui.View()
    select.callback = select_callback
    view.add_item(select)
    await interaction.response.send_message("📗 اختر العملة:", view=view, ephemeral=True)

async def ask_timeframe(interaction: discord.Interaction, symbol):
    options = [discord.SelectOption(label=frame) for frame in TIMEFRAMES]

    select = discord.ui.Select(placeholder=f"اختر الفريم الزمني لإشارة {symbol} ✅", options=options)

    async def select_callback(select_interaction: discord.Interaction):
        selected_frame = select.values[0]
        await send_signal(select_interaction, symbol, selected_frame)

    view = discord.ui.View()
    select.callback = select_callback
    view.add_item(select)
    await interaction.response.send_message(f"✅ اختر الفريم الزمني لإشارة:\n**{symbol}**", view=view, ephemeral=True)

async def send_signal(interaction: discord.Interaction, symbol, timeframe):
    data = SIGNALS.get(symbol, {}).get(timeframe, [])
    if not data:
        await interaction.response.send_message("❌ لا توجد إشارة حالياً لهذه العملة والفريم.", ephemeral=True)
        return

    # احضار أول إشارة قادمة (نموذجية)
    next_signal = data[0]
    decision = next_signal["decision"]
    time_str = next_signal["time"]

    msg = f"""**إشارة Aurix 🧠**
العملة: `{symbol}`
🕰️ الوقت: `{time_str}`
📈 القرار: `{decision}`
📁 [نظام التكرار الزمني مفعل ✅]"""

    await interaction.response.send_message(msg)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

bot.run(TOKEN)
