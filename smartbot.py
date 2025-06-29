import discord
import pytesseract
import cv2
import numpy as np
import aiohttp
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# تحليل الصورة لتحديد الاتجاه
def analyze_image_opencv(image_bytes):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        # تحليل أولي بناءً على الكلمات
        text_lower = text.lower()
        if any(x in text_lower for x in ['up', 'bullish', 'buy']):
            return "✅ القرار: صعود 📈"
        elif any(x in text_lower for x in ['down', 'bearish', 'sell']):
            return "❌ القرار: هبوط 📉"
        else:
            return "⏳ القرار: انتظار 📊"
    except Exception as e:
        print("خطأ في التحليل:", e)
        return "❌ حدث خطأ أثناء تحليل الصورة."

# عند تشغيل البوت
@client.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول كبوت: {client.user.name}')

# استقبال الصور وتحليلها
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                image_data = await resp.read()
                                result = analyze_image_opencv(image_data)
                                await message.channel.send(result)
                            else:
                                await message.channel.send("❌ فشل في تحميل الصورة.")
                except Exception as e:
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة.")
                    print("خطأ:", e)

client.run(TOKEN)
