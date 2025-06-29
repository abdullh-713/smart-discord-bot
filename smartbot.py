import discord
from discord.ext import commands
from PIL import Image
import torchvision.transforms as transforms
import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights
import io
import asyncio
import os
import hashlib

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج ResNet50 مع أحدث weights
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.fc = nn.Linear(model.fc.in_features, 2)  # فقط صعود / هبوط
model.eval()

# تحويل الصورة إلى تنسيق مناسب
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# خريطة النتائج إلى قرارات
labels_map = {
    0: "📈 صعود",
    1: "📉 هبوط"
}

# تخزين آخر صورة تم تحليلها لتجنب التكرار
last_image_hash = None

def calculate_hash(image_bytes):
    return hashlib.md5(image_bytes).hexdigest()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global last_image_hash

    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    # قراءة الصورة وحساب البصمة
                    image_bytes = await attachment.read()
                    current_hash = calculate_hash(image_bytes)

                    # تجاهل الصور المكررة
                    if current_hash == last_image_hash:
                        return
                    last_image_hash = current_hash

                    # فتح الصورة وتحليلها
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    input_tensor = transform(image).unsqueeze(0)

                    with torch.no_grad():
                        output = model(input_tensor)
                        _, predicted = torch.max(output, 1)
                        label = labels_map[predicted.item()]

                    # إرسال قرار البوت
                    await message.channel.send(f"🤖 قرار البوت: **{label}**")

                except Exception as e:
                    await message.channel.send(f"❌ خطأ أثناء التحليل: {str(e)}")

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من متغير البيئة
bot.run(os.getenv("TOKEN"))
