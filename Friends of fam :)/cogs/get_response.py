import asyncio
import discord
from cogs import EmbedCreator, get_response_for_query, Core
from discord.ext import commands


class Core(commands.Cog, EmbedCreator, Core):
  """The core features of the bot"""

  def __init__(self, bot):
    self.bot = bot
  
  @commands.Cog.listener()
  async def on_message(self, message, *, start_modmail=None, opened=None, user=None):
    if start_modmail:
      overwrites = {
    message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    message.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True),
    message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
}
      if user:
        for category in message.guild.categories:
          if str(category.name) == 'Modmail':
            for ch in category.channels:
              if ch.name == f'{user.name}-{user.discriminator}':
                return

            await category.create_text_channel(name=f'{user.name}-{user.discriminator}', overwrites=overwrites)
      
        msg = await message.channel.send(embed=await self.create_embed(title='A new modmail ticket!', description=f'Ticket opened by {opened.display_name}!', colour=discord.Colour.green(), timestamp=message.created_at))

        return await msg.pin()
      
      for category in message.guild.categories:
        if str(category.name) == 'Modmail':
          for ch in category.channels:
            if ch.name == f'{message.author.name}-{message.author.discriminator}':
              return
              
          channel = await category.create_text_channel(name=f'{message.author.name}-{message.author.discriminator}', overwrites=overwrites)
      
      msg = await channel.send(embed=await self.create_embed(title='A new modmail ticket!', description=f'Ticket opened by {opened.display_name}!', colour=discord.Colour.green(), timestamp=message.created_at))

      await msg.pin()

    else:
      await self.bot.process_commands(message)

  @commands.command(name='query', aliases=['question'])
  async def query(self, ctx, *, query=None):
    if query is None:
      return await ctx.send(embed=await self.create_embed(title='Query not found', description='Please provide your query after this command.', colour=discord.Colour.red(), timestamp=ctx.message.created_at))

    response = await get_response_for_query(query=query)
    
    if response is None:
      return await ctx.send(embed=await self.create_embed(title='Matching response not found', description='A matching response for your query was not found amongst our data.', colour=discord.Colour.red(), timestamp=ctx.message.created_at))
    
    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel
    
    await ctx.send(embed=await self.create_embed(title='Mathcing responses for your query', description='Check whether your query is answered here: \n\n ' + response['results_embed'] + '\n\nKindly enter `y` if your query is solved or `n` if your query is not solved.', colour=discord.Colour.red(), timestamp=ctx.message.created_at))

    try:
      msg = await self.bot.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
      return await ctx.send(ctx.author.mention, embed=await self.create_embed(title='Timed out!', description='You took too long to respond to this one, be quick next time!', colour=discord.Colour.red(), timestamp=ctx.message.created_at))

      if msg.content not in ('y', 'n'):
              return await ctx.send(embed=await self.create_embed(title='Invalid response!', description='Enter only `y` or `n`', colour=discord.Colour.red(), timestamp=ctx.message.created_at))
      
      if msg.content == 'n':
              await ctx.send(embed=await self.create_embed(title='Redirecting...', description='We are sorry that our AI service was unable to answer your query. You are being redirected to the modmail for our server staff to deal with your query...', colour=discord.Colour.red(), timestamp=ctx.message.created_at))

              await self.on_message(ctx.message, start_modmail=True)

      return await ctx.send(embed=await self.create_embed(title='Thank you!', description='We are happy that our AI service was able to deal and answer you with your question!', colour=discord.Colour.green(), timestamp=ctx.message.created_at))
  
  @commands.command(name='modmail', aliases=['ticket'])
  async def modmail(self, ctx, *, member: discord.Member=None):
    if member is not None:
      if not ctx.channel.permissions_for(ctx.author).manage_channels:
        return await ctx.send(embed=await self.create_embed(title='Missing permissions!', description='You dont have enough permissions to do that option!', colour=discord.Colour.red(), timestamp=ctx.message.created_at))
      else:
        await ctx.send(embed=await self.create_embed(title=f'Opening a ticket for {member.display_name}...', 
        description='This would usally take about 5 - 10 seconds.', colour=discord.Colour.green(), timestamp=ctx.message.created_at))
        
        overwrites = {          
          ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
          ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True),
          ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
          }
        
        for category in ctx.message.guild.categories:
            if str(category.name) == 'Modmail':
              for ch in category.channels:
                if ch.name == f'{member.name}-{member.discriminator}':
                  return

              ch = await category.create_text_channel(name=f'{member.name}-{member.discriminator}', overwrites=overwrites)
        
              msg = await ch.send(embed=await self.create_embed(title='A new ticket!', description=f'Ticket opened by {ctx.author.display_name}!', colour=discord.Colour.green(), timestamp=ctx.message.created_at))

              return await msg.pin()

    await ctx.send(embed=await self.create_embed(title='Opening a ticket for you...', 
    description='This would usally take about 5 - 10 seconds.', colour=discord.Colour.green(), timestamp=ctx.message.created_at))

    await self.on_message(ctx.message, start_modmail=True, opened=ctx.author)
  
  @commands.command(name='close')
  async def close(self, ctx):
    if str(ctx.channel.category.name) == 'Modmail':
      return await ctx.channel.delete()
  
  @commands.command(name='answer')
  async def answer(self, ctx, q, *, answer):
    await self.update(q, answer)
    await ctx.send('Done!')

def setup(bot):
  bot.add_cog(Core(bot))
