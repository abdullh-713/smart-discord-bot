import discord
import os
import requests
import numpy as np
import pandas as pd
import cv2
from io import BytesIO
from PIL import Image
from discord.ext import commands
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from dotenv import load_dotenv
import torch
from transformers import AutoProcessor, AutoModel

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج ذكاء صناعي مخصص (محليًا أو من huggingface)
processor = AutoProcessor.from_pretrained("nateraw/bert-base-uncased-emotion")
model = AutoModel.from_pretrained("nateraw/bert-base-uncased-emotion")

def analyze_image(img: Image.Image):
    # تحويل الصورة إلى numpy
    img_np = np.array(img.convert("RGB"))

    # استخراج بعض البيانات الأساسية من الصورة
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # افتراض مؤشرات مرئية:
    avg_brightness = np.mean(blur)

    # تحليل بدائي لمحاكاة RSI و Bollinger و MACD (استبداله لاحقاً بالتحليل الذكي من الصورة مباشرة)
    rsi_val = 70 if avg_brightness > 140 else 30
    macd_val = 1 if avg_brightness > 130 else -1
    boll_val = "tight" if np.std(blur) < 10 else "wide"

    # القرار النهائي:
    if rsi_val > 65 and macd_val > 0 and boll_val == "wide":
        return "⬇️ هبوط"
    elif rsi_val < 35 and macd_val < 0 and boll_val == "wide":
        return "⬆️ صعود"
    else:
        return "⏸️ انتظار"

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # إذا كانت الرسالة تحتوي على صورة
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                try:
                    response = requests.get(attachment.url)
                    image = Image.open(BytesIO(response.content))
                    prediction = analyze_image(image)

                    await message.channel.send(f"📉 Prediction: **{prediction}**")
                except Exception as e:
                    await message.channel.send(f"❌ حدث خطأ أثناء التحليل: {e}")

    await bot.process_commands(message)
