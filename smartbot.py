import discord
from discord.ext import commands
from PIL import Image
import pytesseract
import io
import re
import os

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user.name}")

def analyze_chart(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    decision = "🕐 القرار: انتظار"

    if "rsi" in text.lower() or "stoch" in text.lower():
        if re.search(r"(70|80)[\s%]*", text.lower()):
            decision = "❌ القرار: هبوط"
        elif re.search(r"(20|30)[\s%]*", text.lower()):
            decision = "✅ القرار: صعود"

    if text.lower().count("green") >= 3:
        decision = "✅ القرار: صعود"
    elif text.lower().count("red") >= 3:
        decision = "❌ القرار: هبوط"

    return decision

@bot.event
async def on_message(message):
    if message.author.bot or not message.attachments:
        return

    for attachment in message.attachments:
        if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_bytes = await attachment.read()
            decision = analyze_chart(image_bytes)
            await message.channel.send(decision)

bot.run(TOKEN)
