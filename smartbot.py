‏import discord
from discord.ext import commands
from PIL import Image
import io
import torchvision.transforms as transforms
import torch
from torchvision import models
import torch.nn as nn
import torchvision

# إعدادات البوت
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# نموذج الذكاء الصناعي الأساسي (ResNet50)
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 3)  # 3 نواتج: صعود، هبوط، انتظار
model.load_state_dict(torch.load("model_weights.pth", map_location=torch.device('cpu')))
model.eval()

# التحويلات على الصورة
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# قائمة التصنيفات
CLASSES = ['صعود', 'هبوط', 'انتظار']

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كبوت: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                img_data = await attachment.read()
                image = Image.open(io.BytesIO(img_data)).convert('RGB')
                image = transform(image).unsqueeze(0)  # إضافة الباتش
                with torch.no_grad():
                    outputs = model(image)
                    _, predicted = torch.max(outputs, 1)
                    decision = CLASSES[predicted.item()]
                    await message.channel.send(decision)
    await bot.process_commands(message)

# تشغيل البوت
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
