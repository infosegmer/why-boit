import discord
from discord.ext import commands
 
import sqlite3
from config import settings
from Cybernator import Paginator as pag
from discord.utils import get 
import requests
from bs4 import BeautifulSoup



import os
import sys
import connect 
import voice 
import youtube_dl
import random
import time

from discord import Spotify
client = commands.Bot(command_prefix = settings['PREFIX'])
client.remove_command('help')

 
connection = sqlite3.connect('server.db')
cursor = connection.cursor()
 
 
@client.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        lvl INT,
        server_id INT
    )""")
 
    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
    )""")
 
    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {guild.id})")
            else:
                pass
 
    connection.commit()
    print('Бот вошел в сеть')
    print('Создатель: М0ксек#1719')
    print('Создан: 03.06.20')
    print('Префикс: >')

    await client.change_presence(activity=discord.Streaming(name="+help", url="https://www.twitch.tv/d"))
 
@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {member.guild.id})")
        connection.commit()
    else:
        pass

@client.event
async def on_member_update(before, after):
    if before.nick != after.nick:#проверка на смену ника
        channel = client.get_channel(738348483014033459)#ид канала куда будет отправляться сообщение
        emb = discord.Embed(title = '', description = f'**Пользователь {before.mention} сменил ник.**', color = 0x36393f)
        emb.add_field(name = '**Старый ник**', value = f'{before.nick}') 
        emb.add_field(name = '**Новый ник**', value = f'{after.nick}') 
        emb.set_footer(text = 'why:christmas_tree:? ')

        await channel.send(embed = emb)

@client.command()
@commands.has_permissions( administrator = True )
async def clear(ctx, amount=None):
    await ctx.channel.purge(limit=int(amount))
    await ctx.send(embed = discord.Embed(
        title = '**Сообщения успешно удалены**', color = 0x36393f)

    )

@client.command()
async def help(ctx):
    await ctx.send(embed = discord.Embed(
        title = '**Что-бы посмотреть команды бота нажми на этот текст**', color = 0x36393f,
        url = f'https://www.codexbot.tk/'
        ))

@client.command()
async def me(ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    roles = [role for role in member.roles]

    embed = discord.Embed(colour = 0x36393f, timestamp = ctx.message.created_at )

    embed.set_author(name = f"Информация пользователя - {member}" )
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(text = f"Запросил: {ctx.author.name}", icon_url = ctx.author.avatar_url )

    embed.add_field(name = "ID", value = member.id )
    embed.add_field(name = "Name", value = member.display_name )

    embed.add_field(name = "Зарегистрирован: ", value = member.created_at.strftime("%a, %#d, %B, %Y, %I:%M %p") )
    embed.add_field(name = "Вошел на сервер:", value = member.joined_at.strftime("%a, %#d, %B, %Y, %I:%M %p") )

    embed.add_field(name = f"Роли({len(roles)})", value = "".join(role.mention for role in roles) )
    embed.add_field(name = "Высшая роль:", value = member.top_role.mention )

    embed.set_image(url = f'https://cdn.discordapp.com/attachments/660185603270377473/719578342852132904/Hogwarts_Rainbow.gif')

    await ctx.send( embed = embed )

@client.command()
async def avatar(ctx, member: discord.Member = None):

    member = ctx.author if not member else member
    roles = [role for role in member.roles]

    embed = discord.Embed(colour = 0x36393f, timestamp = ctx.message.created_at )

    embed.set_author(name = f"Аватар пользователя - {member.display_name}" )
 

    embed.set_image(url = member.avatar_url)


    await ctx.send( embed = embed )



@client.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.message.add_reaction('✅')

@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.message.add_reaction('✅') 

startTime = time.time()

@client.command()
async def uptime(ctx):
    timeUp = time.time() - startTime
    hoursUp = round(timeUp) // 3600
    timeUp %= 3600
    minutesUp = round(timeUp) // 60
    timeUp = round(timeUp % 60)
    msg = "Бот запустился: **{0}** час. **{1}** мин. **{2}** сек. назад".format(hoursUp, minutesUp, timeUp)
    await ctx.send(f"{msg}")

@client.command(aliases = ['balance', 'cash'])
async def __balance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            description = f"""Баланс пользователя **{ctx.author}** составляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :christmas_tree: **"""
        ))
        
    else:
        await ctx.send(embed = discord.Embed(
            description = f"""Баланс пользователя **{member}** составляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} :christmas_tree: **"""
        ))  

@client.command(aliases = ['award'])
async def __award(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому желаете выдать определенную сумму")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, укажите сумму, которую желаете начислить на счет пользователя")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :christmas_tree: ")
        else:
            cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')

