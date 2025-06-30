import os
import asyncio
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# العملات والفريمات
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
timeframes = ["1m", "2m", "5m"]

# إشارات وهمية محفوظة مسبقًا لكل عملة وفريم (تُكرر تلقائيًا)
signals = {
    "EURUSD_1m": ["صعود", "هبوط", "صعود", "صعود", "هبوط"],
    "EURUSD_2m": ["هبوط", "صعود", "هبوط", "صعود", "هبوط"],
    "EURUSD_5m": ["صعود", "صعود", "هبوط", "هبوط", "صعود"],
    "GBPUSD_1m": ["هبوط", "هبوط", "صعود", "صعود", "هبوط"],
    "GBPUSD_2m": ["صعود", "هبوط", "صعود", "هبوط", "صعود"],
    "GBPUSD_5m": ["هبوط", "صعود", "صعود", "هبوط", "هبوط"],
    "USDJPY_1m": ["صعود", "صعود", "هبوط", "هبوط", "صعود"],
    "USDJPY_2m": ["هبوط", "صعود", "هبوط", "صعود", "هبوط"],
    "USDJPY_5m": ["صعود", "هبوط", "صعود", "صعود", "هبوط"]
}

# متغيرات لتتبع الاختيارات
user_symbol = {}
user_timeframe = {}
user_index = {}

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user.name}")

@bot.command()
async def ابدأ(ctx):
    keyboard = [[discord.ui.Button(label=s, style=discord.ButtonStyle.primary)] for s in symbols]
    view = discord.ui.View()
    for row in keyboard:
        for btn in row:
            view.add_item(btn)
            btn.callback = lambda i, s=btn.label: asyncio.create_task(select_symbol(ctx, i, s))
    await ctx.send("🪙 اختر العملة:", view=view)

async def select_symbol(ctx, interaction, symbol):
    user_symbol[ctx.author.id] = symbol
    keyboard = [[discord.ui.Button(label=t, style=discord.ButtonStyle.secondary)] for t in timeframes]
    view = discord.ui.View()
    for row in keyboard:
        for btn in row:
            view.add_item(btn)
            btn.callback = lambda i, t=btn.label: asyncio.create_task(start_signals(ctx, i, t))
    await interaction.response.edit_message(content=f"✅ تم اختيار العملة: `{symbol}`\n⏱ الآن اختر الفريم:", view=view)

async def start_signals(ctx, interaction, timeframe):
    uid = ctx.author.id
    symbol = user_symbol.get(uid)
    tf_key = f"{symbol}_{timeframe}"
    user_timeframe[uid] = tf_key
    user_index[uid] = 0
    await interaction.response.edit_message(content=f"✅ بدأ إرسال الإشارات لـ `{tf_key}` كل 15 ثانية.", view=None)
    send_signal.start(ctx)

@tasks.loop(seconds=15)
async def send_signal(ctx):
    uid = ctx.author.id
    tf_key = user_timeframe.get(uid)
    index = user_index.get(uid, 0)
    if tf_key in signals:
        signal = signals[tf_key][index % len(signals[tf_key])]
        await ctx.send(f"📊 إشـارة ({tf_key}) 👉 `{signal}`")
        user_index[uid] = index + 1
