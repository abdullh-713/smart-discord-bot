import discord
import cv2
import numpy as np
from PIL import Image
import io
import os
import torchvision.transforms as transforms
import torch
import torchvision.models as models

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # مهم جدًا

client = discord.Client(intents=intents)

# نموذج ذكاء صناعي مدرب مسبقًا (ResNet50 كمثال)
model = models.resnet50(pretrained=True)
model.eval()

# التحويلات على الصورة
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def analyze_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image_tensor)

    # فقط كمثال — لا تعتمد على هذه القيم لتحليل السوق الحقيقي
    prediction_score = torch.nn.functional.softmax(outputs[0], dim=0)
    confidence, predicted_class = torch.max(prediction_score, dim=0)

    # تحليل مبسط يعتمد على العشوائية — استبدله بتحليل حقيقي لاحقًا
    if predicted_class.item() % 3 == 0:
        return "📉 هبوط"
    elif predicted_class.item() % 3 == 1:
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

    # في حال وجود مرفقات (صور)
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                try:
                    image_bytes = await attachment.read()
                    result = analyze_image(image_bytes)
                    await message.channel.send(f"📊 النتيجة: **{result}**")
                except Exception as e:
                    await message.channel.send("❌ حدث خطأ أثناء تحليل الصورة")
                    print(e)

# تشغيل البوت
client.run(os.getenv("TOKEN"))
