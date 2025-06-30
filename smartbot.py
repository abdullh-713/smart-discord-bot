import discord
from discord.ext import commands
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models
import json
import datetime
import os

# تحميل جدول الإشارات
with open("full_signal_table.json", "r", encoding="utf-8") as f:
    SIGNAL_TABLE = json.load(f)

# إعدادات البوت
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تحميل نموذج الذكاء الصناعي
model = models.resnet50(pretrained=True)
model.fc = torch.nn.Linear(model.fc.in_features, 3)
model.eval()

# الفئات: 0 = هبوط، 1 = صعود، 2 = انتظار
LABELS = ["هبوط", "صعود", "انتظار"]

# تحويل الصور للإدخال في النموذج
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

@bot.event
async def on_ready():
    print(f"✅ تسجيل الدخول كن {bot.user}")

@bot.command()
async def اشارة(ctx, العملة: str, الفريم: str):
    """يستخرج الإشارة من الجدول"""
    try:
        now = datetime.datetime.utcnow()
        current_time = now.strftime("%H:%M")

        if العملة in SIGNAL_TABLE and الفريم in SIGNAL_TABLE[العملة]:
            for entry in SIGNAL_TABLE[العملة][الفريم]:
                if entry["time"] == current_time:
                    await ctx.send(f"📊 العملة: {العملة}\n⏰ الوقت: {current_time}\n📈 القرار: {entry['decision']}")
                    return
        await ctx.send("❌ لا توجد إشارة حالياً لهذه العملة والفريم.")
    except Exception as e:
        await ctx.send(f"⚠️ خطأ: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(("jpg", "jpeg", "png")):
                await message.channel.send("📥 جاري تحليل الصورة...")
                img_path = f"/tmp/{attachment.filename}"
                await attachment.save(img_path)

                image = Image.open(img_path).convert("RGB")
                image_tensor = transform(image).unsqueeze(0)

                with torch.no_grad():
                    prediction = model(image_tensor)
                    label_index = torch.argmax(prediction, dim=1).item()
                    result = LABELS[label_index]

                await message.channel.send(f"✅ النتيجة: **{result}**")
                os.remove(img_path)
    await bot.process_commands(message)

bot.run(TOKEN)
