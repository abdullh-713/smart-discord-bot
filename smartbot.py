import discord
import cv2
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2
from PIL import Image
import numpy as np
import io
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

model = mobilenet_v2(weights='DEFAULT')
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def analyze_market(image):
    img = image.convert("RGB").resize((224, 224))
    input_tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
    prediction = torch.argmax(output).item()
    # ملاحظة: هذه مجرد تمثيل، يجب تدريب النموذج لتوقع السوق فعلياً.
    if prediction % 3 == 0:
        return "📉 النتيجة: هبوط"
    elif prediction % 3 == 1:
        return "📈 النتيجة: صعود"
    else:
        return "⏳ النتيجة: انتظار"

@client.event
async def on_ready():
    print(f"✅ Bot is running as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            image_bytes = await attachment.read()
            image = Image.open(io.BytesIO(image_bytes))
            result = analyze_market(image)
            await message.channel.send(result)

# استخدم متغير البيئة TOKEN لتأمين التوكن
client.run(os.getenv("TOKEN"))
