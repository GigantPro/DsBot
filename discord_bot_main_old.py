import time
from threading import Thread
import discord
from discord import guild
from datetime import date, datetime
from discord.ext import commands
from discord.utils import get
from config import settings
import json
import youtube_dl
import string
import os, sqlite3
from datetime import datetime
from asyncio import sleep

from database import json_write, json_read_login, json_read_pass, create, set_bad_word, json_read, del_bad_word, json_read_passport, json_write_passport
#from check import check_for_bot_admin



set_check = True

default_welcome_message_private = 'Hello!) I am a friendly server bot) To explore my capabilities, enter the command "``{prefix}help``" )'
ctx_default_welcome_message_server  = '{member}, hey bro!) Check your private messages)))'


bot = commands.Bot(command_prefix = settings['prefix'], intents=discord.Intents.all()) # Так как мы указали префикс в settings, обращаемся к словарю с ключом prefix.

def update_time():
    global time_now
    while True:
        time_now = datetime.now()
        time.sleep(1) 

def check_for_bot_admin(message=None, member=None):
    if message:
        if get(message.author.roles, name=settings['admin_bot_role']):
            return True
        else:
            return False
    if member:
        if get(member.roles, name=settings['admin_bot_role']):
            return True
        else:
            return False
    

def give_max_counter_warns(message: discord.message = None, member: discord.member = None):
    try:
        guild_id = None
        guild_name = None
        try:
            guild_id = message.guild.id
            guild_name = message.guild.name
        except:
            guild_id = member.guild.id
            guild_name = member.guild.name
        answer = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (int(guild_id),)).fetchone()
        if answer != None:
            return int(answer[2])
        else:
            default_welcome_message_private = 'Hello!) I am a friendly server bot) To explore my capabilities, enter the command `{settings["prefix"]}help` )'
            base.execute('INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?)', (int(guild_id), str(guild_name), 5, int(message.channel.id), default_welcome_message_private, default_welcome_message_private))
            base.commit()
            return 5
    except:
        print('ERROR WITH GIVE COUNTER WARNS WELCOME')
        return None


@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def hello(ctx): # Создаём функцию и передаём аргумент ctx.
    """Welcome you)))"""
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.

    await ctx.send(f'Hello, {author.mention}!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.

#@bot.command()
#async def help(ctx): # Создаём функцию и передаём аргумент ctx.
#    """Will display a list of available commands"""
#    await ctx.send(f'**Command list:**\nBot prefix **?**\n**help** - displays this message with\n**hello** - greeting)))\n**repeat** and **say** - the bot will repeat the text you wrote after the command\n**friend** - will send a fan gif\n**fire** - will output:fire:\n**password** - will give you a password if you are in base)))\n**add** - add your username and password to the base')

@bot.command()
async def repeat(ctx, *, arg):
    """Will repeat what you write next"""
    await ctx.send(arg)
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'repeat', admin_level, 'Ok', arg))
    base.commit()

@bot.command()
async def tell(ctx, *, arg):
    """Will repeat what you write next"""
    await ctx.send(arg)
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'tell', admin_level, 'Ok', arg))
    base.commit()

@bot.command()
async def write(ctx, member: discord.Member, *, message):
    """Will write your message on behalf of the bot to the user)))! Write @User a message"""
    author = ctx.message.author
    #if check_for_bot_admin(author) == True:
    try:
        await member.send(message)
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'write', admin_level, 'Ok', 'Send to: ' + member.display_name))
        base.commit()
    except: # this will error if the user has blocked the bot or has server dms disabled
        await ctx.send(f"Sadly (((This user has forbidden to send him messages (((")
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'write', admin_level, 'Ok', 'Can`t send to: ' + member.display_name))
        base.commit()
    else:
        await ctx.send(f"It was possible to send a message to {member}!")

    #else:
        #await ctx.send(f'{author.mention}, you do not have sufficient rights for this operation ...')


