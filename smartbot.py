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
        "**اختر العملة من القائمة التالية:**\n" +
        "\n".join(f"- `{symbol}`" for symbol in OTC_SYMBOLS)
    )

@bot.command()
async def set_symbol(ctx, symbol: str):
    if ctx.author.id not in user_state:
        await ctx.send("اكتب الأمر `!start` أولاً.")
        return
    if symbol not in OTC_SYMBOLS:
        await ctx.send("❌ العملة غير صحيحة. اختر من القائمة.")
        return
    user_state[ctx.author.id]['symbol'] = symbol
    await ctx.send("✅ تم اختيار العملة.\nالآن اختر الفريم الزمني:\n" + "\n".join(f"- `{tf}`" for tf in TIMEFRAMES))

@bot.command()
async def set_timeframe(ctx, timeframe: str):
    if ctx.author.id not in user_state or 'symbol' not in user_state[ctx.author.id]:
        await ctx.send("❌ يجب أن تختار العملة أولاً باستخدام `!set_symbol`.")
        return
    if timeframe not in TIMEFRAMES:
        await ctx.send("❌ الفريم غير متاح.")
        return
    user_state[ctx.author.id]['timeframe'] = timeframe
    await ctx.send("✅ تم تعيين الفريم الزمني.\nالآن اختر مدة الصفقة:\n" + "\n".join(f"- `{d}`" for d in DURATIONS))

@bot.command()
async def set_duration(ctx, duration: str):
    if ctx.author.id not in user_state or 'timeframe' not in user_state[ctx.author.id]:
        await ctx.send("❌ يجب أن تختار الفريم أولاً باستخدام `!set_timeframe`.")
        return
    if duration not in DURATIONS:
        await ctx.send("❌ المدة غير متاحة.")
        return
    user_state[ctx.author.id]['duration'] = duration
    user = user_state[ctx.author.id]
    await ctx.send(f"✅ تم إعداد البوت بنجاح:\n- العملة: `{user['symbol']}`\n- الفريم: `{user['timeframe']}`\n- المدة: `{user['duration']}`")

# بدء تشغيل البوت باستخدام التوكن من المتغير البيئي
bot.run(os.getenv("TOKEN"))
