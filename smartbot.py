import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن من .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# دالة تحليل الصورة واتخاذ القرار للشمعة القادمة
def analyze_candle(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "⏸"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # تحليل الشموع بالألوان
    green_mask = cv2.inRange(hsv, np.array([35, 60, 60]), np.array([85, 255, 255]))
    red_mask = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255])) | \
               cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))

    green_pixels = cv2.countNonZero(green_mask)
    red_pixels = cv2.countNonZero(red_mask)

    # RSI (اللون البنفسجي غالبًا في الأسفل)
    rsi_area = img[-120:-60, 50:300]
    rsi_mean = np.mean(rsi_area[:, :, 0])  # قناة اللون الأزرق للتقدير التقريبي

    # Stochastic (خطوط بيضاء وبرتقالية/صفراء)
    stoch_area = img[-100:-30, 400:700]
    stoch_brightness = np.mean(stoch_area)

    # Bollinger Bands (تحديد مكان السعر)
    bb_area = img[150:300, 100:600]
    bb_brightness = np.mean(bb_area)

    # منطق القرار النهائي
    if (
        green_pixels > red_pixels * 1.2
        and rsi_mean < 95
        and stoch_brightness < 105
        and bb_brightness < 105
    ):
        return "🔼"  # صعود

    elif (
        red_pixels > green_pixels * 1.2
        and rsi_mean > 130
        and stoch_brightness > 130
        and bb_brightness > 130
    ):
        return "🔽"  # هبوط

    else:
        return "⏸"  # انتظار

# جاهزية البوت
@bot.event
async def on_ready():
    print(f"✅ البوت يعمل الآن: {bot.user}")

# استقبال وتحليل الصور
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = f"temp_{attachment.filename}"
                await attachment.save(path)

                result = analyze_candle(path)
                await message.channel.send(result)

                os.remove(path)

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
