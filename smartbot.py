import discord
import os
import requests
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from discord.ext import commands
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحليل بيانات السوق من الصورة (ذكاء مخصص)
def extract_candles_from_image(img: Image.Image):
    # تحويل الصورة إلى numpy (مقاس صغير لتحليل مبدئي)
    img_np = np.array(img.resize((600, 400)).convert("RGB"))

    # تحويل الصورة إلى تدرج رمادي وتطبيق العتبة
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    # افتراض عدد الشموع بناءً على عرض الصورة
    candles = []
    candle_width = 10
    for i in range(60, 540, candle_width + 2):
        candle = gray[100:300, i:i + candle_width]
        avg = np.mean(candle)
        candles.append(avg)

    closes = pd.Series(candles)

    return closes

def analyze_market_image(image: Image.Image):
    closes = extract_candles_from_image(image)
    if len(closes) < 20:
        return "⏸️ انتظار (بيانات غير كافية)"

    df = pd.DataFrame({"close": closes})

    # مؤشرات فنية
    df["rsi"] = RSIIndicator(close=df["close"]).rsi()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    bb = BollingerBands(close=df["close"])
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()

    # آخر القيم
    latest = df.iloc[-1]

    # الشروط
    if latest["rsi"] > 65 and latest["macd"] > 0 and latest["close"] > latest["bb_upper"]:
        return "⬇️ هبوط"
    elif latest["rsi"] < 35 and latest["macd"] < 0 and latest["close"] < latest["bb_lower"]:
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

    # استقبال الصور فقط
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                try:
                    response = requests.get(attachment.url)
                    image = Image.open(BytesIO(response.content))

                    result = analyze_market_image(image)

                    await message.channel.send(f"📉 Prediction: **{result}**")
                except Exception as e:
                    await message.channel.send(f"❌ خطأ في التحليل: {str(e)}")

    await bot.process_commands(message)
