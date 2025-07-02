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

    decision = "انتظار"

    # مناطق التحليل من الصورة
    chart_area = open_cv_image[int(height*0.10):int(height*0.70), int(width*0.05):int(width*0.95)]
    rsi_area   = open_cv_image[int(height*0.82):int(height*0.89), int(width*0.05):int(width*0.95)]
    stoch_area = open_cv_image[int(height*0.90):int(height*0.97), int(width*0.05):int(width*0.95)]

    # تحليل RSI
    rsi_gray = cv2.cvtColor(rsi_area, cv2.COLOR_BGR2GRAY)
    rsi_avg = np.mean(rsi_gray)
    rsi_signal = "neutral"
    if rsi_avg > 170:
        rsi_signal = "overbought"
    elif rsi_avg < 85:
        rsi_signal = "oversold"

    # تحليل Stochastic
    stoch_gray = cv2.cvtColor(stoch_area, cv2.COLOR_BGR2GRAY)
    stoch_avg = np.mean(stoch_gray)
    stoch_signal = "neutral"
    if stoch_avg > 160:
        stoch_signal = "overbought"
    elif stoch_avg < 90:
        stoch_signal = "oversold"

    # تحليل آخر شمعة
    candle_col = chart_area[:, -20:]
    candle_color = np.mean(candle_col, axis=(0, 1))
    last_candle = "neutral"
    if candle_color[2] > candle_color[1] + 30:
        last_candle = "bearish"
    elif candle_color[1] > candle_color[2] + 30:
        last_candle = "bullish"

    # Bollinger Bands (مقاومة ودعم)
    top_band_pixel = chart_area[5, -10]
    bottom_band_pixel = chart_area[-5, -10]
    current_pixel = chart_area[chart_area.shape[0]//2, -10]

    touch_top = np.linalg.norm(current_pixel - top_band_pixel) < 40
    touch_bottom = np.linalg.norm(current_pixel - bottom_band_pixel) < 40

    bb_signal = "neutral"
    if touch_top and last_candle == "bearish":
        bb_signal = "resistance_reject"
    elif touch_bottom and last_candle == "bullish":
        bb_signal = "support_bounce"

    # Moving Average
    ma_row = chart_area[chart_area.shape[0]//2, -20:]
    ma_color = np.mean(ma_row, axis=0)
    if ma_color[0] > 200 and ma_color[1] > 200:
        ma_signal = "above"
    elif ma_color[0] < 100 and ma_color[1] < 100:
        ma_signal = "below"
    else:
        ma_signal = "neutral"

    # الاستراتيجية الذكية النهائية
    if rsi_signal == "oversold" and stoch_signal == "oversold" and bb_signal == "support_bounce" and ma_signal == "above":
        decision = "صعود"
    elif rsi_signal == "overbought" and stoch_signal == "overbought" and bb_signal == "resistance_reject" and ma_signal == "below":
        decision = "هبوط"
    elif rsi_signal == "oversold" and last_candle == "bullish" and ma_signal == "above":
        decision = "صعود"
    elif rsi_signal == "overbought" and last_candle == "bearish" and ma_signal == "below":
        decision = "هبوط"
    elif bb_signal == "support_bounce" and ma_signal == "above":
        decision = "صعود"
    elif bb_signal == "resistance_reject" and ma_signal == "below":
        decision = "هبوط"
    else:
        decision = "انتظار"

    return decision

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                img_bytes = await attachment.read()
                result = analyze_image(img_bytes)
                await message.channel.send(result)

# ✅ استخدام التوكن من متغير بيئة (مناسب لـ Railway)
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
