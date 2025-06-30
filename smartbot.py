import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="/", intents=intents)

OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc"
]

TIMEFRAMES = ["5s", "10s", "30s", "1min", "2min", "5min"]

SIGNALS = {
    "EURUSD_otc": {
        "5s": "📊 إشـارة Aurix\n💱 العملة: EURUSD_otc\n🕒 الوقت: 12:00:00\n📈 القرار: صعود\n📂 نظام التكرار الزمني مفعل ✅",
        "10s": "📊 إشـارة Aurix\n💱 العملة: EURUSD_otc\n🕒 الوقت: 12:05:00\n📉 القرار: هبوط\n📂 نظام التكرار الزمني مفعل ✅"
    },
    "CADCHF_otc": {
        "5s": "📊 إشـارة Aurix\n💱 العملة: CADCHF_otc\n🕒 الوقت: 12:10:00\n📈 القرار: صعود\n📂 نظام التكرار الزمني مفعل ✅",
        "10s": "📊 إشـارة Aurix\n💱 العملة: CADCHF_otc\n🕒 الوقت: 12:15:00\n📉 القرار: هبوط\n📂 نظام التكرار الزمني مفعل ✅"
    }
}

class TimeframeMenu(Select):
    def __init__(self, symbol):
        self.symbol = symbol
        options = [discord.SelectOption(label=tf, description=f"عرض إشارة {symbol} لفريم {tf}") for tf in TIMEFRAMES]
        super().__init__(placeholder="🔽 اختر الفريم الزمني", options=options)

    async def callback(self, interaction: discord.Interaction):
        signal = SIGNALS.get(self.symbol, {}).get(self.values[0], "❌ لا توجد إشارة حالياً لهذه العملة والفريم.")
        await interaction.response.send_message(signal, ephemeral=True)

class SymbolMenu(Select):
    def __init__(self):
        options = [discord.SelectOption(label=symbol, description=f"اختر {symbol}") for symbol in OTC_SYMBOLS]
        super().__init__(placeholder="🔽 اختر العملة", options=options)

    async def callback(self, interaction: discord.Interaction):
        view = View(timeout=None)
        view.add_item(TimeframeMenu(self.values[0]))
        await interaction.response.send_message(f"✅ اختر الفريم الزمني لإشارة **{self.values[0]}**:", view=view, ephemeral=True)

class MainMenu(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SymbolMenu())

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"✅ Bot is ready as {client.user}")

@client.tree.command(name="start", description="ابدأ تحليل Aurix")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message("📌 اختر العملة:", view=MainMenu(), ephemeral=True)

client.run(TOKEN)
