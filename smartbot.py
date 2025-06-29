import discord
import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import io
import asyncio

# إعداد التوكن من المتغير البيئي
TOKEN = os.getenv("TOKEN")

# إعداد الإنتنتس المطلوبة
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# إنشاء العميل
client = discord.Client(intents=intents)

# التحويل المسبق للصور قبل تمريرها للنموذج
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# تحميل نموذج ذكاء صناعي جاهز (ResNet50 مُعدل)
class ImageClassifier(nn.Module):
    def __init__(self):
        super(ImageClassifier, self).__init__()
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        for param in self.model.parameters():
            param.requires_grad = False
        self.model.fc = nn.Sequential(
            nn.Linear(self.model.fc.in_features, 128),
            nn.ReLU(),
            nn.Linear(128, 3)  # 3 فئات: صعود، هبوط، انتظار
        )

    def forward(self, x):
        return self.model(x)

# إنشاء النموذج وتحميله إلى الجهاز المتاح
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ImageClassifier().to(device)
model.eval()

# دالة توقع القرار
def predict_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)
    prediction = torch.argmax(output, dim=1).item()
    labels = ['صعود 📈', 'هبوط 📉', 'انتظار ⏸️']
    return labels[prediction]

# الاستجابة للصور المرسلة
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
            try:
                image_bytes = await attachment.read()
                result = predict_image(image_bytes)
                await message.channel.send(f"✅ التحليل: **{result}**")
            except Exception as e:
                await message.channel.send("⚠️ حدث خطأ أثناء التحليل.")
                print(e)

# بدء تشغيل البوت
client.run(TOKEN)
