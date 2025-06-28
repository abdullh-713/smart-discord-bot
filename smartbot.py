import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# حالة المستخدم المؤقتة
user_state = {}

# بيانات العملات و الفريمات و مدد الصفقات
symbols = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc"]
timeframes = ["5s", "10s", "30s"]
durations = ["1m", "2m", "3m"]

# تحليل وهمي (تغيّره لاحقًا بتحليل حقيقي)
def analyze_market(symbol, timeframe, duration):
    return f"✅ التحليل: {symbol}, {timeframe}, {duration} → 🔼 صعود"  # أو 🔽 هبوط

# بدء الواجهة التفاعلية
@bot.command()
async def اختيار(ctx):
    user_state[ctx.author.id] = {}
    view = discord.ui.View()
    for sym in symbols:
        view.add_item(discord.ui.Button(label=sym, custom_id=f"sym_{sym}"))
    await ctx.send("📌 اختر العملة:", view=view)

# التعامل مع الضغط على الأزرار
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        user_id = interaction.user.id
        custom_id = interaction.data['custom_id']

        if custom_id.startswith("sym_"):
            symbol = custom_id.replace("sym_", "")
            user_state[user_id]["symbol"] = symbol
            view = discord.ui.View()
            for tf in timeframes:
                view.add_item(discord.ui.Button(label=tf, custom_id=f"tf_{tf}"))
            await interaction.response.send_message("⏱ اختر الفريم الزمني:", view=view)

        elif custom_id.startswith("tf_"):
            tf = custom_id.replace("tf_", "")
            user_state[user_id]["timeframe"] = tf
            view = discord.ui.View()
            for dur in durations:
                view.add_item(discord.ui.Button(label=dur, custom_id=f"dur_{dur}"))
            await interaction.response.send_message("🕒 اختر مدة الصفقة:", view=view)

        elif custom_id.startswith("dur_"):
            dur = custom_id.replace("dur_", "")
            user_state[user_id]["duration"] = dur
            symbol = user_state[user_id]["symbol"]
            timeframe = user_state[user_id]["timeframe"]
            result = analyze_market(symbol, timeframe, dur)
            await interaction.response.send_message(result)

# الرد على كلمة "الاختبار"
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.strip().lower() == "الاختبار":
        await message.channel.send("✅ البوت يعمل بشكل سليم!")

    await bot.process_commands(message)

# تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل كـ {bot.user}")

bot.run(TOKEN)
