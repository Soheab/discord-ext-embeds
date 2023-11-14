import discord
from discord.ext import commands


bot = commands.Bot(commands.when_mentioned, intents=discord.Intents.all())


@bot.event
async def setup_hook():
    await bot.load_extension("jishaku")


bot.run("NTczNTMxNjk0ODIxNTM5ODUw.GYpOBC.-cN2niOLORipjAn9w3r54VAN-YD9MYx4MJ8Kfc")
