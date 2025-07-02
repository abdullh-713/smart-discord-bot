import os
import cv2
import numpy as np
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن من متغير البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحليل ذكي متكامل للشمعة القادمة
def analyze_candle_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ تعذر قراءة الصورة"

    img = cv2.resize(img, (800, 400))  # تحسين الدقة
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # مؤشرات Bollinger Bands + Moving Average (تحليل بصري مبسط)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    bb_strength = np.sum(edges[300:350, 300:500])  # منطقة بولينجر
    ma_line = np.sum(edges[150:180, 300:500])      # منطقة الموفينج أفريج

    # ألوان الشموع
    green_mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
    red_mask1 = cv2.inRange(hsv, np.array([0, 60, 60]), np.array([10, 255, 255]))
    red_mask2 = cv2.inRange(hsv, np.array([170, 60, 60]), np.array([180, 255, 255]))
    red_mask = red_mask1 | red_mask2

    green_area = cv2.countNonZero(green_mask)
    red_area = cv2.countNonZero(red_mask)

    # مؤشر RSI و Stochastic (مناطق معينة من الصورة)
    rsi_zone = gray[50:100, 600:750]
    stoch_zone = gray[110:160, 600:750]
    rsi_value = np.mean(rsi_zone)
    stoch_value = np.mean(stoch_zone)

    # قرار ذكي باستخدام استراتيجية مدمجة
    if green_area > red_area and rsi_value > 130 and stoch_value > 130 and ma_line > 5000:
        return "🔼 صعود"
    elif red_area > green_area and rsi_value < 100 and stoch_value < 100 and ma_line > 5000:
        return "🔽 هبوط"
    elif abs(green_area - red_area) < 800 or ma_line < 3000 or bb_strength < 3000:
        return "⏸ انتظار"
    else:
        return "⏸ انتظار"

# استقبال الصور وتحليلها تلقائيًا
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = f"temp_{attachment.filename}"
                await attachment.save(path)
                result = analyze_candle_image(path)
                await message.channel.send(result)
                os.remove(path)
    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
