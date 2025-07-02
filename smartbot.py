‏import discord
import os
import cv2
import numpy as np
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def analyze_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "❌ صورة غير صالحة"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    red_mask = cv2.inRange(hsv, (0, 60, 50), (10, 255, 255)) | cv2.inRange(hsv, (170, 60, 50), (180, 255, 255))

    rsi_area = gray[450:470, 50:250]
    rsi_val = np.mean(rsi_area)

    bb_area = gray[100:120, 50:250]
    bb_std = np.std(bb_area)

    stochastic_area = gray[300:320, 50:250]
    stochastic_val = np.mean(stochastic_area)

    green_strength = cv2.countNonZero(green_mask)
    red_strength = cv2.countNonZero(red_mask)
    white_area = cv2.countNonZero(cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1])

    score_up = 0
    score_down = 0

    if green_strength > red_strength and white_area > 10000:
        score_up += 1
    if red_strength > green_strength and white_area > 10000:
        score_down += 1

    if rsi_val < 90:
        score_down += 1
    if rsi_val > 140:
        score_up += 1

    if bb_std > 20:
        score_up += 1
    if bb_std < 10:
        score_down += 1

    if stochastic_val > 130:
        score_down += 1
    if stochastic_val < 100:
        score_up += 1

    if score_up >= 3:
        return "🔼 صعود"
    elif score_down >= 3:
        return "🔽 هبوط"
    else:
        return "⏸ انتظار"

@bot.event
async def on_message(message):
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = f"temp_{attachment.filename}"
                await attachment.save(path)

                result = analyze_image(path)
                await message.channel.send(result)
                os.remove(path)

    await bot.process_commands(message)

bot.run(TOKEN)
