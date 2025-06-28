import os
import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import ccxt
import io

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# قائمة عملات OTC وهمية (للتجربة فقط)
OTC_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF",
    "EURJPY", "EURGBP", "NZDUSD", "AUDCAD"
]

# فريمات زمنية
TIMEFRAMES = ["5s", "15s", "30s", "1m", "2m", "5m"]

# مدد الصفقات
TRADE_DURATIONS = ["30s", "1min", "2min", "5min"]

# تحليل حقيقي من السوق باستخدام Binance
def fetch_market_data(symbol):
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe='1m', limit=10)
        closes = [candle[4] for candle in ohlcv]
        sma = sum(closes[-5:]) / 5
        last_price = closes[-1]
        if last_price > sma:
            return "📈 صعود (إشارة حقيقية)"
        elif last_price < sma:
            return "📉 هبوط (إشارة حقيقية)"
        else:
            return "⏸️ انتظار (السعر قريب من المتوسط)"
    except Exception as e:
        return f"❌ خطأ في التحليل: {str(e)}"

# استقبال الصورة وتحليل تجريبي
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                image_data = await attachment.read()
                await message.channel.send("📊 تم استقبال الشارت، جاري التحليل (تجريبي)...")
                await message.channel.send("📈 القرار التجريبي: صعود 🔼 (مبني على قراءة تجريبية)")

    await bot.process_commands(message)

# رسالة البدء
@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول باسم: {bot.user}")
    try:
        synced = await tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر.")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {str(e)}")

# أمر البداية /start
@tree.command(name="start", description="ابدأ اختيار العملة والفريم ومدة الصفقة")
async def start_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "يرجى اختيار العملة:",
        view=CurrencySelection()
    )

# زر مباشر - تجربة التثبيت على الشارت
@tree.command(name="live", description="🔍 تحليل مباشر عند تثبيتك على الشارت")
async def live_analysis(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🖥️ عند تثبيتك على الشارت لمدة 5 ثوانٍ، سيتم التحليل تلقائيًا...\n(ميزة قيد التجربة)"
    )

# أمر اختبار
@tree.command(name="اختبار", description="اختبار استجابة البوت")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("✅ تم استلام الأمر: اختبار بنجاح!")

# قائمة العملات التفاعلية
class CurrencySelection(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        for symbol in OTC_SYMBOLS:
            self.add_item(CurrencyButton(symbol))

class CurrencyButton(discord.ui.Button):
    def __init__(self, symbol):
        super().__init__(label=symbol, style=discord.ButtonStyle.primary)
        self.symbol = symbol

    async def callback(self, interaction: discord.Interaction):
        result = fetch_market_data(self.symbol)
        await interaction.response.send_message(f"📊 التحليل للعملة {self.symbol}/USDT:\n{result}")

bot.run(TOKEN)
