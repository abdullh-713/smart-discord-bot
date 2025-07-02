import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن من متغير البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_image_advanced(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ الصورة غير واضحة"

    height, width, _ = img.shape

    # مقاطع المؤشرات في الصورة (حسب مواقعها المعروفة في الشارت)
    rsi_zone = img[int(height*0.85):int(height*0.95), int(width*0.05):int(width*0.95)]
    stoch_zone = img[int(height*0.75):int(height*0.83), int(width*0.05):int(width*0.95)]
    bb_zone = img[int(height*0.15):int(height*0.45), int(width*0.05):int(width*0.95)]
    ma_zone = img[int(height*0.15):int(height*0.45), int(width*0.05):int(width*0.95)]
    candles_zone = img[int(height*0.15):int(height*0.45), int(width*0.05):int(width*0.95)]

    # تحليل RSI
    rsi_gray = cv2.cvtColor(rsi_zone, cv2.COLOR_BGR2GRAY)
    _, rsi_thresh = cv2.threshold(rsi_gray, 200, 255, cv2.THRESH_BINARY)
    rsi_white_pixels = cv2.countNonZero(rsi_thresh)

    # تحليل Stochastic
    stoch_gray = cv2.cvtColor(stoch_zone, cv2.COLOR_BGR2GRAY)
    _, stoch_thresh = cv2.threshold(stoch_gray, 200, 255, cv2.THRESH_BINARY)
    stoch_white_pixels = cv2.countNonZero(stoch_thresh)

    # تحليل Bollinger Bands
    bb_gray = cv2.cvtColor(bb_zone, cv2.COLOR_BGR2GRAY)
    _, bb_thresh = cv2.threshold(bb_gray, 200, 255, cv2.THRESH_BINARY)
    bb_white_pixels = cv2.countNonZero(bb_thresh)

    # تحليل الشموع
    hsv = cv2.cvtColor(candles_zone, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (35, 60, 60), (85, 255, 255))
    red_mask1 = cv2.inRange(hsv, (0, 60, 60), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (170, 60, 60), (180, 255, 255))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    green_count = cv2.countNonZero(green_mask)
    red_count = cv2.countNonZero(red_mask)

    # الشروط الذكية (بدون تحيز)
    if rsi_white_pixels > 4000 and stoch_white_pixels > 3500 and green_count > red_count * 1.2:
        return "🔼 صعود"
    elif rsi_white_pixels > 4000 and stoch_white_pixels > 3500 and red_count > green_count * 1.2:
        return "🔽 هبوط"
    elif bb_white_pixels < 4000 and abs(red_count - green_count) < 500:
        return "⏸ انتظار"
    else:
        return "⏸ انتظار"

@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = f"temp_{attachment.filename}"
                await attachment.save(file_path)

                result = analyze_image_advanced(file_path)
                await message.channel.send(result)

                os.remove(file_path)

    await bot.process_commands(message)

bot.run(TOKEN)
