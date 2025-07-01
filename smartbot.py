import discord
from discord.ext import commands
import os
import cv2
import numpy as np
from dotenv import load_dotenv

# تحميل التوكن من متغير البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# دالة التحليل الذكي للشمعة القادمة باستخدام المؤشرات
def analyze_image_for_next_candle(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ الصورة غير واضحة"

    # تحويل الصورة إلى أنظمة ألوان مختلفة
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # تحديد ألوان الشموع (أخضر وأحمر)
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

    # استخراج مناطق المؤشرات من الصورة (حسب مقاساتك على الشارت)
    rsi_region = gray[540:560, 40:500]         # مؤشر RSI
    stochastic_region = gray[570:590, 40:500]  # مؤشر Stochastic
    bollinger_region = gray[110:190, 40:500]   # Bollinger Bands
    price_region = gray[200:360, 40:500]       # منطقة الشموع

    # تحليل المؤشرات
    rsi_mean = np.mean(rsi_region)
    stochastic_mean = np.mean(stochastic_region)
    bollinger_std = np.std(bollinger_region)
    price_trend = np.mean(price_region[-10:]) - np.mean(price_region[:10])

    # الشروط الذكية لاتخاذ القرار
    if rsi_mean > 150 and stochastic_mean > 150 and green_pixels > red_pixels * 1.4 and price_trend > 0 and bollinger_std > 10:
        return "🔼 صعود"
    elif rsi_mean < 100 and stochastic_mean < 100 and red_pixels > green_pixels * 1.4 and price_trend < 0 and bollinger_std > 10:
        return "🔽 هبوط"
    else:
        return "⏸ انتظار"

# استقبال وتحليل الصور
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
