import discord
from discord.ext import commands
from PIL import Image
import torchvision.transforms as transforms
import torch
import torch.nn as nn
from torchvision.models import resnet50
import io
import os

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج ResNet50 مدرب مسبقاً وتحويله لفئتين (صعود / هبوط)
model = resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)
model.eval()

# تحويل الصورة إلى تنسيق مناسب للنموذج
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# خريطة النتائج
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
                    # قراءة الصورة وتحويلها
                    image_bytes = await attachment.read()
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    input_tensor = transform(image).unsqueeze(0)

                    # توقع باستخدام النموذج
                    with torch.no_grad():
                        output = model(input_tensor)
                        _, predicted = torch.max(output, 1)
                        label = labels_map[predicted.item()]

                    await message.channel.send(f"🤖 قرار البوت: **{label}**")

                except Exception as e:
                    await message.channel.send(f"❌ خطأ في التحليل: {str(e)}")

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من المتغير البيئي
bot.run(os.getenv("TOKEN"))