#@bot.command()
async def спам(ctx, member: discord.Member, summ, *, message):
    """Заспамит пользователя"""
    flag = False
    if summ < 0:
        summ = -summ
    author = ctx.message.author
    if check_for_bot_admin(member) == True:
        for i in range(int(summ)):
            try:
                await member.send(message)
            except: # this will error if the user has blocked the bot or has server dms disabled
                await ctx.send(f"Печально((( Этот пользователь запретил отсылать ему сообщения(((")
                break
            else:
                if flag == False:
                    await ctx.send(f"Получилось отправить сообщение {member} !")
                    flag = True               
    else:
        await ctx.send(f'{author.mention}, у вас недостаточно прав для этой операции...')  
        
@bot.command(aliases=["rule34"])   #aliases=["rule34"]
async def friend(ctx):
    """Just a fun GIF"""
    embed = discord.Embed(
        title="Say friend and the doors will open",
        color=discord.Colour.blue()
        )
    embed.set_image(url="https://cdn.discordapp.com/attachments/867495470989443137/878686286368636978/XAbh.gif")
    await ctx.send(embed=embed)
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'friend', admin_level, 'Ok', None))
    base.commit()
    
@bot.command()
async def fire(ctx):
    """Will just send :fire:"""
    await ctx.send(f":fire:")
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'fire', admin_level, 'Ok', None))
    base.commit()

async def print_for_user(member: discord.Member, message):
    try:
        await member.send(message)
    except: # this will error if the user has blocked the bot or has server dms disabled
        return False
    else:
        return True

@bot.command()
async def add(ctx, login, *, passwd):
    """With this command you can add your username and password to the database"""
    dis = ctx.message.author
    json_write(str(dis), login, passwd)
    await ctx.send(f"Your password with login is completely safe))))\nOnly **YOU** will be able to find it out (unless it's a server ...)))) \nBut if you change your name, you will have to enter it again ...")
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'add', admin_level, 'Ok', None))
    base.commit()
#@bot.command()
async def админпанель(ctx):
    author = ctx.message.author
    if check_for_bot_admin(author) == True:
        await ctx.send(f"**Админ - панель**\n1. Тест")
        msg = ctx.message.id
        for emoji in ['⬅', '☑', '➡']:
           await ctx.message.add_reaction(emoji)
    else:
        await ctx.send(f'{author.mention}, у вас недостаточно прав для этой операции...')

#@bot.command()
async def exit(ctx):
    await ctx.bot.voice_clients[0].disconnect()

#@bot.command()
async def yt(ctx, arg):
    await ctx.send(search_youtube(arg))

#@bot.command()
async def music(ctx, *,args):
    global vc

    if "youtu.be" in args or "youtube.com" in args:
        try:
            voice_channel = ctx.message.author.voice.channel
            vc = voice_channel.connect()
        except:
            print('Уже подключен или не удалось подключиться')

        if vc.is_playing():
            await ctx.send(f'{ctx.message.author.mention}, музыка уже проигрывается.')

        else:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(arg, download=False)
            URL = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source = URL, **FFMPEG_OPTIONS))
            while vc.is_playing():
                await sleep(1)
                if not vc.is_paused():
                    await vc.disconnect()
        
    else:
        args = search_youtube(args)
        try:
            print('1')
            voice_channel = ctx.message.author.voice.channel
            print(voice_channel)
            vc = await voice_channel.connect()
            print(vc)
        except:
            print('Уже подключен или не удалось подключиться')

        if vc.is_playing():
            await ctx.send(f'{ctx.message.author.mention}, музыка уже проигрывается.')

        else:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(args, download=False)

            URL = info['formats'][0]['url']

            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source = URL, **FFMPEG_OPTIONS))
                
        while vc.is_playing():
            await sleep(1)
            if not vc.is_paused():
                await vc.disconnect()
        print('step 3')
    


