import discord
import os
import requests
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from discord.ext import commands
from dotenv import load_dotenv

# تحميل التوكن
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_chart_image(img: Image.Image) -> str:
    np_img = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)

    # استخراج إشارات تحليل بدائية لمحاكاة المؤشرات
    brightness = np.mean(gray)
    contrast = np.std(gray)

    rsi = 70 if brightness > 150 else 30
    macd = 1 if brightness > 135 else -1
    bollinger = "wide" if contrast > 12 else "tight"

    # منطق قرار محترف
    if rsi > 65 and macd > 0 and bollinger == "wide":
        return "⬇️ هبوط"
    elif rsi < 35 and macd < 0 and bollinger == "wide":
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
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    response = requests.get(attachment.url)
                    img = Image.open(BytesIO(response.content))
                    result = analyze_chart_image(img)
                    await message.channel.send(f"📊 التحليل: **{result}**")
                except Exception as e:
                    await message.channel.send(f"❌ فشل التحليل: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