@client.command(aliases = ['take'])
async def __take(ctx, member: discord.Member = None, amount = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, у которого желаете отнять сумму денег")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, укажите сумму, которую желаете отнять у счета пользователя")
        elif amount == 'all':
            cursor.execute("UPDATE users SET cash = {} WHERE id = {}".format(0, member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')
        elif int(amount) < 1:
            await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :christmas_tree: ")
        else:
            cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')

@client.command(aliases = ['add-shop'])
async def __add_shop(ctx, role: discord.Role = None, cost: int = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль, которую вы желаете внести в магазин")
    else:
        if cost is None:
            await ctx.send(f"**{ctx.author}**, укажите стоимость для даннойй роли")
        elif cost < 0:
            await ctx.send(f"**{ctx.author}**, стоимость роли не может быть такой маленькой")
        else:
            cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
            connection.commit()
 
            await ctx.message.add_reaction('✅')

@client.command(aliases = ['remove-shop'])
async def __remove_shop(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль, которую вы желаете удалить из магазина")
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()
 
        await ctx.message.add_reaction('✅')


@client.command(aliases = ['shop'])
async def __shop(ctx):
    embed = discord.Embed(title = 'Магазин ролей')
 
    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Стоимость **{row[1]} :christmas_tree:**",
                value = f"Вы приобрете роль {ctx.guild.get_role(row[0]).mention}",
                inline = False
            )
        else:
            pass
 
    await ctx.send(embed = embed)

@client.command(aliases = ['buy', 'buy-role'])
async def __buy(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль, которую вы желаете приобрести")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**, у вас уже имеется данная роль")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author}**, у вас недостаточно :christmas_tree: для покупки данной роли")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')

@client.command(aliases = ['rep', '+rep'])
async def __rep(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите участника сервера")
    else:
        if member.id == ctx.author.id:
            await ctx.send(f"**{ctx.author}**, вы не можете указать смого себя")
        else:
            cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(1, member.id))
            connection.commit()
 
            await ctx.message.add_reaction('✅')

@client.command(aliases = ['leaderboard', 'lb'])
async def __leaderboard(ctx):
    embed = discord.Embed(title = 'Топ 10 сервера')
    counter = 0
 
    for row in cursor.execute("SELECT name, cash FROM users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        embed.add_field(
            name = f'# {counter} | `{row[0]}`',
            value = f'Баланс: {row[1]}',
            inline = False
        )
 
    await ctx.send(embed = embed)

@client.command()
async def saper(ctx):
    embed = discord.Embed(description = '''
                     Держи :smile:
||0️⃣||||0️⃣||||0️⃣||||1️⃣||||1️⃣||||2️⃣||||1️⃣||||2️⃣||||1️⃣||||1️⃣||||
2️⃣||||2️⃣||||1️⃣||||1️⃣||||💥||||2️⃣||||💥||||3️⃣||||💥||||1️⃣||||
💥||||💥||||1️⃣||||1️⃣||||2️⃣||||3️⃣||||3️⃣||||💥||||2️⃣||||1️⃣||||
2️⃣||||2️⃣||||1️⃣||||0️⃣||||1️⃣||||💥||||2️⃣||||1️⃣||||1️⃣||||0️⃣||||
0️⃣||||0️⃣||||0️⃣||||1️⃣||||2️⃣||||2️⃣||||1️⃣||||0️⃣||||0️⃣||||0️⃣||||
1️⃣||||1️⃣||||0️⃣||||1️⃣||||💥||||1️⃣||||1️⃣||||2️⃣||||2️⃣||||1️⃣||||
💥||||1️⃣||||1️⃣||||2️⃣||||2️⃣||||1️⃣||||1️⃣||||💥||||💥||||1️⃣||||
1️⃣||||1️⃣||||1️⃣||||💥||||1️⃣||||1️⃣||||2️⃣||||3️⃣||||2️⃣||||1️⃣||||
1️⃣||||2️⃣||||2️⃣||||2️⃣||||2️⃣||||2️⃣||||💥||||1️⃣||||0️⃣||||0️⃣||||
💥||||2️⃣||||💥||||1️⃣||||1️⃣||||💥||||2️⃣||||2️⃣||||1️⃣||||1️⃣||||
1️⃣||||2️⃣||||1️⃣||||1️⃣||||1️⃣||||1️⃣||||1️⃣||||1️⃣||||💥||||1️⃣|| 
    ''', )
    await ctx.send(embed=embed)

@client.command()
async def free(ctx):
    embed = discord.Embed(description = '''
Локации хостинга

***___Odessa___ >>>
RAM- 6гб
CPU- 1
DISK- 30гб
SERVER- от 2 до 6 штук
Описание: Небольшая локация для 2-3 серверов на ней могут подвисать сервера.***

***___Kiev___ >>>
RAM- 6гб
CPU- 1
DISK- 30гб
SERVER- от 2 до 6 штук
Описание: Небольшая локация для 2-3 серверов на ней могут подвисать сервера.***
    ''', )
    await ctx.send(embed=embed)

@client.command()
async def daemon(ctx):
    embed = discord.Embed(description = '''
Статус локаций
***___Kiev:green_circle:

RAM- 1024/6196мб

CPU- 1

DISK- 30гб___***

***___Odessa:green_circle:

RAM- 0/6196мб

CPU- 1

DISK- 30гб___***
    ''', )
    await ctx.send(embed=embed)

@client.command()
async def inf(ctx):
    embed = discord.Embed(description = '''
Добро пожаловать на GXTHost!

• Вы на бесплатном хостинге GXTHost тут 100% дружелюбная администрация, тут вы можете найти себе друзей.;) 
• Я знаю вы любите дропы и их будет много если я увижу большой актив.
• В этом канале вы можете обратиться в поддержку #『🎫』ticket-support 
• У нас серверов хватит на всех.

Проверяйте : #『💻』daemon-status 
Minecraft
  - :green_circle: Spigot
  - :green_circle: Forge

Задонатив вы поможет развитию и созданию новых локаций.

Панель:
Локации: Kiev
    ''', )
    await ctx.send(embed=embed)



@client.command()
async def rules1(ctx):
    embed = discord.Embed(description = '''
[При общих правилах запрещено]:
¹.¹. Любые формы оскорблений, издевательств, расизма, дискриминации, религиозной враждебности, сексизма и т.д.
Устное предупреждение/мут до ¹⁸⁰ минут

¹.². Неадекватное поведение в любых его проявлениях.
Устное предупреждение/мут до ²⁴⁰ минут

¹.³. Деанон ⁽слив имен, фотографий, переписок и т.д.⁾ любого участника сервера без его согласия.
Бан/варн

¹.⁴. Провокация в любых проявлениях.
Устное предупреждение/мут до ⁶⁰ минут/варн

¹.⁵. Иметь "твинк" ⁽второй аккаунт⁾ для обхода наказаний и фарма серверной валюты.
Бан "твинка" и варн/бан основного аккаунта

¹.⁶. Коммерческая деятельность.
Варн/бан

¹.⁷. Реклама любых сторонних ресурсов, в том числе и в личные сообщения.
Варн/бан до ⁷ дней

¹.⁸. Использовать изображение профиля, содержащий шокирующий или сексуальный контент.
Устное предупреждение/варн

¹.⁹. Намеренное копирование профилей, никнеймов, а так же оскорбительные и провокационные никнеймы, включая названия личных комнат.
Устное предупреждение/варн

¹.¹⁰. Публикация/трансляция шокирующего и сексуального контента.
Бан/варн

¹.¹¹. Сообщения прямо или косвенно восхваляющие суицид, нанесение вреда самому себе или употребление наркотиков.
Мут до ³⁶⁰ минут/варн/Устное предупреждение

¹.¹². Препятствовать работе администрации сервера.
Устное предупреждение/мут до ¹²⁰ минут*

¹.¹³. Обман, неуважительное отношение, а также попытки дискредитации администрации сервера в любом виде.
На усмотрение администрации

¹.¹⁴. Выдавать себя за другого человека.
Бан
    ''', )
    await ctx.send(embed=embed)

@client.command()
async def raz(ctx):
    embed = discord.Embed(description = '''
Отличный хостинг, скоро откроется

GrovNodes
Гостинг для твоего сервера!
При том бесплатный!
★★★
  
〖 https://discord.gg/hAyQaD6f5y 〗
  
    ''', )
    await ctx.send(embed=embed)

    
startTime = time.time()   

@client.command()
async def rand(ctx, member: discord.Member = None):

    member = ctx.author if not member else member
    roles = [role for role in member.roles]

    embed = discord.Embed(colour = 0x36393f, timestamp = ctx.message.created_at )

    embed.set_author(name = f"🎲| Вам выпало - {random.randint(0, 100)}")

    await ctx.send( embed = embed )

@client.command()
async def spotify(ctx, member: discord.Member = None):
    member = member or ctx.author

    spot = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)

    if not spot:
        return await ctx.send(f"{member.mention}, не слушает Spotify :mute:")

    embed = discord.Embed(title = f"{member} слушает Spotify :notes:", color = spot.color)

    embed.add_field(name = "Песня", value = spot.title)
    embed.add_field(name = "Исполнитель", value = spot.artist)
    embed.add_field(name = "Альбом", value = spot.album)
    embed.add_field(name = "Пати айди", value = spot.party_id[8:])
    embed.add_field(name = "Трек айди", value = spot.track_id)
    embed.add_field(name = "Длительность аудио", value = strfdelta(spot.duration, '{hours:02}:{minutes:02}:{seconds:02}'))
    embed.set_thumbnail(url = spot.album_cover_url)

    await ctx.send(embed = embed)


@client.command()
async def kiss(ctx, member: discord.Member):
    if ctx.author.mention == member.mention:
        emb = discord.Embed(title = '', description = f'**Ты что-ли настолько одинокий что пытаешься сам себя поцеловать** {member.mention}?', color = 0x36393f)
        await ctx.send(embed = emb)

    else:
        emb = discord.Embed(title = '💋Поцелуй!💋', description = f'**Пользователь:** {ctx.author.mention}, **поцеловал** { member.mention }!💋', color = 0x36393f)
        emb.set_image(url = 'https://cdn.discordapp.com/attachments/786990676273135666/787006798787117086/anime-kiss-m.gif')
        await ctx.send( embed = emb )

@client.command()
async def hug(ctx, member: discord.Member):
    if ctx.author.mention == member.mention:
        emb = discord.Embed(title = '', description = f'**Ты настолько одинок что пытаешься сам себя обнять** {member.mention}?', color = 0x36393f)
        await ctx.send(embed = emb)

    else:
        emb = discord.Embed(title = '**Объятия!**', description = f'**Пользователь:** {ctx.author.mention}, **обнял:** {member.mention}!', color = 0x36393f)
        emb.set_image(url = 'https://cdn.discordapp.com/attachments/786990676273135666/787006801525735454/anime-hug.gif')
        await ctx.send(embed = emb)


@client.command()
async def pasta(ctx, member: discord.Member):
    if ctx.author.mention == member.mention:
        emb = discord.Embed(title = '', description = f'**Ты настолько голоден** {member.mention}?', color = 0x36393f)
        await ctx.send(embed = emb) 

    else:
        emb = discord.Embed(title = '**Лопша**', description = f'**Пользователь:** {ctx.author.mention}, **предложил поесть лопши:** {member.mention}!', color = 0x36393f)
        emb.set_image(url = 'https://cdn.discordapp.com/attachments/705530601314320414/731821014912335928/image_860106151332073779703.gif')
        await ctx.send(embed = emb)

@client.command()
async def sex(ctx, member: discord.Member):
    if ctx.author.mention == member.mention:
        emb = discord.Embed(title = '', description = f'**Ты реально хочешь сам с собой** {member.mention}?', color = 0x36393f)
        await ctx.send(embed = emb) 

    else:
        emb = discord.Embed(title = '**Cекс**', description = f'**Пользователь:** {ctx.author.mention}, **предложил заняться сексом:** {member.mention}!', color = 0x36393f)
        emb.set_image(url = 'https://cdn.discordapp.com/attachments/786990676273135666/787006802625167380/vgif-ru-17461.gif')
        await ctx.send(embed = emb)

@client.command()
async def cry(ctx, member: discord.Member):
    if ctx.author.mention == member.mention:
        emb = discord.Embed(title = '', description = f'**Мне тебя жалко** {member.mention}', color = 0x36393f)
        await ctx.send(embed = emb) 

    else:
        emb = discord.Embed(title = '**Слезы**', description = f'**Пользователь:** {ctx.author.mention}, **заплакал из-за:** {member.mention}!', color = 0x36393f)
        emb.set_image(url = 'https://cdn.discordapp.com/attachments/786990676273135666/787006803182485524/6VHR.gif')
        await ctx.send(embed = emb)

@client.command()
async def suicide(ctx, member: discord.Member):
    if ctx.author.mention == member.mention:
        emb = discord.Embed(title = '', description = f'**Тебе реально скучно жить** {member.mention}?', color = 0x36393f)
        await ctx.send(embed = emb) 

    else:
        emb = discord.Embed(title = '**Суицыд**', description = f'**Пользователь:** {ctx.author.mention}, **самоубился из-за:** {member.mention}!', color = 0x36393f)
        emb.set_image(url = 'https://cdn.discordapp.com/attachments/786990676273135666/787006805791604756/646a25027d8a083042fccc14fb14121acd65de7c_hq.gif')
        await ctx.send(embed = emb)   

client.run(settings['TOKEN'])