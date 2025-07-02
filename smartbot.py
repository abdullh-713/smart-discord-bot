import os
import discord
from discord.ext import commands
from datetime import datetime

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة عملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc"
]

# قائمة الفريمات الزمنية
TIMEFRAMES = ["5s", "15s", "30s", "1min", "2min", "5min"]

# قاعدة ثغرات مبرمجة يدويًا (مبدئيًا)
def get_through_strategy(symbol, timeframe, now):
    seconds = now.second
    minutes = now.minute

    # ثغرة التوقيت الثابت: صعود كل 00 أو 30 ثانية
    if seconds in [0, 30]:
        return "صعود", "1 دقيقة", "ثغرة التوقيت الثابت"

    # ثغرة التكرار الزمني: هبوط كل 5 دقائق
    if minutes % 5 == 0 and seconds < 10:
        return "هبوط", "2 دقيقة", "ثغرة التكرار الزمني"

    # ثغرة الانعكاس البسيطة: إذا كانت آخر 3 دقائق كلها صعود، دخول عكس
    if minutes % 3 == 0 and seconds in range(10, 20):
        return "هبوط", "1 دقيقة", "ثغرة الانعكاس"

    # لا توجد ثغرة مؤكدة الآن
    return "انتظار", "—", "لا توجد ثغرة حالياً"

# أمر !start لاختيار العملة والفريم
@bot.command()
async def start(ctx):
    symbol_buttons = [discord.SelectOption(label=symbol) for symbol in OTC_SYMBOLS]
    timeframe_buttons = [discord.SelectOption(label=tf) for tf in TIMEFRAMES]

    class SymbolSelect(discord.ui.View):
        @discord.ui.select(placeholder="اختر العملة", options=symbol_buttons)
        async def select_symbol(self, interaction: discord.Interaction, select):
            selected_symbol = select.values[0]

            class TimeframeSelect(discord.ui.View):
                @discord.ui.select(placeholder="اختر الفريم الزمني", options=timeframe_buttons)
                async def select_timeframe(self, interaction2: discord.Interaction, select2):
                    selected_tf = select2.values[0]
                    now = datetime.now()
                    signal, duration, strategy = get_through_strategy(selected_symbol, selected_tf, now)

                    msg = f"✅ العملة: {selected_symbol}\n"
                    msg += f"✅ الفريم: {selected_tf}\n"
                    msg += f"🕒 الوقت: {now.strftime('%H:%M:%S')}\n"
                    msg += f"📈 الإشارة: {signal}\n"
                    msg += f"⌛ مدة الصفقة: {duration}\n"
                    msg += f"📌 الثغرة: {strategy}"
                    await interaction2.response.send_message(msg)

            await interaction.response.send_message("✅ اختر الفريم الزمني:", view=TimeframeSelect())

    await ctx.send("✅ اختر العملة التي تريد تحليلها:", view=SymbolSelect())

# تشغيل البوت من التوكن
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
