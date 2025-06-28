import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} is ready.")

@bot.command()
async def start(ctx):
    await ctx.send("🤖 مرحبًا بك! أرسل 'اختبار' أو 'مباشر' أو 'تحليل' وسأرد عليك تلقائيًا.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if "اختبار" in content:
        await message.channel.send("✅ تم استلام الأمر: اختبار بنجاح!")
    elif "مباشر" in content:
        await message.channel.send("📡 الوضع المباشر مفعل الآن.")
    elif "تحليل" in content:
        await message.channel.send("📊 جاري تحليل السوق...")

    await bot.process_commands(message)

# توكن البوت من المتغير البيئي
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
