import os
import discord
import requests
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from transformers import ViTImageProcessor, ViTForImageClassification

# إعدادات Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# تحميل النموذج والمعالج
processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # إذا تم إرسال صورة
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                try:
                    image_url = attachment.url
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content)).convert("RGB")

                    inputs = processor(images=image, return_tensors="pt")
                    with torch.no_grad():
                        outputs = model(**inputs)
                        logits = outputs.logits
                        predicted_class_idx = logits.argmax(-1).item()
                        predicted_label = model.config.id2label[predicted_class_idx]

                    await message.channel.send(f"📊 Prediction: **{predicted_label}**")
                except Exception as e:
                    await message.channel.send(f"❌ Error: {e}")

# تشغيل البوت
if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ TOKEN environment variable not found.")
