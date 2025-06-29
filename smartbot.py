import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io
import aiohttp

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول باسم: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # تحليل الصور فقط في القنوات وليس الرسائل الخاصة
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                try:
                    img_bytes = await attachment.read()
                    np_arr = np.frombuffer(img_bytes, np.uint8)
                    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                    if img is None:
                        await message.channel.send("❌ حدث خطأ أثناء قراءة الصورة.")
                        return

                    # تحويل الصورة إلى رمادية ثم OCR
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(gray)

                    # تحليل تجريبي بسيط للنص من الصورة (تعديل حسب استراتيجيتك)
                    if "call" in text.lower() or "صعود" in text:
                        result = "✅ القرار: صعود 📈"
                    elif "put" in text.lower() or "هبوط" in text:
                        result = "🔻 القرار: هبوط 📉"
                    else:
                        result = "⚠️ لم يتم تحديد اتجاه واضح من الصورة."

                    await message.channel.send(result)

                except Exception as e:
                    print("❌ خطأ:", e)
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة.")
    await bot.process_commands(message)
