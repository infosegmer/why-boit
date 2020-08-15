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
import pyowm

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

    await client.change_presence( status = discord.Status.online, activity = discord.Game('>help_music'))
 
 
@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {member.guild.id})")
        connection.commit()
    else:
        pass

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

@client.command()
async def play(ctx, url : str):
    song_there = os.path.isfile('song.mp3')

    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старый файл удален')
    except PermissionError:
        print('[log] Не удалось удалить файл')

    await ctx.send('Музыка скоро начнет свое проигрываниe')

    voice = get(client.voice_clients, guild = ctx.guild)

    ydl_opts = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192'
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[log] Загружаю музыку...')
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            print(f'[log] Переименовываю файл: {file}')
            os.rename(file, 'song.mp3')

    voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, музыка закончила свое проигрывание'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.08

    song_name = name.rsplit('-', 2)
    await ctx.send(f'Сейчас проигрывает музыка: {song_name[0]}')

startTime = time.time()

@client.command()
async def musicup(ctx):
    timeUp = time.time() - startTime
    hoursUp = round(timeUp) // 3600
    timeUp %= 3600
    minutesUp = round(timeUp) // 60
    timeUp = round(timeUp % 60)
    msg = "Бот запустился: **{0}** час. **{1}** мин. **{2}** сек. назад".format(hoursUp, minutesUp, timeUp)
    await ctx.send(f"{msg}")

client.run(settings['TOKEN'])