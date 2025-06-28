import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة العملات OTC
OTC_SYMBOLS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AED/CNY OTC",
    "MAD/USD OTC", "USD/RUB OTC", "USD/EGP OTC", "USD/INR OTC"
]

TIMEFRAMES = ["S5", "S10", "S15", "M1", "M2", "M5", "M10"]
DURATIONS = ["15s", "30s", "1m", "2m", "3m"]

user_choices = {}  # تخزين اختيارات المستخدم مؤقتًا

@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(name="trade", description="ابدأ تحديد العملة والفريم والمدة")
async def trade_command(interaction: discord.Interaction):
    view = TradeView()
    await interaction.response.send_message("اختر إعدادات الصفقة:", view=view, ephemeral=True)

class TradeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(discord.ui.Select(
            placeholder="اختر عملة OTC",
            options=[discord.SelectOption(label=symbol) for symbol in OTC_SYMBOLS],
            custom_id="symbol_select"
        ))
        self.add_item(discord.ui.Select(
            placeholder="اختر الفريم الزمني",
            options=[discord.SelectOption(label=tf) for tf in TIMEFRAMES],
            custom_id="timeframe_select"
        ))
        self.add_item(discord.ui.Select(
            placeholder="اختر مدة الصفقة",
            options=[discord.SelectOption(label=dur) for dur in DURATIONS],
            custom_id="duration_select"
        ))
        self.add_item(discord.ui.Button(label="ابدأ التحليل الذكي", style=discord.ButtonStyle.success, custom_id="start_analysis"))

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        cid = interaction.data["custom_id"]
        user_id = interaction.user.id

        if user_id not in user_choices:
            user_choices[user_id] = {}

        if cid == "symbol_select":
            user_choices[user_id]["symbol"] = interaction.data["values"][0]
            await interaction.response.send_message(f"✅ تم اختيار العملة: {interaction.data['values'][0]}", ephemeral=True)

        elif cid == "timeframe_select":
            user_choices[user_id]["timeframe"] = interaction.data["values"][0]
            await interaction.response.send_message(f"✅ تم اختيار الفريم: {interaction.data['values'][0]}", ephemeral=True)

        elif cid == "duration_select":
            user_choices[user_id]["duration"] = interaction.data["values"][0]
            await interaction.response.send_message(f"✅ تم اختيار المدة: {interaction.data['values'][0]}", ephemeral=True)

        elif cid == "start_analysis":
            data = user_choices.get(user_id, {})
            if "symbol" in data and "timeframe" in data and "duration" in data:
                await interaction.response.send_message(f"🚀 بدء التحليل:\n- العملة: {data['symbol']}\n- الفريم: {data['timeframe']}\n- المدة: {data['duration']}", ephemeral=False)
            else:
                await interaction.response.send_message("❌ الرجاء اختيار جميع الإعدادات أولًا.", ephemeral=True)

bot.run("YOUR_TOKEN_HERE")  # ضع التوكن هنا أو اجعلها من المتغيرات
