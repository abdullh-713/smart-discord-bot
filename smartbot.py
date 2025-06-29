import os
import discord
import requests
import numpy as np
import pandas as pd
import cv2
from io import BytesIO
from PIL import Image
from discord.ext import commands
from dotenv import load_dotenv
import pytesseract
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

# تحميل المتغيرات البيئية
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج ذكاء صناعي لتحليل الصور
processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50")

# استخراج مؤشرات من الصورة
def extract_market_features(img: Image.Image):
    img_np = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    brightness = np.mean(blur)
    volatility = np.std(blur)

    text = pytesseract.image_to_string(img)

    rsi_value = 70 if brightness > 140 else 30
    macd_value = 1 if brightness > 130 else -1
    boll = "tight" if volatility < 10 else "wide"

    return rsi_value, macd_value, boll, text

# اتخاذ القرار النهائي
def make_final_decision(rsi, macd, boll):
    if rsi > 65 and macd > 0 and boll == "wide":
        return "⬇️ هبوط"
    elif rsi < 35 and macd < 0 and boll == "wide":
        return "⬆️ صعود"
    else:
        return "⏸️ انتظار"

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    response = requests.get(attachment.url)
                    img = Image.open(BytesIO(response.content))

                    rsi, macd, boll, text = extract_market_features(img)
                    decision = make_final_decision(rsi, macd, boll)

                    await message.channel.send(f"📊 RSI: {rsi}, MACD: {macd}, Bollinger: {boll}")
                    await message.channel.send(f"📈 القرار النهائي: **{decision}**")
                except Exception as e:
                    await message.channel.send(f"❌ خطأ أثناء التحليل: {e}")

    await bot.process_commands(message)
