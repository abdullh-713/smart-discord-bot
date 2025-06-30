import os
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="/", intents=intents)

OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc"
]

TIMEFRAMES = ["5s", "10s", "15s", "30s", "1min", "2min", "3min", "5min"]

SIGNALS = {
    "EURUSD_otc": {
        "5s": "🧠 إشـارة Aurix\n💱 العملة: EURUSD_otc\n🕒 الوقت: 12:10:25\n📉 القرار: هبوط\n📂 [نظام التكرار الزمني مفعل ✅]",
        "10s": "🧠 إشـارة Aurix\n💱 العملة: EURUSD_otc\n🕒 الوقت: 13:15:33\n📈 القرار: صعود\n📂 [نظام التكرار الزمني مفعل ✅]"
    },
    "GBPUSD_otc": {
        "5s": "🧠 إشـارة Aurix\n💱 العملة: GBPUSD_otc\n🕒 الوقت: 15:12:33\n📉 القرار: هبوط\n📂 [نظام التكرار الزمني مفعل ✅]",
        "10s": "🧠 إشـارة Aurix\n💱 العملة: GBPUSD_otc\n🕒 الوقت: 21:46:42\n📈 القرار: صعود\n📂 [نظام التكرار الزمني مفعل ✅]"
    },
    "USDJPY_otc": {
        "5s": "🧠 إشـارة Aurix\n💱 العملة: USDJPY_otc\n🕒 الوقت: 14:42:37\n📈 القرار: صعود\n📂 [نظام التكرار الزمني مفعل ✅]",
        "10s": "🧠 إشـارة Aurix\n💱 العملة: USDJPY_otc\n🕒 الوقت: 12:39:10\n📈 القرار: صعود\n📂 [نظام التكرار الزمني مفعل ✅]"
    },
    "CADCHF_otc": {
        "5s": "🧠 إشـارة Aurix\n💱 العملة: CADCHF_otc\n🕒 الوقت: 12:10:00\n📈 القرار: صعود\n📂 [نظام التكرار الزمني مفعل ✅]",
        "10s": "🧠 إشـارة Aurix\n💱 العملة: CADCHF_otc\n🕒 الوقت: 12:15:00\n📉 القرار: هبوط\n📂 [نظام التكرار الزمني مفعل ✅]"
    }
    # يمكنك إضافة بقية العملات بنفس النمط
}

@client.event
async def on_ready():
    print(f"✅ Bot is ready as {client.user}")
    try:
        synced = await client.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@client.tree.command(name="start", description="ابدأ إشارات Aurix")
async def start(interaction: discord.Interaction):
    symbol_options = [discord.SelectOption(label=symbol) for symbol in OTC_SYMBOLS]

    class SymbolSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="🔽 اختر العملة", options=symbol_options)

        async def callback(self, interaction2: discord.Interaction):
            await ask_timeframe(interaction2, self.values[0])

    view = discord.ui.View()
    view.add_item(SymbolSelect())
    await interaction.response.send_message("🔰 اختر العملة:", view=view, ephemeral=True)

async def ask_timeframe(interaction, symbol):
    timeframe_options = [discord.SelectOption(label=tf) for tf in TIMEFRAMES]

    class TimeframeSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="🔽 اختر الفريم الزمني", options=timeframe_options)

        async def callback(self, interaction2: discord.Interaction):
            tf = self.values[0]
            signal = SIGNALS.get(symbol, {}).get(tf, "❌ لا توجد إشارة حالياً لهذه العملة والفريم.")
            await interaction2.response.send_message(signal)

    view = discord.ui.View()
    view.add_item(TimeframeSelect())
    await interaction.followup.send(f"✅ اختر الفريم الزمني لإشارة **{symbol}**:", view=view, ephemeral=True)

client.run(TOKEN)
