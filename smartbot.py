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

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل النموذج المدرب مسبقًا باستخدام الطريقة الحديثة
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.fc = nn.Linear(model.fc.in_features, 2)  # فقط صعود أو هبوط
model.eval()

# تحويل الصورة إلى تنسيق مناسب للنموذج
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# خريطة النتائج إلى القرارات
labels_map = {
    0: "📈 صعود",
    1: "📉 هبوط"
}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    # قراءة وتحليل الصورة
                    image_bytes = await attachment.read()
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    input_tensor = transform(image).unsqueeze(0)

                    with torch.no_grad():
                        output = model(input_tensor)
                        _, predicted = torch.max(output, 1)
                        label = labels_map[predicted.item()]

                    # إرسال القرار
                    await message.channel.send(f"🤖 قرار البوت: **{label}**")
                    await asyncio.sleep(0.5)  # تأخير بسيط لتفادي التداخل

                except Exception as e:
                    await message.channel.send(f"❌ خطأ أثناء التحليل: {str(e)}")

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من متغير البيئة
bot.run(os.getenv("TOKEN"))
