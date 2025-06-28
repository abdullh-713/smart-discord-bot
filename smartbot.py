import os
import discord
from discord.ext import commands
from discord import Intents, Interaction, ButtonStyle
from discord.ui import Button, View
import asyncio

TOKEN = os.getenv("TOKEN")

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# العملات والفريمات ومدد الصفقات
OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc",
    "CHFJPY_otc", "NZDJPY_otc", "AUDCHF_otc", "EURCAD_otc"
]
TIMEFRAMES = ["5s", "10s", "15s", "30s", "1m", "2m", "5m"]
DURATIONS = ["30s", "1m", "2m", "3m", "5m"]

user_state = {}

# تحليل ذكي وهمي (استبدله لاحقًا بتحليل حقيقي)
def smart_analysis(symbol, tf, duration):
    return f"✅ نتيجة التحليل: العملة **{symbol}**، الفريم **{tf}**، مدة الصفقة **{duration}** → 🔽 هبوط مؤكد"

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("📍 Pong!")

@bot.command(name="ابدأ")
async def start(ctx):
    view = View()
    for symbol in OTC_SYMBOLS:
        view.add_item(Button(label=symbol, style=ButtonStyle.primary, custom_id=f"symbol:{symbol}"))
    await ctx.send("اختر العملة:", view=view)

@bot.event
async def on_interaction(interaction: Interaction):
    if interaction.data["custom_id"].startswith("symbol:"):
        symbol = interaction.data["custom_id"].split(":")[1]
        user_state[interaction.user.id] = {"symbol": symbol}
        view = View()
        for tf in TIMEFRAMES:
            view.add_item(Button(label=tf, style=ButtonStyle.secondary, custom_id=f"tf:{tf}"))
        view.add_item(Button(label="رجوع", style=ButtonStyle.danger, custom_id="back"))
        await interaction.response.send_message(f"✅ اختر الفريم الزمني لـ {symbol}:", view=view, ephemeral=True)

    elif interaction.data["custom_id"].startswith("tf:"):
        tf = interaction.data["custom_id"].split(":")[1]
        user_state[interaction.user.id]["tf"] = tf
        view = View()
        for duration in DURATIONS:
            view.add_item(Button(label=duration, style=ButtonStyle.success, custom_id=f"dur:{duration}"))
        view.add_item(Button(label="رجوع", style=ButtonStyle.danger, custom_id="back"))
        await interaction.response.send_message("⏱️ اختر مدة الصفقة:", view=view, ephemeral=True)

    elif interaction.data["custom_id"].startswith("dur:"):
        duration = interaction.data["custom_id"].split(":")[1]
        info = user_state.get(interaction.user.id)
        if info:
            symbol = info.get("symbol")
            tf = info.get("tf")
            result = smart_analysis(symbol, tf, duration)
            await interaction.response.send_message(result)

    elif interaction.data["custom_id"] == "back":
        await start(interaction)

@bot.command(name="العملات")
async def show_symbols(ctx):
    await ctx.send("💱 العملات المتوفرة OTC:\n" + "\n".join(OTC_SYMBOLS))

@bot.command(name="الفريمات")
async def show_timeframes(ctx):
    await ctx.send("🕓 الفريمات الزمنية:\n" + ", ".join(TIMEFRAMES))

@bot.command(name="المدد")
async def show_durations(ctx):
    await ctx.send("⏳ مدد الصفقات:\n" + ", ".join(DURATIONS))

@bot.command(name="تحليل")
async def analyze_manual(ctx, symbol=None, tf=None, duration=None):
    if not symbol or not tf or not duration:
        await ctx.send("❌ الرجاء كتابة الأمر هكذا: `!تحليل [الرمز] [الفريم] [المدة]`")
        return
    result = smart_analysis(symbol, tf, duration)
    await ctx.send(result)

@bot.command(name="مساعدة")
async def help_command(ctx):
    await ctx.send(
        "🧠 أوامر البوت:\n"
        "`!ping` - اختبار البوت\n"
        "`!ابدأ` - عرض قائمة العملات\n"
        "`!العملات` - عرض العملات المتوفرة\n"
        "`!الفريمات` - عرض الفريمات الزمنية\n"
        "`!المدد` - عرض مدد الصفقات\n"
        "`!تحليل [الرمز] [الفريم] [المدة]` - تحليل ذكي يدوي\n"
        "`!صورة` - تحليل صورة مرسلة\n"
        "`!مباشر` - مشاركة الشاشة والتحليل التلقائي"
    )

@bot.command(name="صورة")
async def analyze_image(ctx):
    await ctx.send("📸 أرسل صورة الشارت الآن وسأقوم بتحليلها... (هذه الميزة تحت التطوير الذكي)")

@bot.command(name="مباشر")
async def screen_share(ctx):
    await ctx.send("🖥️ عند تثبيتك على الشارت لمدة 5 ثوانٍ، سيتم التحليل تلقائيًا... (ميزة قيد التجربة)")

bot.run(TOKEN)