#@bot.event
async def on_raw_reaction_add(payload):
    try:
        if (payload.message_id == msg) and (payload.user_id != bot.user.id):
            channel = bot.get_channel(payload.channel_id)
    except:
        print(end='')      

@bot.command()
async def passwd(ctx):
    """With this command you can see your username and password"""
    global msg
    await ctx.send('Send here?')
    msg = ctx.message.id
    for emoji in ['☑', '🚫']:
       await ctx.message.add_reaction(emoji)
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'passwd', admin_level, 'Ok', None))
    base.commit()

@bot.event
async def on_raw_reaction_add(payload):
    try:
        if (payload.message_id == msg) and (payload.user_id != bot.user.id):
            channel = bot.get_channel(payload.channel_id)
            #await channel.send(f'Получена реакция: {payload.emoji}')
            create()
            if f'{str(payload.emoji)}' == '☑':
        
                await channel.send(f'Well, as you know ... If this is a server chat, then blame yourself ....')
                user = payload.member
                answer_login = json_read_login(str(user))
                if answer_login == False:
                    await channel.send(f"Sorry, but you are not in my database... \nYou can enter yourself by writing the command **add** \nExample: ?Add [Your login] [Your password] \nDon't worry, no one will do it for you)))")
                else:
                    answer_pass = json_read_pass(str(user))
                    await channel.send(f'Here is your username and password))) Use \nLogin:' + str(answer_login) + '\nPassword: ' + str(answer_pass))  
                    if temp_boll == False:
                        print('ERROR не удалось отправить в личку логин и пароль')
                        
        else:    
            await channel.send("That's right!) There is nothing for others to do for you dz))) \nCheck a personal)))")
            user = payload.member
            answer_login = json_read_login(str(user))
            if answer_login == False:
                temp_boll = await print_for_user(user, "Sorry, but you are in my database ntu ... \ nYou can enter yourself by writing the command ** add ** \ nExample:! Add [Your login] [Your password] \ nDon't worry, no one will do it for you))")
                if temp_boll == False:
                    print('ERROR не удалось отправить в личку про отсутствие в базе')
                #await bot.send_message(user, f'Извини, но тебя в моей базе нту...\nТы можешь себя вписать написа команду **добавить** \nПример: !добавить [Твой логин] [Твой пароль]\nНе переживайте, за тебя никто дз не выполнит))😉)')                     
            else:
                answer_pass = json_read_pass(str(user))
                temp_bool = await user.send(f'Вот твои логин и пароль))) Пользуйся 😉\nЛогин: ' + str(answer_login) + '\nПароль: ' + str(aswer_pass))  
                if temp_boll == False:
                    print('ERROR не удалось отправить в личку логин и пароль')
    except:
        print(end='')
    

#def search_youtube(title):

        # options = {
        #     'format': 'bestaudio/best',
        #     'default_search': 'auto',
        #     'noplaylist': True,
        #     "cookiefile": "/Discord BOT/cookies.txt"
        # }

        # with youtube_dl.YoutubeDL(options) as ydl:
        #     r = ydl.extract_info(title, download=False)

        # videocode = r['entries'][0]['id']

        # return "https://www.youtube.com/watch?v={}".format(videocode)

#@bot.command()
async def войс(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect() #  Use the channel instance you put into a variable

#

@bot.command()
async def setbad(ctx, *, arg):
        '''Set bad word into the black list'''
    #if check_for_bot_admin(ctx) == True:
        await ctx.message.delete()
        try:
            base.execute('INSERT INTO bads VALUES(?, ?)', (str(arg), 0))
            base.commit()
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setbad: ' + arg, admin_level, 'Ok', None))
            base.commit()
        except:
            await ctx.send("This word is already in the database.")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setbad: ' + arg, admin_level, 'Ok', 'Was in base'))
            base.commit()
        else:
            await ctx.send("Bad word set to data base)))")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setbad: ' + arg, admin_level, 'Ok', None))
            base.commit()
        
    #else:
     #   await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
     #   await ctx.message.delete()  

@bot.command()
async def delbad(ctx, *, arg):
    '''Del from base bad word'''
    await ctx.message.delete()
    if check_for_bot_admin(ctx) == True: 
        try:
            cur.execute('DELETE FROM bads WHERE Word == ?', (str(arg),))
            base.commit()
        except:
            await ctx.send('Bad word wasn`t in base.')
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'delbad: ' + arg, admin_level, 'Ok', 'Hasn`t word in base'))
            base.commit()
        else:
            await ctx.send("Bad word delete from data base.")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'delbad: ' + arg, admin_level, 'Ok', None))
            base.commit()
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        await ctx.message.delete()
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'delbad: ' + arg, admin_level, 'Ok', 'Hasn`t admin Status'))
        base.commit()
    
