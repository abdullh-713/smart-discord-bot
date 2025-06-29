import os
import discord
from discord.ext import commands
import requests
from io import BytesIO
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageClassification
import torch
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("TOKEN")  # تأكد أن متغير البيئة TOKEN موجود في Railway

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل النموذج والمعالج
processor = AutoProcessor.from_pretrained("microsoft/dit-base-finetuned-rvlcdip")
model = AutoModelForImageClassification.from_pretrained("microsoft/dit-base-finetuned-rvlcdip")

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")

@bot.event
async def on_message(message):
    # تجاهل رسائل البوت نفسه
    if message.author == bot.user:
        return

    # إذا احتوت الرسالة على صورة
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    image_url = attachment.url
                    image_data = requests.get(image_url).content
                    image = Image.open(BytesIO(image_data)).convert("RGB")

                    # تجهيز الصورة للنموذج
                    inputs = processor(images=image, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model(**inputs)

                    logits = outputs.logits
                    predicted_class_idx = logits.argmax(-1).item()
                    predicted_label = model.config.id2label[predicted_class_idx]

                    await message.channel.send(f"📊 Prediction: **{predicted_label}**")

                except Exception as e:
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة.")
                    print(f"Error: {e}")

    await bot.process_commands(message)

# تشغيل البوت
bot.run(TOKEN)
