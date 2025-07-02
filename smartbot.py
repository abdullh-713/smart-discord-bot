‏import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل متغير التوكن
load_dotenv()
TOKEN = os.getenv("TOKEN")

# صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحليل متقدم (شمعة قادمة فقط) بناءً على مؤشرات مرئية
def advanced_candle_decision(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "⏸"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # تحليل ألوان الشموع
    green_mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
    red_mask = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255])) | \
               cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))
    green_pixels = cv2.countNonZero(green_mask)
    red_pixels = cv2.countNonZero(red_mask)

    # تحليل RSI كتشبع (مؤقت: أسفل الشاشة باللون البنفسجي)
    rsi_area = img[-120:-60, 50:300]
    rsi_mean = np.mean(rsi_area[:, :, 0])  # نأخذ المتوسط اللوني للقناة الزرقاء كقيمة تقديرية

    # تحليل Bollinger (مكان السعر)
    band_area = img[150:300, 100:600]
    bright = np.mean(band_area)

    # منطق القرار النهائي الذكي
    if rsi_mean < 90 and bright < 100 and green_pixels > red_pixels * 1.3:
        return "🔼"
    elif rsi_mean > 130 and red_pixels > green_pixels * 1.3:
        return "🔽"
    else:
        return "⏸"

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل الآن: {bot.user}")

# استلام الصور وتحليلها فورًا
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = f"temp_{attachment.filename}"
                await attachment.save(file_path)

                decision = advanced_candle_decision(file_path)
                await message.channel.send(decision)

                os.remove(file_path)

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
