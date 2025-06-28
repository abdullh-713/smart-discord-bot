import os
import discord
from discord.ext import commands
from datetime import datetime
import random

# إعداد التوكن من المتغير البيئي
TOKEN = os.getenv("TOKEN")

# تهيئة البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة عملات OTC
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc",
    "AUDUSD_otc", "CHFJPY_otc", "NZDJPY_otc", "AUDCHF_otc", "EURCAD_otc"
]

# الفريمات الزمنية
TIMEFRAMES = ["5s", "10s", "15s", "30s", "1m", "2m", "5m"]

# مدد الصفقات
DURATIONS = ["30s", "1m", "2m", "3m", "5m"]

# رد عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# أمر اختبار الاتصال
@bot.command()
async def ping(ctx):
    await ctx.send("✅ البوت يعمل بنجاح.")

# قائمة العملات
@bot.command()
async def العملات(ctx):
    await ctx.send("💱 العملات المتوفرة OTC:\n" + "\n".join(OTC_SYMBOLS))

# قائمة الفريمات
@bot.command()
async def الفريمات(ctx):
    await ctx.send("🕒 الفريمات الزمنية:\n" + ", ".join(TIMEFRAMES))

# قائمة مدد الصفقات
@bot.command()
async def المدد(ctx):
    await ctx.send("⏱️ مدد الصفقات:\n" + ", ".join(DURATIONS))

# تحليل ذكي للسوق (محاكاة)
@bot.command()
async def تحليل(ctx, العملة: str, الفريم: str, المدة: str):
    if العملة not in OTC_SYMBOLS:
        await ctx.send("❌ العملة غير مدعومة.")
        return
    if الفريم not in TIMEFRAMES:
        await ctx.send("❌ الفريم غير مدعوم.")
        return
    if المدة not in DURATIONS:
        await ctx.send("❌ مدة الصفقة غير مدعومة.")
        return

    الاتجاه = random.choice(["📈 صعود", "📉 هبوط", "⏸️ انتظار"])
    الوقت = datetime.now().strftime("%H:%M:%S")
    await ctx.send(f"""🔍 تحليل ذكي للعملة **{العملة}**  
🕒 الفريم: {الفريم}  
⏱️ مدة الصفقة: {المدة}  
📊 القرار: **{الاتجاه}**  
🕰️ الوقت: {time}
""")

# أمر المساعدة
@bot.command()
async def مساعدة(ctx):
    await ctx.send("""
📌 أوامر البوت المتاحة:

!ping - اختبار البوت
!العملات - عرض العملات المتاحة
!الفريمات - عرض الفريمات
!المدد - عرض مدد الصفقات
!تحليل [العملة] [الفريم] [المدة] - إجراء تحليل ذكي
!مساعدة - عرض هذه القائمة
""")

bot.run(TOKEN)
