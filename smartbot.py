import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env أو بيئة Railway
load_dotenv()

# تعيين صلاحيات البوت
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# إنشاء البوت
bot = commands.Bot(command_prefix="!", intents=intents)

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كبوت: {bot.user}")

# أمر بسيط لتجربة البوت
@bot.command()
async def ping(ctx):
    await ctx.send("🔔 Pong!")

# تشغيل البوت باستخدام التوكن من متغير البيئة
if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ لم يتم العثور على التوكن! تأكد من إضافة TOKEN في متغيرات Railway.")
