import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ الصورة غير واضحة"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, width = img.shape[:2]

    # تحليل الشمعة (أخضر = صعود، أحمر = هبوط)
    green_mask = cv2.inRange(hsv, (35, 60, 60), (85, 255, 255))
    red_mask1 = cv2.inRange(hsv, (0, 60, 60), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (170, 60, 60), (180, 255, 255))
    red_mask = red_mask1 | red_mask2

    green_strength = cv2.countNonZero(green_mask)
    red_strength = cv2.countNonZero(red_mask)

    # تحليل RSI - نأخذ منطقة معروفة من الصورة (مثلاً أسفل الزاوية اليمنى)
    rsi_area = img[height-60:height-30, width-110:width-10]
    rsi_gray = cv2.cvtColor(rsi_area, cv2.COLOR_BGR2GRAY)
    rsi_brightness = np.mean(rsi_gray)

    # تحليل Bollinger Bands (نقاط قرب الحافة العلوية والسفلية)
    bb_upper = img[100:110, int(width/2)-20:int(width/2)+20]
    bb_lower = img[height-110:height-100, int(width/2)-20:int(width/2)+20]
    bb_up_mean = np.mean(cv2.cvtColor(bb_upper, cv2.COLOR_BGR2GRAY))
    bb_low_mean = np.mean(cv2.cvtColor(bb_lower, cv2.COLOR_BGR2GRAY))

    # تحليل Stochastic (أخذ من منطقة أسفل الشارت)
    stoch_area = img[height-90:height-60, width-120:width-20]
    stoch_gray = cv2.cvtColor(stoch_area, cv2.COLOR_BGR2GRAY)
    stoch_value = np.mean(stoch_gray)

    # تحليل استراتيجي باستخدام كل العناصر
    if green_strength > red_strength * 1.4 and rsi_brightness < 100 and bb_up_mean < 110 and stoch_value < 100:
        return "📈 صعود"
    elif red_strength > green_strength * 1.4 and rsi_brightness > 160 and bb_low_mean < 110 and stoch_value > 150:
        return "📉 هبوط"
    else:
        return "⏸ انتظار"

@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = f"temp_{attachment.filename}"
                await attachment.save(path)
                result = analyze_image(path)
                await message.channel.send(result)
                os.remove(path)
    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
