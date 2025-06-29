import os
import discord
from discord.ext import commands
import pytesseract
from PIL import Image
import cv2
import numpy as np
import requests
from io import BytesIO
import traceback

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")  # تأكد أن المتغير البيئي مضاف في Railway

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول باسم: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                try:
                    # تحميل الصورة
                    img_bytes = await attachment.read()
                    img_array = np.asarray(bytearray(img_bytes), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    # تحويل إلى تدرج رمادي
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    # تحليل النص من الصورة
                    text = pytesseract.image_to_string(gray)

                    # تحليل ذكي: (مثال مبسط جدًا — يمكن تطويره لاحقًا)
                    if "up" in text.lower() or "call" in text.lower():
                        decision = "🚀 صعود"
                    elif "down" in text.lower() or "put" in text.lower():
                        decision = "📉 هبوط"
                    else:
                        decision = "⏳ انتظار"

                    await message.channel.send(f"📊 القرار: {decision}")

                except Exception as e:
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة.")
                    traceback.print_exc()

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("❌ فشل تشغيل البوت:")
        traceback.print_exc()
