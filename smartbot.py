import os
import discord
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_image(image: Image.Image) -> str:
    """
    تحليل الصورة يدويًا لاستخلاص قرار: صعود، هبوط، انتظار
    بناءً على شكل الشموع + RSI + MACD + Bollinger Bands
    """
    # تحويل الصورة إلى OpenCV
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # استخراج القسم السفلي (المؤشرات)
    h, w, _ = img_cv.shape
    indicators_crop = img_cv[int(h * 0.78):, :]

    # مؤقتًا: استخدام اللون لتقدير الاتجاه (تحليل بدائي كمثال)
    green_pixels = np.sum(np.all(indicators_crop > [0, 180, 0], axis=-1))
    red_pixels = np.sum(np.all(indicators_crop > [180, 0, 0], axis=-1))

    if green_pixels > red_pixels * 1.5:
        return "📈 صعود"
    elif red_pixels > green_pixels * 1.5:
        return "📉 هبوط"
    else:
        return "⏳ انتظار"

@bot.event
async def on_ready():
    print(f"✅ Bot is running as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                try:
                    image_bytes = await attachment.read()
                    image = Image.open(BytesIO(image_bytes))
                    result = analyze_image(image)
                    await message.channel.send(f"📊 Prediction: **{result}**")
                except Exception as e:
                    await message.channel.send(f"❌ Error: {str(e)}")

    await bot.process_commands(message)
