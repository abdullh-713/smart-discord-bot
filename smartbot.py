import discord
from discord.ext import commands
from PIL import Image
import io
import cv2
import numpy as np
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    height, width, _ = open_cv_image.shape

    chart_area = open_cv_image[int(height*0.12):int(height*0.70), int(width*0.05):int(width*0.95)]
    rsi_area = open_cv_image[int(height*0.82):int(height*0.89), int(width*0.05):int(width*0.95)]
    stoch_area = open_cv_image[int(height*0.90):int(height*0.97), int(width*0.05):int(width*0.95)]

    # تحليل الشمعة الأخيرة
    last_candle = chart_area[:, -20:]
    avg_color = np.mean(last_candle, axis=(0, 1))
    candle_type = "neutral"
    if avg_color[1] > avg_color[2] + 25:
        candle_type = "bullish"
    elif avg_color[2] > avg_color[1] + 25:
        candle_type = "bearish"

    # تحليل RSI
    rsi_gray = cv2.cvtColor(rsi_area, cv2.COLOR_BGR2GRAY)
    rsi_line = np.mean(rsi_gray, axis=1)
    rsi_gradient = np.gradient(rsi_line)
    rsi_trend = np.mean(rsi_gradient)

    # تحليل Stochastic
    stoch_gray = cv2.cvtColor(stoch_area, cv2.COLOR_BGR2GRAY)
    stoch_line = np.mean(stoch_gray, axis=1)
    stoch_gradient = np.gradient(stoch_line)
    stoch_trend = np.mean(stoch_gradient)

    # ⚖️ منطق متوازن لاتخاذ القرار
    strong_up = rsi_trend > 0.15 and stoch_trend > 0.15
    strong_down = rsi_trend < -0.15 and stoch_trend < -0.15

    if strong_up and candle_type == "bullish":
        return "صعود"
    elif strong_down and candle_type == "bearish":
        return "هبوط"
    elif abs(rsi_trend) < 0.05 and abs(stoch_trend) < 0.05:
        return "انتظار"
    else:
        return "انتظار"

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                img_bytes = await attachment.read()
                result = analyze_image(img_bytes)
                await message.channel.send(result)

# 🔑 التوكن من متغير البيئة (مناسب لـ Railway)
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
