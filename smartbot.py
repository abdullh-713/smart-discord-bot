import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_candle_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ تعذر قراءة الصورة"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # تحليل الألوان (الشموع)
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    red_mask1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    green_area = cv2.countNonZero(green_mask)
    red_area = cv2.countNonZero(red_mask)

    # مؤشر Bollinger Bands - تحليل الحواف
    edges = cv2.Canny(gray, 50, 150)
    upper_band_area = edges[:int(edges.shape[0]*0.3), :].sum()
    lower_band_area = edges[int(edges.shape[0]*0.7):, :].sum()

    # مؤشر RSI و Stochastic (تحليل مناطق التشبع بالألوان الزرقاء والصفراء)
    rsi_zone = hsv[gray.shape[0]//2:gray.shape[0], :]
    blue_rsi = cv2.inRange(rsi_zone, (90, 50, 50), (130, 255, 255))
    yellow_stochastic = cv2.inRange(rsi_zone, (20, 100, 100), (35, 255, 255))

    rsi_value = cv2.countNonZero(blue_rsi)
    stochastic_value = cv2.countNonZero(yellow_stochastic)

    # الشروط
    if (
        green_area > red_area + 3000
        and lower_band_area > upper_band_area
        and stochastic_value > 1000
        and rsi_value < 800
    ):
        return "🔼 صعود"
    
    elif (
        red_area > green_area + 3000
        and upper_band_area > lower_band_area
        and stochastic_value > 1000
        and rsi_value > 800
    ):
        return "🔽 هبوط"

    else:
        return "⏸ انتظار"

@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                file_path = f"temp_{attachment.filename}"
                await attachment.save(file_path)

                decision = analyze_candle_image(file_path)
                await message.channel.send(decision)

                os.remove(file_path)

    await bot.process_commands(message)

bot.run(TOKEN)
