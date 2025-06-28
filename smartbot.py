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
        "**🧠 اختر العملة التي تريد تحليلها:**\n" +
        "\n".join(f"{i+1}. {symbol}" for i, symbol in enumerate(OTC_SYMBOLS)) +
        "\n\nاكتب رقم العملة."
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id
    if user_id in user_state:
        if "symbol" not in user_state[user_id]:
            try:
                index = int(message.content) - 1
                if 0 <= index < len(OTC_SYMBOLS):
                    user_state[user_id]["symbol"] = OTC_SYMBOLS[index]
                    await message.channel.send(
                        "**⏱️ اختر الفريم الزمني:**\n" +
                        "\n".join(f"{i+1}. {tf}" for i, tf in enumerate(TIMEFRAMES)) +
                        "\n\nاكتب رقم الفريم."
                    )
                else:
                    await message.channel.send("❌ رقم غير صالح. حاول مجددًا.")
            except ValueError:
                await message.channel.send("❌ من فضلك أدخل رقم.")
            return
        elif "timeframe" not in user_state[user_id]:
            try:
                index = int(message.content) - 1
                if 0 <= index < len(TIMEFRAMES):
                    user_state[user_id]["timeframe"] = TIMEFRAMES[index]
                    await message.channel.send(
                        "**📊 اختر مدة الصفقة:**\n" +
                        "\n".join(f"{i+1}. {d}" for i, d in enumerate(DURATIONS)) +
                        "\n\nاكتب رقم المدة."
                    )
                else:
                    await message.channel.send("❌ رقم غير صالح.")
            except ValueError:
                await message.channel.send("❌ من فضلك أدخل رقم.")
            return
        elif "duration" not in user_state[user_id]:
            try:
                index = int(message.content) - 1
                if 0 <= index < len(DURATIONS):
                    user_state[user_id]["duration"] = DURATIONS[index]

                    symbol = user_state[user_id]["symbol"]
                    timeframe = user_state[user_id]["timeframe"]
                    duration = user_state[user_id]["duration"]

                    await message.channel.send(
                        f"✅ تم اختيار:\n"
                        f"• العملة: `{symbol}`\n"
                        f"• الفريم: `{timeframe}`\n"
                        f"• مدة الصفقة: `{duration}`\n\n"
                        f"🔍 جاري التحليل الحقيقي للسوق..."
                    )

                    # تحليل وهمي الآن – سنستبدله لاحقًا بالتحليل الذكي الحقيقي
                    await message.channel.send("📈 **النتيجة: صعود** (تحليل تجريبي)")

                    del user_state[user_id]  # إعادة تعيين المستخدم بعد التحليل
                else:
                    await message.channel.send("❌ رقم غير صالح.")
            except ValueError:
                await message.channel.send("❌ من فضلك أدخل رقم.")
            return

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من المتغير البيئي
bot.run(os.getenv("TOKEN"))
