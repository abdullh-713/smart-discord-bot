import discord
import io
from PIL import Image
import random
import os

# استخدم التوكن من المتغير البيئي
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# نموذج تحليل الصور (تجريبي)
def analyze_image(image: Image.Image) -> str:
    # هنا يمكنك استخدام نموذج حقيقي لتحليل المؤشرات والشموع والثغرات
    # حالياً نستخدم اختيار عشوائي للمحاكاة
    decision = random.choice(["صعود", "هبوط", "انتظار"])
    return decision

@client.event
async def on_ready():
    print(f"✅ البوت جاهز. اسم المستخدم: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                try:
                    img_bytes = await attachment.read()
                    img = Image.open(io.BytesIO(img_bytes))

                    decision = analyze_image(img)

                    await message.channel.send(f"📊 القرار: **{decision}** ✅")

                except Exception as e:
                    await message.channel.send(f"❌ حدث خطأ أثناء تحليل الصورة: {str(e)}")

client.run(TOKEN)
