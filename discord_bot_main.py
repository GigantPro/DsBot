import time
from threading import Thread
import discord
from discord import guild
from datetime import date, datetime
from discord.ext import commands
from discord.utils import get
import string
import os, sqlite3
from datetime import datetime
from asyncio import sleep

from database import json_write, json_read_login, json_read_pass, create, set_bad_word, json_read, del_bad_word, json_read_passport, json_write_passport
from config import settings
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

def check_for_bot_admin(message=None, member=None, payload=None):
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
    if payload:
        if get(payload.member.roles, name=settings['admin_bot_role']):
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
async def addlogin(ctx, *, login):
    """With this command you can add your login to the database"""
    try:
        cur.execute('UPDATE passwords SET Login == ? WHERE WhoId == ?', (str(login), int(ctx.author.id)))
        base.commit()
        await ctx.send(f"Your login has been updated))))\nOnly **YOU** will be able to find it out (unless it's a server ...))))")
    except:  
        cur.execute('INSERT INTO passwords VALUES(?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), str(login), None))
        base.commit()
        await ctx.send(f"Your login has been added, but there is no password ... You can enter the '{settings['prefix']}addpass' and add it")
    admin_level = check_for_bot_admin(member=ctx.author)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'addpass', admin_level, 'Ok', None))
    base.commit()

@bot.command()
async def addpass(ctx, *, login):
    """With this command you can add your password to the database"""
    try:  
        base.execute('INSERT INTO passwords VALUES(?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), None, str(login)))
        base.commit()
        await ctx.send(f"Your password has been added, but there is no login...\nYou can enter the '{settings['prefix']}addlogin' and add it")
    except:
        base.execute('UPDATE passwords SET Password == ? WHERE WhoId == ?', (str(login), int(ctx.author.id)))
        base.commit()
        await ctx.send(f"Your password has been updated))))\nOnly **YOU** will be able to find it out (unless it's a server ...))))")
    admin_level = check_for_bot_admin(member=ctx.author)
    base.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'addpass', admin_level, 'Ok', None))
    base.commit()

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
        admin_level = check_for_bot_admin(payload=payload)
        guild_name = bot.get_guild(payload.guild_id).name
    except:
        admin_level = guild_name = 'PV'
    user: discord.member = payload.member

    try:
        pass_base = None
        channel = bot.get_channel(payload.channel_id)
        if (payload.message_id == msg) and (payload.user_id != bot.user.id):
            
            try:
                print(user.id)
                pass_base = cur.execute('SELECT * FROM passwords WHERE WhoId == ?', (int(user.id),)).fetchone()
                if not pass_base:
                    vizov_iscluchenija
            except:       
                await channel.send(f"Sorry, but you are not in my database... \nYou can enter yourself by writing the command **addlogin** and **addpass**")
                cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, user.name, user.id, guild_name, payload.guild_id, 'Event', 'on_raw_reaction_add', admin_level, 'Hasn`t in base', None))
                base.commit()
                return
            #await channel.send(f'Получена реакция: {payload.emoji}')
            if f'{str(payload.emoji)}' == '☑':        
                await channel.send(f'Well, as you know ... If this is a server chat, then blame yourself ....')
                await channel.send(f'Here is your username and password))) Use it 😉\nLogin: **{pass_base[3]}**\nPassword: **{pass_base[4]}**')       
            else:    
                await channel.send("That's right!)\nCheck a PV)))")
                user = payload.member
                temp_bool = await user.send(f'Here is your username and password))) Use it 😉\nLogin: **{pass_base[3]}**\nPassword: **{pass_base[4]}**')  
                if temp_bool == False:
                    await channel.send(f'{user.mention}, you blocked my messages((')
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, user.name, user.id, guild_name, payload.guild_id, 'Event', 'on_raw_reaction_add', admin_level, 'Ok', f'Reaction: {str(payload.emoji)}'))
            base.commit()
    except:
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, user.name, user.id, guild_name, payload.guild_id, 'Event', 'on_raw_reaction_add', admin_level, 'Error', f'Reaction: {str(payload.emoji)}'))
        base.commit()
        pass

@bot.command()
async def setbad(ctx, *, arg):
        '''Set bad word into the black list'''
    #if check_for_bot_admin(ctx) == True:
        await ctx.message.delete()
        try:
            base.execute('INSERT INTO bads VALUES(?, ?)', (str(arg).lower(), 0))
            base.commit()
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setbad: ' + arg.lower(), admin_level, 'Ok', None))
            base.commit()
        except:
            await ctx.send("This word is already in the database.")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setbad: ' + arg.lower(), admin_level, 'Ok', 'Was in base'))
            base.commit()
        else:
            await ctx.send("Bad word set to data base)))")
            admin_level = check_for_bot_admin(member=ctx.author)
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.author.guild.name, ctx.author.guild.id, 'Use', 'setbad: ' + arg.lower(), admin_level, 'Ok', None))
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
    await ctx.message.delete()
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
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), ctx.guild.name, ctx.guild.id, 'Use', 'setwelcomechannel: ' + channel.name + ' ' + channel.id, admin_level, 'Ok', None))
        base.commit()
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        
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

@bot.command()
async def setblack(ctx, *, arg):
    try:
        cur.execute('INSERT INTO blacklist VALUES(?, ?)', (str(arg), 0))
        base.commit()
        await ctx.channel.send('Set to black list.')
    except:
        await ctx.channel.send('Already in base.')

@bot.event
async def yt(ctx, url):

    author = ctx.message.author
    voice_channel = author.voice_channel
    vc = await bot.join_voice_channel(voice_channel)

    player = await vc.create_ytdl_player(url)
    player.start()

