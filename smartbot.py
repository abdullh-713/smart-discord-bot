import discord
import pytesseract
import io
import cv2
import numpy as np
import logging
import os
from dotenv import load_dotenv

# إعدادات
load_dotenv()
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)

@client.event
async def on_ready():
    logging.info(f"✅ تم تسجيل الدخول باسم: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # تحليل الصورة عند إرسال مرفق
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    image_bytes = await attachment.read()
                    image_np = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

                    # تحليل النص من الصورة
                    text = pytesseract.image_to_string(image, lang="eng+ara")

                    # استجابة حسب الكلمات المفتاحية
                    if "صعود" in text or "up" in text:
                        await message.channel.send("✅ القرار: صعود 📈")
                    elif "هبوط" in text or "down" in text:
                        await message.channel.send("🔻 القرار: هبوط 📉")
                    else:
                        await message.channel.send("⏳ لم يتم التعرف على الاتجاه بشكل واضح.")
                except Exception as e:
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة.")
                    logging.error(f"تحليل الصورة فشل: {e}")

client.run(TOKEN)
