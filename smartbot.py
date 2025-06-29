import discord
import os
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from dotenv import load_dotenv
import hashlib
from datetime import datetime

# تحميل المتغيرات البيئية
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعدادات Discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# قاعدة بيانات بسيطة للصور المُعالجة
processed_hashes = {}

# تحميل نموذج ذكاء صناعي مُدرب مسبقًا
model = models.resnet50(pretrained=True)
model.eval()

# تصنيفات وهمية: 0 = هبوط، 1 = صعود
labels = ["هبوط", "صعود"]

# تحويل الصور إلى شكل يمكن للنموذج قراءته
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# دالة التحقق من تكرار الصورة
def is_duplicate(image_bytes):
    image_hash = hashlib.md5(image_bytes).hexdigest()
    current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
    if processed_hashes.get(current_minute) == image_hash:
        return True
    processed_hashes[current_minute] = image_hash
    return False

# دالة تحليل الصورة وإعطاء القرار
def predict_image(image_bytes):
    image = Image.open(image_bytes).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)

    return labels[predicted.item()]

# عند تشغيل البوت
@client.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كبوت: {client.user}")

# عند استقبال رسالة
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                try:
                    image_bytes = await attachment.read()

                    if is_duplicate(image_bytes):
                        await message.channel.send("⚠️ تم تجاهل صورة مكررة أو تم إرسالها قبل انتهاء الوقت.")
                        return

                    decision = predict_image(image_bytes=Image.open(io.BytesIO(image_bytes)))
                    await message.channel.send(f"📈 القرار: **{decision}**")

                except Exception as e:
                    await message.channel.send(f"حدث خطأ أثناء تحليل الصورة ❌: {str(e)}")

# تشغيل البوت
client.run(TOKEN)
