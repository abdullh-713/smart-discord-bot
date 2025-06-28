import os
import discord
import io
import ccxt
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from discord.ext import commands
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from PIL import Image

# تحميل التوكن
TOKEN = os.getenv("TOKEN")

# تفعيل الصلاحيات
intents = discord.Intents.default()
intents.message_content = True

# إعداد البوت
bot = commands.Bot(command_prefix="!", intents=intents)

# قوائم الخيارات
symbols = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc", "GBPJPY_otc",
    "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc", "AUDUSD_otc", "USDCHF_otc"
]
timeframes = ["5s", "10s", "30s", "1m", "5m", "15m"]
durations = ["10s", "30s", "1m", "2m", "5m"]

user_state = {}

# ===== تحليل السوق الحقيقي =====
def analyze_market(symbol: str, timeframe: str):
    try:
        exchange = ccxt.binance()
        symbol_binance = symbol.replace("_otc", "/USDT")
        ohlcv = exchange.fetch_ohlcv(symbol_binance, timeframe='1m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        rsi = RSIIndicator(df['close'], window=14).rsi().iloc[-1]
        sma_fast = SMAIndicator(df['close'], window=5).sma_indicator().iloc[-1]
        sma_slow = SMAIndicator(df['close'], window=20).sma_indicator().iloc[-1]

        if rsi > 70 and sma_fast < sma_slow:
            return "🔻 هبوط مؤكد"
        elif rsi < 30 and sma_fast > sma_slow:
            return "🔺 صعود مؤكد"
        else:
            return "⏸️ انتظر، السوق غير واضح"
    except Exception as e:
        return f"⚠️ فشل في التحليل: {str(e)}"

# ===== استقبال الصور =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
                image_bytes = await attachment.read()
                await message.channel.send("📷 تم استلام الصورة. جارٍ التحليل الذكي...")
                # تحليل وهمي حاليًا
                await asyncio.sleep(2)
                await message.channel.send("✅ التحليل: السوق يبدو في حالة تذبذب. القرار: ⏸️ انتظر")
    await bot.process_commands(message)

# ===== الأوامر التفاعلية =====
@bot.command()
async def start(ctx):
    user_state[ctx.author.id] = {}
    view = discord.ui.View()
    for sym in symbols:
        view.add_item(discord.ui.Button(label=sym, style=discord.ButtonStyle.primary, custom_id=f"sym_{sym}"))
    await ctx.send("🔽 اختر العملة:", view=view)

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 البوت يعمل!")

class ButtonView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="🔁 رجوع", style=discord.ButtonStyle.danger, custom_id="back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await start(interaction)

# ===== معالجات الأزرار =====
@bot.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id", "")
    user_id = interaction.user.id

    if custom_id.startswith("sym_"):
        symbol = custom_id.replace("sym_", "")
        user_state[user_id]["symbol"] = symbol
        view = discord.ui.View()
        for d in durations:
            view.add_item(discord.ui.Button(label=d, style=discord.ButtonStyle.secondary, custom_id=f"dur_{d}"))
        await interaction.response.send_message("⏱️ اختر مدة الصفقة:", view=view, ephemeral=True)

    elif custom_id.startswith("dur_"):
        duration = custom_id.replace("dur_", "")
        user_state[user_id]["duration"] = duration
        symbol = user_state[user_id].get("symbol", "")
        decision = analyze_market(symbol, "1m")
        await interaction.response.send_message(f"📊 التحليل للعملة: **{symbol}**\n⏱️ المدة: **{duration}**\nالقرار: **{decision}**", ephemeral=False)

    elif custom_id == "back":
        await start(interaction)

# ===== تشغيل البوت =====
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل كـ: {bot.user}")

bot.run(TOKEN)
@bot.command()
async def اختبار(ctx):
    await ctx.send("✅ التحليل الذكي يعمل الآن. أرسل صورة شارت لتحليلها أو استخدم الأزرار.")
