import os
import discord
from discord.ext import commands
from PIL import Image
import numpy as np
import cv2
import io
import time
import torch
import torchvision.transforms as transforms
from torchvision import models

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج ResNet المدرب مسبقاً
model = models.resnet50(pretrained=True)
model.eval()

# تحويل الصور إلى تنسيق مناسب للنموذج
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# لتخزين توقيع آخر صورة تم تحليلها
last_image_signature = None
last_analysis_time = 0
min_analysis_interval = 4  # ثواني بين كل تحليل

# قطع الجزء الأيمن من الصورة (منطقة الشموع الأخيرة)
def extract_last_segment(image):
    width, height = image.size
    cropped = image.crop((int(width * 0.8), 0, width, height))
    return cropped

# توليد توقيع بسيط للصورة لتحديد التكرار
def generate_signature(image):
    image = image.convert("L").resize((20, 20))
    return np.array(image).flatten()

# التحقق إذا كانت الصورة جديدة أو مكررة
def should_analyze(new_image):
    global last_image_signature, last_analysis_time
    current_time = time.time()
    if current_time - last_analysis_time < min_analysis_interval:
        return False
    segment = extract_last_segment(new_image)
    new_signature = generate_signature(segment)
    if last_image_signature is not None:
        diff = np.sum(np.abs(new_signature - last_image_signature))
        if diff < 100:
            return False
    last_image_signature = new_signature
    last_analysis_time = current_time
    return True

# تحليل الصورة باستخدام نموذج الذكاء الصناعي
def analyze_image(image):
    img = image.convert("RGB")
    img_tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        output = model(img_tensor)
    _, predicted = torch.max(output, 1)
    index = predicted.item()
    if index % 3 == 0:
        return "📉 التحليل: هبوط ✅"
    elif index % 3 == 1:
        return "📈 التحليل: صعود ✅"
    else:
        return "⏸️ التحليل: انتظار ✅"

# التعامل مع الصور المرسلة في الديسكورد
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                image_bytes = await attachment.read()
                image = Image.open(io.BytesIO(image_bytes))
                if should_analyze(image):
                    result = analyze_image(image)
                    await message.channel.send(result)
                else:
                    print("تم تجاهل صورة مكررة أو تم إرسالها قبل انتهاء الوقت.")

# تشغيل البوت
bot.run(os.getenv("TOKEN"))
