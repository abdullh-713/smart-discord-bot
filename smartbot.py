import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن من البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحليل الشمعة القادمة باستخدام مؤشرات RSI + Bollinger + Stochastic + MA
def analyze_image_advanced(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "⏸ الصورة غير واضحة"

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # --- مؤشرات الألوان ---
        # صعود (أخضر)
        green_mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
        green_score = cv2.countNonZero(green_mask)

        # هبوط (أحمر)
        red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255])) | \
                   cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
        red_score = cv2.countNonZero(red_mask)

        # مؤشر RSI (منطقة أسفل الشارت عادةً بنفسجي)
        rsi_zone = img[-100:-50, 40:300]
        rsi_mean = np.mean(rsi_zone[:, :, 0])  # متوسط الأزرق لتقدير التشبع

        # Bollinger Bands (تفوق أو هبوط مفاجئ)
        bb_zone = img[140:240, 100:600]
        bb_brightness = np.mean(bb_zone)

        # Moving Average تقريبًا في منتصف الشارت (خط أصفر أو أبيض)
        ma_zone = img[100:140, 150:400]
        ma_brightness = np.mean(ma_zone)

        # Stochastic (عادة رمادي/أزرق أسفل RSI)
        sto_zone = img[-50:, 40:300]
        sto_std = np.std(sto_zone[:, :, 2])  # تذبذب الأحمر

        # --- منطق القرار النهائي ---
        if red_score > green_score * 1.2 and rsi_mean > 130 and bb_brightness < 90 and sto_std > 20:
            return "🔽 هبوط"
        elif green_score > red_score * 1.2 and rsi_mean < 100 and bb_brightness > 120 and sto_std > 20:
            return "🔼 صعود"
        else:
            return "⏸ انتظار"
    except Exception as e:
        return f"⚠️ خطأ في التحليل: {str(e)}"

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل الآن باسم: {bot.user}")

# استقبال الصور وتحليلها فوراً
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                temp_path = f"temp_{attachment.filename}"
                await attachment.save(temp_path)

                decision = analyze_image_advanced(temp_path)
                await message.channel.send(decision)

                os.remove(temp_path)
    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
