import discord
from discord.ext import commands
from PIL import Image
import torchvision.transforms as transforms
import torch
import torch.nn as nn
from torchvision.models import resnet50
import io
import cv2
import numpy as np
import os

# إعداد صلاحيات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج ResNet50 وتعديله لتصنيف (صعود / هبوط فقط)
model = resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)  # فئتان فقط: صعود / هبوط
model.eval()

# تحويل الصور إلى تنسيق مناسب للنموذج
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# خريطة النتائج إلى قرارات
labels_map = {
    0: "📈 صعود",
    1: "📉 هبوط"
}

# تقسيم الصورة إلى مناطق الشموع + المؤشرات
def extract_indicator_regions(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    h, w, _ = img_cv.shape

    # مناطق القص: حسب النسبة المئوية للمؤشرات داخل الصورة
    candles = img_cv[int(0.05*h):int(0.55*h), int(0.1*w):int(0.9*w)]
    rsi     = img_cv[int(0.85*h):int(0.95*h), int(0.1*w):int(0.9*w)]
    macd    = img_cv[int(0.75*h):int(0.85*h), int(0.1*w):int(0.9*w)]
    boll    = img_cv[int(0.05*h):int(0.55*h), int(0.1*w):int(0.9*w)]

    return [candles, rsi, macd, boll]

# تحويل كل جزء إلى تنسيق ResNet وتحليله
def preprocess_region(region):
    image = Image.fromarray(cv2.cvtColor(region, cv2.COLOR_BGR2RGB))
    return transform(image).unsqueeze(0)

# تحليل كل منطقة وإعطاء القرار النهائي
def predict_signal(regions):
    signals = []
    for region in regions:
        tensor = preprocess_region(region)
        with torch.no_grad():
            output = model(tensor)
            _, pred = torch.max(output, 1)
            signals.append(pred.item())

    # خوارزمية التصويت: إذا الأغلبية صعود => صعود
    final = 0 if signals.count(0) > signals.count(1) else 1
    return labels_map[final]

# عند تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# عند استقبال رسالة تحتوي على صورة
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                try:
                    image_bytes = await attachment.read()
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    regions = extract_indicator_regions(image)
                    signal = predict_signal(regions)
                    await message.channel.send(f"🤖 قرار البوت: **{signal}**")
                except Exception as e:
                    await message.channel.send(f"❌ خطأ أثناء التحليل: {str(e)}")

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من متغير البيئة
bot.run(os.getenv("TOKEN"))
