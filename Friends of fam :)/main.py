import os
from discord.ext import commands


client = commands.Bot(command_prefix='f.')


@client.event
async def on_ready():
  print('Back online!')


for fn in os.listdir('./cogs'):
  if fn.endswith('.py'):
    client.load_extension(f"cogs.{fn[:-3]}")

client.run(TOKEN)