@bot.command()
async def setwelcomechannel(ctx, channel: discord.TextChannel):
    '''Set welcome channel'''
    if check_for_bot_admin(ctx) == True:
        try:
            cur.execute('UPDATE servers SET WelcomeChat == ? WHERE ServerID == ?', (channel.id, ctx.guild.id))
            base.commit()
            await ctx.send("Welcome chat was update)))")
        except:
            cur.execute('INSERT INTO servers VALUES(?, ? , ?, ?, ?, ?)', (int(ctx.guild.id), str(ctx.guild.name), 5, int(channel.id), ctx_default_welcome_message_server, default_welcome_message_private))
            base.commit()
            await ctx.send("Welcome chat was update)))")
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomechannel: ' + channel.name + ' ' + channel.id, admin_level, 'Ok', None))
        base.commit()
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        await ctx.message.delete()
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomechannel: ' + channel.name + ' ' + channel.id, admin_level, 'Ok', 'Hasn`t admin Status'))
        base.commit()

@bot.command()
async def setwelcomemessageserver(ctx, *, arg):
    '''Set welcome message'''
    if check_for_bot_admin(ctx) == True:
        try:
            idserv = ctx.guild.id
            answer = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (int(idserv),)).fetchone()
            if answer != None:
                cur.execute('UPDATE servers SET WelcomeServerMessage == ? WHERE ServerID == ?', (str(arg), int(idserv)))
                base.commit()
            else:
                idserv = ctx.guild.id
                base.execute('INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?)', (int(idserv), str(ctx.guild.name), 5, int(ctx.channel.id), str(arg), default_welcome_message_private))
                base.commit()
            await ctx.send("Welcome message was update)))")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomemessageserver: ' + arg, admin_level, 'Ok', None))
            base.commit()
        except:
            print('ERROR WITH UPDATE SERVER WELCOME')
            await ctx.send("ERROR")                                         #ErrorLog 1
            admin_level = check_for_bot_admin(member=ctx.author)    
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomemessageserver: ' + arg, admin_level, 'ERROR', 'ErrorLog: 1'))
            base.commit()
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        await ctx.message.delete()
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomemessageserver: ' + arg, admin_level, 'Ok', 'Hasn`t admin Status'))
        base.commit()

