
import discord
from discord.ext import commands
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

cliente_groq = Groq(api_key=os.getenv('GROQ_API_KEY'))

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

if os.path.exists("levels.json"):
    with open("levels.json", "r") as file:
        levels = json.load(file)
else:
    levels = {}
historial = {}

def guardar():
    with open("levels.json", "w") as file:
        json.dump(levels, file, indent=4)


@bot.command()
async def sendGeneral(ctx, *args):
    channel = bot.get_channel(1506526443541233807)
    result = ' '.join(args)
    await channel.send(result.capitalize())


@bot.command()
async def say(ctx, *args):
    result = ' '.join(args)
    await ctx.message.delete()
    await ctx.send(result.capitalize())


@bot.command()
async def ayuda(ctx):
    embed = discord.Embed (
        title="Panel de comandos",
        description="Es el panel de comandos de las funciones del bot Ada",
        color=discord.Color.green()
    )

    embed.add_field(name="Lista de comandos", value="`!ayuda` - Abre el panel de ayuda\n`!say [mensaje]` - Hace que el bot escriba algo\n`!roles` - Te muestra tus roles\n`!avatar [mencion]` - Muestra tu avatar o el del miembro que menciones\n`!nivel` - Te muestra tu nivel y experiencia", inline=False)
    


    await ctx.reply(embed=embed)


@bot.command()
async def roles(ctx):
    embed = discord.Embed(
        title="Tus roles:",
        color=discord.Color.green()
    )

    for rol in ctx.author.roles:
        embed.add_field(name=f"- {rol.name}", value="", inline=False)

    
    await ctx.reply(embed=embed)


@bot.command()
async def avatar(ctx, *, member: str = None):
    try:
        if member is None:
            member_obj = ctx.author
        else:
            member_obj = await commands.MemberConverter().convert(ctx, member)
        
        
        avatar_url=member_obj.avatar.url

        embed = discord.Embed(
            title=f"Avatar de {member_obj.display_name}",
            color=discord.Color.green()
        )

        embed.set_image(url=avatar_url)

        
        await ctx.reply(embed=embed)

    except commands.MemberNotFound:

        
        await ctx.reply("No encontre ese miembro en el servidor")



@bot.event
async def on_ready():
    print(f'Se ha conectado con exito {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "hola ada" in message.content.lower():
        await message.channel.send(f"Hola <@{message.author.id}>, usa **$ayuda** para ver que puedo hacer")
    elif "como estas ada" in message.content.lower():
        await message.channel.send(f"Estoy bien <@{message.author.id}>, usa **$ayuda** para ver que puedo hacer")

    user_id = str(message.author.id)
    if user_id not in levels:
        levels[user_id] = {"exp": 0, "level": 1}
    levels[user_id]["exp"] += 10
    current_exp = levels[user_id]["exp"]
    current_level = levels[user_id]["level"]
    exp_need = current_level * 100
    if current_exp >= exp_need:
        levels[user_id]["level"] += 1
        levels[user_id]["exp"] = current_exp - exp_need
        new_level = levels[user_id]["level"]
        async def addRol(levelNeed, rol_name):
            if new_level == levelNeed:
                role_name = rol_name
                guild = message.guild
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await message.author.add_roles(role)
                    await message.channel.send(f"Se le asigno el rol **{role.name}** a {message.author.display_name} por llegar al nivel {levelNeed}")
                else:
                    await message.channel.send(f"El rol {role_name} no existe")
        await addRol(2, "Bronce")
        await addRol(4, "Plata")
        await addRol(6, "Oro")
        await addRol(8, "Diamante")
        embed = discord.Embed(
            title=f"¡Has subido de nivel!",
            description=f"Has subido al nivel {levels[user_id]['level']}",
            color=discord.Color.magenta()
        )
        await message.channel.send(message.author.mention, embed=embed)
    guardar()
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1506534239506792470)

    embed = discord.Embed(
        title="Bienvenid@ a El mejor server de discord 🥳",
        description=f"{member.mention}, espero que te la pases bien en la comunidad, echate un vistazo al canal de #verficacion, no olvides pasarte por el canal de #normas.",
        color=discord.Color.green(),
    )
    avatar_url = member.avatar.url if member.avatar else member.default_avatar
    embed.set_thumbnail(url=avatar_url)

    if channel:
        await channel.send(embed=embed)

@bot.command()
async def nivel(ctx, member: discord.member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)
    if user_id in levels:
        exp = levels[user_id]["exp"]
        level = levels[user_id]["level"]

        embed = discord.Embed(
            title="Datos",
            color=discord.Color.magenta()

            
        )

        embed.add_field(name="Nivel:", value=f"{level}", inline=False)
        embed.add_field(name="Expereiencia:", value=f"{exp}", inline=False)

        await ctx.reply(embed=embed)
    else:
        await ctx.reply("No tienes experiencia registrada")

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1506534784242024518)

    embed = discord.Embed(
        title=f"{member.display_name} se ha ido 😔",
        description=f"Ha abandonado la comunidad o ha sido expulsado, nunca te olvidaremos",
        color=discord.Color.green(),
    )
    avatar_url = member.avatar.url if member.avatar else member.default_avatar
    embed.set_thumbnail(url=avatar_url)

    if channel:
        await channel.send(embed=embed)

@bot.command()
async def ada(ctx, *, message):
    response = cliente_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role":"system",
                    "content":"Eres Ada, una asistente amigable y divertida que siempre busca la manera de ayudar en lo que te pidan"
                    },
                {
                    "role":"user",
                    "content": message
                    }
                ]

            )
    await ctx.reply(response.choices[0].message.content)


bot.run(os.getenv("BOT_TOKEN"))
