import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# دالة تحليل الشمعة القادمة بناءً على الألوان والمؤشرات الظاهرة بالرؤية
def analyze_chart(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "⏸ الصورة غير واضحة"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # تحليل ألوان الشموع (أخضر وأحمر)
    green_mask = cv2.inRange(hsv, np.array([35, 60, 60]), np.array([85, 255, 255]))
    red_mask1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
    red_mask2 = cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))
    red_mask = red_mask1 | red_mask2

    green_pixels = cv2.countNonZero(green_mask)
    red_pixels = cv2.countNonZero(red_mask)

    # مؤشر RSI (افتراضي أنه موجود في الأسفل بلون بنفسجي/أزرق)
    rsi_zone = img[-120:-60, 50:300]
    rsi_level = np.mean(rsi_zone[:, :, 0])  # القناة الزرقاء

    # مؤشر Bollinger Bands (افتراضي في الوسط)
    bb_zone = img[150:300, 100:600]
    brightness = np.mean(bb_zone)

    # القرار النهائي الذكي
    if green_pixels > red_pixels * 1.4 and rsi_level < 100 and brightness < 110:
        return "🔼 صعود"
    elif red_pixels > green_pixels * 1.4 and rsi_level > 130 and brightness > 120:
        return "🔽 هبوط"
    elif abs(green_pixels - red_pixels) < 600:
        return "⏸ انتظار"
    else:
        return "⏸ غير كافٍ لاتخاذ قرار"

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل الآن باسم: {bot.user}")

# عند استقبال صورة في القناة
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                file_path = f"temp_{attachment.filename}"
                await attachment.save(file_path)

                decision = analyze_chart(file_path)
                await message.channel.send(decision)

                os.remove(file_path)

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
