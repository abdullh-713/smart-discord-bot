import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل متغيرات البيئة (TOKEN)
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعدادات صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل الآن كمستخدم: {bot.user}")

# دالة التحليل للشمعة القادمة فقط
def analyze_image_for_next_candle(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ الصورة غير واضحة أو تالفة"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # تعريف ألوان الشموع
    green_lower = np.array([35, 50, 50])
    green_upper = np.array([85, 255, 255])
    red_lower1 = np.array([0, 70, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 70, 50])
    red_upper2 = np.array([180, 255, 255])

    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    red_mask = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)

    green_pixels = cv2.countNonZero(green_mask)
    red_pixels = cv2.countNonZero(red_mask)

    # القرار النهائي موجه فقط للشمعة القادمة
    if green_pixels > red_pixels * 1.4:
        return "📈 التحليل: 🔼 صعود (للشمعة القادمة)"
    elif red_pixels > green_pixels * 1.4:
        return "📉 التحليل: 🔽 هبوط (للشمعة القادمة)"
    else:
        return "⏸ التحليل: انتظار (لا قرار حاسم للشمعة القادمة)"

# استقبال الصور من القناة وتحليلها
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                file_path = f"received_{attachment.filename}"
                await attachment.save(file_path)

                result = analyze_image_for_next_candle(file_path)
                await message.channel.send(result)

                os.remove(file_path)

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
