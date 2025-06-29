import os
import discord
from discord.ext import commands
from PIL import Image
import io
import logging

# إعدادات السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# جلب التوكن من المتغير البيئي
TOKEN = os.getenv("TOKEN")

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# تهيئة البوت
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"✅ تم تسجيل الدخول باسم: {bot.user}")

def analyze_image_colors(image: Image.Image) -> str:
    """
    تحليل الصورة بناءً على الألوان (الأخضر > صعود، الأحمر > هبوط، مختلط > انتظار)
    """
    try:
        image = image.convert("RGB").resize((300, 300))
        pixels = list(image.getdata())

        red_count = 0
        green_count = 0

        for r, g, b in pixels:
            if r > 200 and g < 100:
                red_count += 1
            elif g > 200 and r < 100:
                green_count += 1

        total = red_count + green_count

        if total == 0:
            return "❌ لا يوجد بيانات كافية"

        red_ratio = red_count / total
        green_ratio = green_count / total

        if red_ratio > 0.6:
            return "📉 هبوط"
        elif green_ratio > 0.6:
            return "📈 صعود"
        else:
            return "⏳ انتظار"
    except Exception as e:
        logger.error(f"فشل تحليل الصورة: {e}")
        return "❌ حدث خطأ أثناء تحليل الصورة."

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # تحقق من وجود مرفقات صور
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    image_bytes = await attachment.read()
                    image = Image.open(io.BytesIO(image_bytes))
                    result = analyze_image_colors(image)
                    await message.channel.send(result)
                except Exception as e:
                    logger.error(f"تحليل مرفق فشل: {e}")
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة.")
    await bot.process_commands(message)

# تشغيل البوت
if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ لم يتم العثور على التوكن في المتغير البيئي TOKEN")
    else:
        bot.run(TOKEN)