@bot.event
async def on_message(message: discord.Message):
    message_content = message.content.lower().translate(str.maketrans('','', string.punctuation + ' '))
    if message.content[1:7] != 'setbad' and message.content[1:7] != 'delbad':
        bads = cur.execute('SELECT * FROM bads').fetchall()
        base_bads = []
        for i in bads:
            base_bads.append(str(i[0]))
        flag = False
        counter_warns = 0
        for i in base_bads:
            if i in message_content:
                counter_warns += 1
                admin_level = check_for_bot_admin(member=message.author)
                cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, message.author.name, int(message.author.id), message.author.guild.name, message.author.guild.id, 'warn', message.content, admin_level, 'Ok', 'Word: ' + i))
                base.commit()
                if flag is False:
                    await message.channel.send(f'{message.author.mention}, uuuuu... Who should be spanked on the lips?')
                    await message.delete()
                    flag = True
        if flag is True:
            warn = None
            max_counter_warns = give_max_counter_warns(message)
            try:
                idperson = message.author.id
                answer = cur.execute('SELECT * FROM warns WHERE MemberID == ?', (int(idperson),)).fetchone()
                if answer != None:
                    arg_str = answer
                    arg = int(arg_str[2])
                    warn = arg + counter_warns
                    cur.execute('UPDATE warns SET CounterWARNS == ? WHERE MemberID == ?', (int(warn), int(idperson)))
                    base.commit()
                    if warn >= max_counter_warns:
                        #await message.author.ban(reason= "{}: {}".format(message.author, "Warning limit reached"))
                        await message.author.kick(reason= "{}: {}".format(message.author, "Warning limit reached"))
                        await message.channel.send("Warning limit reached... Member was kicked...")
                        admin_level = check_for_bot_admin(member=message.author)
                        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, message.author.name, int(message.author.id), message.author.guild.name, message.author.guild.id, 'kicked', message.content, admin_level, 'Ok', None))
                        base.commit()
                        return
                else:
                    base.execute('INSERT INTO warns VALUES(?, ?, ?)', (int(message.author.id), str(message.author.name), 1))
                    base.commit()
                    warn = 1
                await message.channel.send(f"You have already **{warn}** warns!!!\nIf you have **{max_counter_warns}** warns, you will be banned!!!")
            except:
                await message.channel.send("**The role of the author is higher than the role of the bot!**")
            schet = cur.execute('SELECT CounterUse FROM bads WHERE Word == ?', (str(i),)).fetchone()[0] + 1
            cur.execute('UPDATE bads SET CounterUse == ? WHERE Word == ?', (schet, i))
            base.commit()
    BlackList = cur.execute('SELECT * FROM blacklist').fetchall()
    for i in BlackList:
        if i[0] in message.content:
            try:
                await message.delete()
                pass
            except:
                pass
            try:
                for guild in bot.guilds: # Перебираем все сервера, где есть бот
                    user = bot.fetch_user(message.author.id)
                    await user.ban(reason = "Spammer whith 'Free Discord Nitro'")
                await message.channel.send('He was banned, because he is spammer!!!')
                admin_level = check_for_bot_admin(member=message.author)
                schet = cur.execute('SELECT CounterUse FROM bads WHERE Word == ?', (str(i),)).fetchone()[0] + 1
                cur.execute('UPDATE bads SET CounterUse == ? WHERE Word == ?', (schet, i))
                base.commit()
                cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, message.author.name, int(message.author.id), message.author.guild.name, message.author.guild.id, 'Banned', message.content, admin_level, 'Ok', 'Reason = Spammer'))
                base.commit()
                break
            except:
                await message.channel.send('**The role of the author is higher than the role of the bot!**')
                admin_level = check_for_bot_admin(member=message.author)
                cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, message.author.name, int(message.author.id), message.author.guild.name, message.author.guild.id, 'TryBanned', message.content, admin_level, 'Ok', 'Reason = Spammer'))
                base.commit()
                break
    await bot.process_commands(message)
    admin_level = check_for_bot_admin(message=message)
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
    welcome_message = server_base[5]
    try:
        await member.send(welcome_message.format(prefix=settings["prefix"], member=member.mention))
    except:
        try:
            await member.send(welcome_message.format(prefix=settings["prefix"]))
        except:
            try:
                await member.send(welcome_message.format(member=member.mention))
            except:
                pass


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
    welcome_message = server_base[4]
    try:
        for ch in bot.get_guild(member.guild.id).channels:
            if ch.id == server_base[3]:
                await bot.get_channel(ch.id).send(welcome_message.format(prefix=settings["prefix"], member=member.mention))
    except:
        try:
            for ch in bot.get_guild(member.guild.id).channels:
                if ch.id == server_base[3]:
                    await bot.get_channel(ch.id).send(welcome_message.format(prefix=settings["prefix"]))
        except:
            try:
                for ch in bot.get_guild(member.guild.id).channels:
                    if ch.id == server_base[3]:
                        await bot.get_channel(ch.id).send(welcome_message.format( member=member.mention))
            except:
                pass
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.id == server_base[3]:
            await bot.get_channel(ch.id).send(welcome_message)
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
    base.execute('CREATE TABLE IF NOT EXISTS {}(Word PRIMARY KEY, CounterUse)'.format('blacklist'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(Time, Who, WhoId PRIMARY KEY, Login, Password)'.format('passwords'))
    base.commit()
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, 'Bot', None, 'Global', None, 'Start', 'Bot started', 666, 'Ok', None))
    base.commit()
    await bot.change_presence(activity=discord.Game(name=".help"))
    #await bot.change_presence(activity=discord.Streaming(name="My Stream", url='test'))
bot.run(settings['token']) # Обращаемся к словарю settings с ключом token, для получения токена
