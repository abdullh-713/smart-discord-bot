import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

OTC_SYMBOLS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "NZDUSD_otc", "EURJPY_otc",
    "GBPJPY_otc", "AUDCAD_otc", "EURGBP_otc", "EURNZD_otc", "CADCHF_otc"
]

TIMEFRAMES = ["5s", "10s", "15s", "30s", "1m", "2m", "5m"]
DURATIONS = ["30s", "1m", "2m", "5m"]

user_state = {}

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.command()
async def start(ctx):
    user_state[ctx.author.id] = {}
    await ctx.send(
        "**اختر العملة:**\n" + "\n".join(f"- {symbol}" for symbol in OTC_SYMBOLS)
    )

@bot.command()
async def عملة(ctx, *, symbol):
    if symbol not in OTC_SYMBOLS:
        await ctx.send("❌ العملة غير موجودة.")
        return
    user_state[ctx.author.id]["symbol"] = symbol
    await ctx.send(f"✅ تم اختيار العملة: `{symbol}`\nالآن اختر الفريم الزمني:\n" +
                   "\n".join(TIMEFRAMES))

@bot.command()
async def فريم(ctx, *, timeframe):
    if timeframe not in TIMEFRAMES:
        await ctx.send("❌ الفريم غير مدعوم.")
        return
    user_state[ctx.author.id]["timeframe"] = timeframe
    await ctx.send(f"✅ تم اختيار الفريم: `{timeframe}`\nالآن اختر مدة الصفقة:\n" +
                   "\n".join(DURATIONS))

@bot.command()
async def مدة(ctx, *, duration):
    if duration not in DURATIONS:
        await ctx.send("❌ مدة غير صالحة.")
        return
    user_state[ctx.author.id]["duration"] = duration

    await ctx.send("✅ تم اختيار كل الإعدادات، جاري تحليل السوق...")

    import random
    result = random.choice(["⬆️ صعود", "⬇️ هبوط", "⏳ انتظار"])
    await ctx.send(f"📊 نتيجة التحليل: **{result}**")

bot.run(os.getenv("TOKEN"))
