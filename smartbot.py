import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")  # يجب أن يكون متغير TOKEN مضاف في منصة Railway

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# دالة التحليل الذكي للشمعة القادمة فقط
def analyze_candle_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ الصورة غير واضحة أو تالفة"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # تعريف ألوان الشموع
    green_lower = np.array([35, 40, 40])
    green_upper = np.array([85, 255, 255])
    red_lower1 = np.array([0, 60, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 60, 50])
    red_upper2 = np.array([180, 255, 255])

    # استخراج قوة الشموع
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    red_mask = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)

    green_strength = cv2.countNonZero(green_mask)
    red_strength = cv2.countNonZero(red_mask)

    # تحليل جسم الشمعة لمعرفة قوتها (تفادي الإشارات الضعيفة)
    candle_body = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(candle_body, 150, 255, cv2.THRESH_BINARY)
    white_area = cv2.countNonZero(thresh)

    # القرار النهائي
    if green_strength > red_strength and white_area > 12000:
        return "🔼 صعود"
    elif red_strength > green_strength and white_area > 12000:
        return "🔽 هبوط"
    elif abs(green_strength - red_strength) < 800:
        return "🔽 هبوط" if red_strength > green_strength else "🔼 صعود"
    else:
        return "⏸ انتظار (الصورة غير واضحة للتحليل)"

# عند استقبال صورة داخل القناة
@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                file_path = f"temp_{attachment.filename}"
                await attachment.save(file_path)

                result = analyze_candle_image(file_path)
                await message.channel.send(result)

                os.remove(file_path)

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
