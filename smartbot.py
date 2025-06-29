import os
import discord
from discord.ext import commands
import pytesseract
from PIL import Image
import cv2
import numpy as np
import requests
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")  # استخدام المتغير البيئي

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول باسم {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                img_bytes = await attachment.read()
                img_array = np.asarray(bytearray(img_bytes), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)

                # تحليل بسيط — عدل هنا لاحقاً لتفعيل الاستراتيجيات الذكية
                if "green" in text.lower():
                    decision = "✅ القرار: صعود 📈"
                elif "red" in text.lower():
                    decision = "✅ القرار: هبوط 📉"
                else:
                    decision = "✅ القرار: انتظار 📊"

                await message.channel.send(decision)

bot.run(TOKEN)
