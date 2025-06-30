import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from PIL import Image
import io
import torch
from torchvision import transforms

# استخدم التوكن من متغير بيئي
TOKEN = os.getenv("TOKEN")

# إعدادات التصاريح
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# دالة تحليل وهمية (عدّل لاحقًا لتحليل فعلي)
def analyze_image(tensor):
    return "📈 صعود"  # يمكن تعديلها إلى "📉 هبوط" أو "⏸️ انتظار"

# القائمة الداخلية - مثل Aurix
class AurixMenu(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔍 تحليل مباشر", style=discord.ButtonStyle.success, custom_id="analyze_now")
    async def analyze_now(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("📷 أرسل صورة الشارت الآن وسأحللها فورًا", ephemeral=True)

    @discord.ui.button(label="🛑 إلغاء", style=discord.ButtonStyle.danger, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("✅ تم إلغاء العملية", ephemeral=True)

# تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ Aurix-style bot active as: {bot.user}")

# عند إرسال أي رسالة
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() in ["ابدأ", "start", "/start"]:
        await message.channel.send("🧠 **مرحبًا بك في بوت Aurix**\nاختر من الخيارات التالية:", view=AurixMenu())

    await bot.process_commands(message)

# عند إرسال صورة للتحليل
@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # إذا أرسل صورة
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith((".png", ".jpg", ".jpeg")):
                img_data = await attachment.read()
                image = Image.open(io.BytesIO(img_data)).convert("RGB")

                transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor()
                ])

                img_tensor = transform(image).unsqueeze(0)
                decision = analyze_image(img_tensor)

                await message.channel.send(
                    f"📊 **التحليل التلقائي للصورة**\n"
                    f"📂 القرار النهائي: **{decision}**"
                )
    await bot.process_commands(message)

bot.run(TOKEN)
