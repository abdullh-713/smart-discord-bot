import os
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc"
]

TIMEFRAMES = ["5s", "10s", "30s", "1min", "2min", "5min"]

SIGNALS = {
    "EURUSD_otc": {
        "5s": "🧠 Aurix Signal\n💱 EURUSD_otc\n🕒 12:00:00\n📈 Up\n📂 Auto-timer enabled ✅",
        "10s": "🧠 Aurix Signal\n💱 EURUSD_otc\n🕒 12:05:00\n📉 Down\n📂 Auto-timer enabled ✅"
    },
    "CADCHF_otc": {
        "5s": "🧠 Aurix Signal\n💱 CADCHF_otc\n🕒 12:10:00\n📈 Up\n📂 Auto-timer enabled ✅",
        "10s": "🧠 Aurix Signal\n💱 CADCHF_otc\n🕒 12:15:00\n📉 Down\n📂 Auto-timer enabled ✅"
    }
    # يمكنك إضافة باقي العملات والفريمات هنا
}

@client.event
async def on_ready():
    print(f"✅ Bot is ready as {client.user}")
    try:
        synced = await client.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@client.tree.command(name="start", description="ابدأ استخدام إشارات Aurix")
async def start(interaction: discord.Interaction):
    symbol_options = [discord.SelectOption(label=s) for s in OTC_SYMBOLS]
    symbol_menu = discord.ui.Select(placeholder="🔽 اختر العملة", options=symbol_options)

    async def symbol_callback(interaction2: discord.Interaction):
        selected_symbol = symbol_menu.values[0]
        await ask_timeframe(interaction2, selected_symbol)

    symbol_menu.callback = symbol_callback

    view = discord.ui.View()
    view.add_item(symbol_menu)
    await interaction.response.send_message("💠 اختر العملة:", view=view, ephemeral=True)

async def ask_timeframe(interaction, symbol):
    timeframe_options = [discord.SelectOption(label=t) for t in TIMEFRAMES]
    timeframe_menu = discord.ui.Select(placeholder="🕒 اختر الفريم الزمني", options=timeframe_options)

    async def timeframe_callback(interaction2: discord.Interaction):
        selected_tf = timeframe_menu.values[0]
        msg = SIGNALS.get(symbol, {}).get(selected_tf, "❌ لا توجد إشارة حالياً لهذه العملة والفريم.")
        await interaction2.response.send_message(msg)

    timeframe_menu.callback = timeframe_callback

    view = discord.ui.View()
    view.add_item(timeframe_menu)
    await interaction.followup.send(f"✅ إختر الفريم لإشارة **{symbol}**:", view=view, ephemeral=True)

client.run(TOKEN)