@bot.command()
async def setwelcomemessageprivate(ctx, *, arg):
    '''Set welcome message'''
    if check_for_bot_admin(ctx) == True:
        
        try:
            idserv = ctx.guild.id
            answer = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (int(idserv),)).fetchone()
            if answer != None:
                cur.execute('UPDATE servers SET WelcomePrivateMessage == ? WHERE ServerID == ?', (str(arg), int(idserv)))
                base.commit()
            else:
                idserv = ctx.guild.id
                base.execute('INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?)', (int(idserv), str(ctx.guild.name), 5, int(ctx.channel.id), default_welcome_message_private, str(arg)))
                base.commit()
            await ctx.send("Welcome message was update)))")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomemessageprivate: ' + arg, admin_level, 'Ok', None))
            base.commit()
            
        except:                                             #ErrorLog: 2
            print('ERROR WITH UPDATE PRIVATE WELCOME')
            await ctx.send("ERROR")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomemessageprivate: ' + arg, admin_level, 'ERROR', 'ErrorLog: 2'))
            base.commit()
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        await ctx.message.delete()
        admin_level = check_for_bot_admin(member=ctx.author)
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setwelcomemessageprivate: ' + arg, admin_level, 'Ok', 'Hasn`t admin Status'))
        base.commit()

@bot.command()
async def setmaxwarnslimit(ctx, arg):
    '''Set max warns limit'''

    await ctx.message.delete()
    try:
        if int(arg) <= 0:
            await ctx.send('**The number of warnings cannot be <= 0 !!!**')
            return
    except:
        await ctx.send('**The argument must be an integer !!!**')
        return
    if check_for_bot_admin(ctx) == True: 
        try:
            try:
                cur.execute('UPDATE servers SET CounterMaxWARNS == ? WHERE ServerID == ?', (int(arg), ctx.guild.id))
                base.commit()
            except:
                cur.execute('INSERT INTO servers VALUES(?, ? , ?, ?, ?, ?)', (int(ctx.guild.id), str(ctx.guild.name), int(arg), int(ctx.channel.id), ctx_default_welcome_message_server, default_welcome_message_private))
                base.commit()
        except:                         #ErrorLog: 1
            await ctx.send('ERROR')
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setmaxwarnslimit: ' + arg, admin_level, 'ERROR', 'ErrorLog: 1'))
            base.commit()
        else:
            await ctx.send("Max counter warns was update.")
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        await ctx.message.delete()
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setmaxwarnslimit: ' + arg, admin_level, 'Ok', None))
    base.commit()

@bot.event
async def on_message(message: discord.Message):
    if message.content[1:7] != 'setbad' and message.content[1:7] != 'delbad':
        bads = cur.execute('SELECT * FROM bads')
        base_bads = []
        for i in bads:
            base_bads.append(str(i[0]))
        if {i.lower().translate(str.maketrans('','', string.punctuation)) for i in message.content.split(' ')}.intersection(base_bads) != set():
            await message.channel.send(f'{message.author.mention}, uuuuu... Who should be spanked on the lips?')
            await message.delete()          #todo: система врнов
            warn = None
            max_counter_warns = give_max_counter_warns(message)
            try:
                idperson = message.author.id
                answer = cur.execute('SELECT * FROM warns WHERE MemberID == ?', (int(idperson),)).fetchone()
                if answer != None:
                    arg_str = cur.execute('SELECT * FROM warns WHERE MemberID == ?', (int(idperson),)).fetchone()
                    arg = int(arg_str[2])
                    warn = arg + 1
                    arg += 1
                    cur.execute('UPDATE warns SET CounterWARNS == ? WHERE MemberID == ?', (int(arg), int(idperson)))
                    base.commit()
                    if arg >= max_counter_warns:
                        #await message.author.ban(reason= "{}: {}".format(message.author, "Warning limit reached"))
                        await message.author.kick(reason= "{}: {}".format(message.author, "Warning limit reached"))
                        await message.channel.send("Warning limit reached... Member was banned...")
                        return
                else:
                    base.execute('INSERT INTO warns VALUES(?, ?, ?)', (int(message.author.id), str(message.author.name), 1))
                    base.commit()
                    warn = 1
                await message.channel.send(f"You have already had **{warn}** warns!!!\nIf you have **{max_counter_warns}** warns, you will be banned!!!")
            except:
                await message.channel.send("**The role of the author is higher than the role of the bot!**")
    await bot.process_commands(message)
    admin_level = check_for_bot_admin(member=message.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, message.author.name, int(message.author.id), message.author.guild.name, message.author.guild.id, 'Write', message.content, admin_level, 'Ok', None))
    base.commit()

@bot.event
async def on_member_join(member):
    print(f'{member.name} was join to {member.guild.name}')
    this_guild = bot.get_guild(member.guild.id)
    guild_id = this_guild.id
    guild_name = this_guild.name
    channel_hello = bot.get_guild(member.guild.id).channels[0]
    server_base = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (int(guild_id),)).fetchone()
    if server_base == None:
        base.execute('INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?)', (int(guild_id), str(guild_name), 5, int(channel_hello.id), default_welcome_message_private, default_welcome_message_private))
        base.commit()
    await member.send(server_base[5].format(member=member.mention, prefix=settings["prefix"]))
    #await channel.send(server_base[4].format(member=member.mention, prefix=settings["prefix"]))
    # await bot.get_channel(ch.id).send(f'{member.mention}, hey bro!) Check your private messages)))')
    #await bot.get_channel(ch.id).send(hello_text[4].format(member=member.mention, prefix=settings["prefix"]))
    idperson = member.id
    answer = cur.execute('SELECT * FROM warns WHERE MemberID == ?', (int(idperson),)).fetchone()
    if answer != None:
        arg = int(answer[2])
        max_counter_warns = give_max_counter_warns(None, member)
        if arg >= max_counter_warns:
            #await message.author.ban(reason= "{}: {}".format(message.author, "Warning limit reached"))
            await member.kick(reason= "{}: {}".format(member, "Warning limit reached"))
            await member.author.send(f'You were kicked from the server because you have too many warnings. This server has a maximum of ``{max_counter_warns}`` warnings, well, you have ``{arg}`` of them.')
            for ch in bot.get_guild(member.guild.id).channels:
                if ch.id == server_base[3]:
                    await bot.get_channel(ch.id).send('Warning limit reached... He is a bag guy...')
                admin_level = check_for_bot_admin(member=member)
                cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, member.name, int(member.id), member.guild.name, member.guild.id, 'Kicked', 'too many warnings', admin_level, 'Ok', None))
                base.commit()
            return
    else:
        base.execute('INSERT INTO warns VALUES(?, ?, ?)', (int(idperson), str(member.name), 0))
        base.commit()
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.id == server_base[3]:
            await bot.get_channel(ch.id).send(server_base[4].format(member=member.mention, prefix=settings["prefix"]))
    admin_level = check_for_bot_admin(member=member)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, member.name, int(member.id), member.guild.name, member.guild.id, 'Join', 'Member was joined', admin_level, 'Ok', None))
    base.commit()


@bot.event
async def on_member_remove(member):
    print(f'{member.name} was remove')
    this_guild = bot.get_guild(member.guild.id)
    guild_id = this_guild.id
    server_base = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (int(guild_id),)).fetchone()
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.id == server_base[3]:
            await bot.get_channel(ch.id).send(f'{member.mention}, we will miss you (((((((')
    admin_level = check_for_bot_admin(member=member)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, member.name, int(member.id), member.guild.name, member.guild.id, 'Escape', 'Member was escaped.', admin_level, 'Ok', None))
    base.commit()

@bot.event
async def on_ready():
    therd = Thread(target=update_time) 
    therd.start()
    
    print('Time update')
    global base, cur
    print('DataBase connected...', end='')
    base = sqlite3.connect('baseff.bd')
    cur = base.cursor()
    if base:
        print('OK')
    base.execute('CREATE TABLE IF NOT EXISTS {}(MemberID PRIMARY KEY, MemberName, CounterWARNS)'.format('warns'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(ServerID PRIMARY KEY, ServerName, CounterMaxWARNS, WelcomeChat, WelcomeServerMessage, WelcomeMessagePivate)'.format('servers'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(Word PRIMARY KEY, CounterUse)'.format('bads'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(WhenTime, WhoName, WhoId, WhereName, WhereId, Action, Description, AdminStatus, ErrorLog, Comment)'.format('logs'))
    base.commit()
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, 'Bot', None, 'Global', None, 'Start', 'Bot started', 666, 'Ok', None))
    base.commit()
    
bot.run(settings['token']) # Обращаемся к словарю settings с ключом token, для получения токена
