import os
import io  # ✅ إصلاح الخطأ هنا
import discord
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models import resnet50, ResNet50_Weights
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import warnings

warnings.filterwarnings("ignore")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# تحميل النموذج المدرب مسبقًا ResNet50
model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def extract_features(image):
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = model(img_tensor)
    return features.numpy().flatten()

def analyze_with_indicators(img_array):
    try:
        prices = np.mean(img_array, axis=2).mean(axis=1)  # تحويل الصورة إلى بيانات سعرية تقريبية

        rsi = RSIIndicator(pd.Series(prices)).rsi().fillna(0)
        macd = MACD(pd.Series(prices)).macd_diff().fillna(0)
        bb = BollingerBands(pd.Series(prices)).bollinger_mavg().fillna(0)

        signals = []

        if rsi.iloc[-1] < 30 and macd.iloc[-1] > 0 and prices[-1] < bb.iloc[-1]:
            signals.append("صعود")
        elif rsi.iloc[-1] > 70 and macd.iloc[-1] < 0 and prices[-1] > bb.iloc[-1]:
            signals.append("هبوط")

        if not signals:
            signals.append("صعود" if macd.iloc[-1] > 0 else "هبوط")

        return signals[-1]

    except Exception as e:
        print(f"Error in analyze_with_indicators: {e}")
        return None

@client.event
async def on_ready():
    print(f'✅ تسجيل الدخول كمستخدم: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or not message.attachments:
        return

    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
            try:
                image_bytes = await attachment.read()
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

                img_array = np.array(image)
                decision = analyze_with_indicators(img_array)

                if decision:
                    await message.channel.send(f"✅ التحليل: {decision}")
                else:
                    await message.channel.send("❌ لم يتمكن البوت من اتخاذ قرار واضح")

            except Exception as e:
                await message.channel.send(f"❌ حدث خطأ أثناء تحليل الصورة: {e}")

# قراءة التوكن من متغير بيئي
TOKEN = os.getenv("TOKEN")
if TOKEN:
    client.run(TOKEN)
else:
    print("❌ لم يتم العثور على التوكن. تأكد من تعيين متغير البيئة TOKEN.")
