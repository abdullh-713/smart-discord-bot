import discord
import os
import cv2
import numpy as np
import pytesseract
import torch
import torchvision.transforms as transforms
from PIL import Image
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import MACD
from io import BytesIO

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def preprocess_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    return gray

def extract_candles_and_indicators(gray_image):
    # استخلاص بيانات تحليلية من الصورة (تجريبية - يمكن تحسينها لاحقًا)
    text = pytesseract.image_to_string(gray_image)
    rsi = 50
    macd = 0
    signal = 0
    if "RSI" in text:
        try:
            rsi_val = int(text.split("RSI")[1].split()[0])
            rsi = max(0, min(100, rsi_val))
        except: pass
    if "MACD" in text:
        try:
            macd_val = float(text.split("MACD")[1].split()[0])
            macd = macd_val
        except: pass
    return rsi, macd

def analyze_market(rsi, macd):
    if rsi > 70 and macd > 0:
        return "📉 هبوط"
    elif rsi < 30 and macd < 0:
        return "📈 صعود"
    else:
        return "⏳ انتظار"

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                image_bytes = await attachment.read()
                gray_image = preprocess_image(image_bytes)
                rsi, macd = extract_candles_and_indicators(gray_image)
                decision = analyze_market(rsi, macd)
                await message.channel.send(f"**نتيجة التحليل:**\n{decision}")
                return

    elif message.content.lower() == "ping":
        await message.channel.send("✅ البوت شغال 100%!")

client.run(TOKEN)
