import os
import random
import csv
import json
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from huachiapi import Huachiapi
import redis
import random

intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!', intents=intents)
allowed_roles = ['Admin']

try:
    redis_db = redis.StrictRedis(host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True)
    token = redis_db.get('DISCORD_BOT_TOKEN')
    allowed_roles = allowed_roles +  json.loads(redis_db.get('ALLOWED_ROLES'))
except Exception as e:
    print("no redis!")
    token = (os.environ['DISCORD_BOT_TOKEN'] if 'DISCORD_BOT_TOKEN' in os.environ else '')


api = Huachiapi()


AF_DET= './txt/afecto_detonador.txt'
AF_RESP = './txt/afecto_respuesta.txt'
RESP_DEF = './txt/respuestas_por_defecto.txt'
REPLIES = './txt/contestaciones.csv'
CHAT_REPLIES = './txt/chat_detonador.csv'


def load_replies(file):
    SORTS = dict()

    for row in csv.DictReader(open(file, "r", encoding="utf-8")):
        SORTS[row["detonador"]] = row["respuesta"]

    return SORTS


def load_file(file):
    """Load the log file and creates it if it doesn't exist.

     Parameters
    ----------
    file : str
        The file to write down
    Returns
    -------
    list
        A list of urls.

    """

    try:
        with open(file, 'r', encoding='utf-8') as temp_file:
            return temp_file.read().splitlines()
    except Exception:

        with open(LOG_FILE, 'w', encoding='utf-8') as temp_file:
            return []


def _get_any_dict(items, key_search):
    for item in list(items.keys()):
        if item in key_search:
            return items[item]
    return None


_af_det = load_file(AF_DET)
_af_resp = load_file(AF_RESP)
_def_resp = load_file(RESP_DEF)
_replies = load_replies(REPLIES)
_chat_replies = load_replies(CHAT_REPLIES)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="en la otra caja le atienden"))


@bot.command(name='server',pass_context=True)
@commands.has_permissions(administrator=True)
async def fetchServerInfo(context):
    guild = context.guild

    await context.send(f'Server Name: {guild.name}')
    await context.send(f'Server Size: {len(guild.members)}')
    await context.send(f'Server Name: {guild.owner.display_name}')


@bot.command(name='limpiar',pass_context=True)
@commands.has_permissions(administrator=True)
async def clear(context, amount=None):
    if amount is None:
        await context.channel.purge(limit=5)
    elif amount == "all":
        await context.channel.purge()
    else:
        await context.channel.purge(limit=int(amount))
    await context.send("Listo Jefe ;)")

@bot.command(name='saldazo')
async def getSaldazo(context):
    response = api.saldazo(None)
    await context.send(response)


@bot.command(name='shop')
@commands.has_any_role(*allowed_roles)
async def doShop(context, *args):
    try:
        response = api.shop(args[0])
    except:
        response = api.shop(None)
    await context.send(response)

@bot.command(name='tip')
async def doTip(context):
    response = api.tip(None)
    await context.send(response)

@bot.command(name='role')
@commands.has_any_role("Admin","Testigo de la Crepa") #permissions
async def role(ctx, user : discord.Member, *, role : discord.Role):
  if role.position > ctx.author.top_role.position: #if the role is above users top role it sends error
    return await ctx.send('**:x: | Este rol es superior al tuyo!**') 
  if role in user.roles:
      await user.remove_roles(role) #removes the role if user already has
      await ctx.send(f"Removido {role} de {user.mention}")
  else:
      await user.add_roles(role) #adds role if not already has it
      await ctx.send(f"Añadido {role} a {user.mention}") 


@bot.command(name='atraco')
@commands.has_any_role("Admin","Testigo de la Crepa") #permissions
async def atraco(context):

    if context.message.reference is None:
        await context.send("Ni robar sabes wey!!")
        return

    print(context.message.reference.message_id)

    reference_msg = await context.fetch_message(context.message.reference.message_id)

    try:
        victim = reference_msg.author.id
        print(victim)
        if victim == bot.user.id:
            response = "A mi no me robas wey!!"
        elif victim == context.author.id:
            response = "No te puedes robar a ti mismo wey!!"
        else:
            currency_string = "${:,.2f}".format(float(random.randrange(0, 1999)))
            response = "{} robó {} <:huachi:809238593696432200> de la cartera de {}".format(context.author.mention, currency_string, reference_msg.author.mention)
        await context.send(response)
    except Exception as e:
        print(e)


@bot.event
async def on_member_join(member):
    try:
        channel = bot.get_channel(821542780730998844)
        await channel.send("<:f_apunta_michi:821874920945352725><:f_apunta_michi:821874920945352725><:f_apunta_michi:821874920945352725><:f_apunta_michi:821874920945352725><:f_apunta_michi:821874920945352725><:f_apunta_michi:821874920945352725>")
    except Exception as e:
        print(e)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # we do not want the bot to reply to itself
    if message.author.id == bot.user.id:
        return
    if message.content.startswith("!"):
        return

    chance = random.randrange(0, 9999999)

    if (chance > 9999990):
        channel = bot.get_channel(821542780730998844)
        await channel.send("https://cdn.discordapp.com/attachments/821542780730998844/869682132316995635/image0-1-1-1-1-1.png")
    

    #print(message.content)
    if bot.user.mentioned_in(message):
        if any(map(message.content.lower().__contains__, _af_det)):
            resp = random.choice(_af_resp)
            await message.channel.send(resp)
        elif resp := _get_any_dict(_replies, message.content.lower()):
            await message.channel.send(resp)
        else:
            resp = random.choice(_def_resp)
            await message.channel.send(resp)
    else:
        if resp := _get_any_dict(_chat_replies, message.content.lower()):
            await message.channel.send(resp)

bot.run(token)
