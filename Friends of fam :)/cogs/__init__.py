import discord
import difflib
import json


def setup(bot):
  pass


async def get_data():
  with open('cogs/data.json', 'r') as f:
    data = json.load(f)
  
  with open('cogs/data.json', 'w') as f:
    json.dump(data, data)

  return data

async def set_data(data):
  with open('cogs/data.json', 'w') as f:
    return json.dump(await get_data(), data)


class EmbedCreator:
  async def create_embed(self, title, description, colour, timestamp, *, footer='© Flying Python Studios 2021'):
    em = discord.Embed(title=title, description=description, colour=colour, timestamp=timestamp)

    em.set_footer(text=footer)

    return em

async def get_response_for_query(query):
  data = await get_data()
  matches = dict()

  for q in data.keys():
    if difflib.SequenceMatcher(None, q, query).ratio() > 65:
      matches[difflib.SequenceMatcher(None, q, query).ratio()] = q
    
    sorted(matches.keys())

  if matches is None or matches in ({}):
    return None
  
  for x in matches.items():
    value = x
    break

  return {'results_embed': value}
