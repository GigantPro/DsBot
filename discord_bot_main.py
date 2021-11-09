import time
from threading import Thread
import discord
from discord import guild
from datetime import date, datetime
from discord.ext import commands
from discord.raw_models import RawMessageUpdateEvent
from discord.utils import get
import string
import os, sqlite3
from datetime import datetime
from asyncio import sleep
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch
import webbrowser

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'False'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


'''
НЕМНОГО О КАРТИНКАХ:
https://cdn.discordapp.com/attachments/904289207739093013/904688195873148938/hz.jpg   - хз что
https://cdn.discordapp.com/attachments/867495470989443137/878686286368636978/XAbh.gif - гифка скажи друже
'''

log_list = []

settings = {
    'token': 'ODg5MDkyNzA2OTM1MTI4MDc0.YUcOGw.IQVUrV52SsdfnT-sZxAVBxXiAEs',
    'bot': 'Crowbar Bot',
    'id': 889092706935128074,
    'prefix': 'ct!',
    'admin_bot_role': 'Bot Admin'}

set_check = True

default_welcome_message_private = 'Hello!) I am a friendly server bot) To explore my capabilities, enter the command "``{prefix}help``" )'
ctx_default_welcome_message_server  = '{member}, hey bro!) Check your private messages)))'

usercommands = f"""**{settings['prefix']}help** - this command
**{settings['prefix']}help [command]** - help with command
**{settings['prefix']}hello** - Welcome you
**{settings['prefix']}repeat** - Will repeat what you write next
**{settings['prefix']}friend** - Just a fun GIF
**{settings['prefix']}fire** - Will just send :fire:
**{settings['prefix']}addlogin** - Add your login to the database
**{settings['prefix']}addpass** - Add your password to the database
**{settings['prefix']}passwd** - See your username and password
**{settings['prefix']}admhelp** - See all admin commands"""
admincommands = f"""**{settings['prefix']}write** - Just send your message to person.
**{settings['prefix']}setbad** - set bad word to data base.
**{settings['prefix']}setwelcomemessageserver** - set welcome message on server
**{settings['prefix']}setwelcomemessageprivate** - set welcome message on PV
**{settings['prefix']}setmaxwarnslimit** - set max warns limit in server"""



bot = commands.Bot(command_prefix = settings['prefix'], intents=discord.Intents.all()) # Так как мы указали префикс в settings, обращаемся к словарю с ключом prefix.
bot.remove_command('help')
#{settings['prefix']}write - Will write your message on behalf of the bot to the user)))! {settings['prefix']}write @User [message]

def update_time():
    global time_now
    while True:
        time_now = datetime.now()
        time.sleep(1) 

def check_for_bot_admin(message=None, member=None, payload=None):
    if message:
        try:
            if message.author.guild_permissions.administrator:
                return True
        except Exception as ex:
            print(ex)
            if get(message.author.roles, name=settings['admin_bot_role']):
                return True
            else:
                return False
    if member:
        try:
            if member.guild_permissions.administrator:
                return True
        except Exception as ex:
            print(ex)
            if get(member.roles, name=settings['admin_bot_role']):
                return True
            else:
                return False
    if payload:
        try:
            if payload.member.guild_permissions.administrator:
                return True
        except Exception as ex:
            print(ex)
        if get(payload.member.roles, name=settings['admin_bot_role']):
            return True
        else:
            return False

def check_in_db_server(ctx, AdminRole=None, CounterMaxWARNS=5, WelcomeChat=None, WelcomeServerMessage=ctx_default_welcome_message_server, WelcomeMessagePivate=default_welcome_message_private):
    base_sq = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (ctx.guild.id,)).fetchone()
    if not base_sq:
        try:
            cur.execute('INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (ctx.guild.name, ctx.guild.id, AdminRole, ctx.guild.member_count, CounterMaxWARNS, WelcomeChat.name, WelcomeChat.id, WelcomeServerMessage, WelcomeMessagePivate))
            base.commit()
        except:
            cur.execute('INSERT INTO servers VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (ctx.guild.name, ctx.guild.id, AdminRole, ctx.guild.member_count, CounterMaxWARNS, WelcomeChat, WelcomeChat, WelcomeServerMessage, WelcomeMessagePivate))
            base.commit()

def update_in_db_server(ctx, AdminRole=None, CounterMaxWARNS=None, WelcomeChat=None, WelcomeServerMessage=None, WelcomeMessagePivate=None):
    check_in_db_server(ctx)
    if AdminRole:
        cur.execute('UPDATE servers SET AdminRole == ? WHERE ServerID == ?', (str(AdminRole), int(ctx.guild.id)))
        base.commit()
    if CounterMaxWARNS:
        cur.execute('UPDATE servers SET CounterMaxWARNS == ? WHERE ServerID == ?', (CounterMaxWARNS, int(ctx.guild.id)))
        base.commit()
    if WelcomeChat:
        cur.execute('UPDATE servers SET WelcomeChatName == ? WHERE ServerID == ?', (WelcomeChat.name, int(ctx.guild.id)))
        base.commit()
        cur.execute('UPDATE servers SET WelcomeChatId == ? WHERE ServerID == ?', (WelcomeChat.id, int(ctx.guild.id)))
        base.commit()
    if WelcomeServerMessage:
        cur.execute('UPDATE servers SET WelcomeServerMessage == ? WHERE ServerID == ?', (str(WelcomeServerMessage), int(ctx.guild.id)))
        base.commit()
    if WelcomeMessagePivate:
        cur.execute('UPDATE servers SET WelcomeMessagePivate == ? WHERE ServerID == ?', (str(WelcomeMessagePivate), int(ctx.guild.id)))
        base.commit()

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
            return int(answer[3])
        else:
            try:
                check_in_db_server(ctx=message)
            except:
                check_in_db_server(ctx=member)
            return 5
    except:
        print('ERROR WITH GIVE COUNTER WARNS WELCOME')
        return None

def log(ctx=None, member=None, Action='Use', Description=None, ErrorLog='Ok', Comment=None):
    admin_status = None
    try:
        admin_status = check_for_bot_admin(message=ctx)
    except:
        admin_status = check_for_bot_admin(member=member)
    try:
        cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.author.name, ctx.author.id, ctx.guild.name, ctx.guild.id, Action, Description, admin_status, ErrorLog, Comment))
        base.commit()
    except:
        try:
            cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.member.name, ctx.user_id, bot.get_guild(ctx.guild_id).name, ctx.guild_id, Action, Description, admin_status, ErrorLog, Comment))
            base.commit()
        except:
            try:
                cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, member.name, member.id, member.guild.name, member.guild.id, Action, Description, admin_status, ErrorLog, Comment))
                base.commit()
            except:
                try:
                    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, ctx.member.name, ctx.user.id, member.guild.name, member.guild.id, Action, Description, admin_status, ErrorLog, Comment))
                    base.commit()
                except Exception as ex:
                    print('Error with logs: ' + str(ex))
                    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, 'Bot', None, 'Global', None, 'ERROR', 'ERROR WITH LOGS', 666, 'ERROR', None))
                    base.commit()

def serch_youtube(arg):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(arg) 
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'False'}
    return video

async def print_for_user(member: discord.Member, message):
    try:
        await member.send(message)
    except: # this will error if the user has blocked the bot or has server dms disabled
        return False
    else:
        return True

@bot.command()
async def help(ctx, *, arg=None):
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
            title = f"Bot prefix ``{settings['prefix']}``",
            description = usercommands,
            color = discord.Colour.dark_gold())
        await ctx.send(embed=embed)
    else:
        list_commands = []
        for command in bot.commands:
            list_commands.append(command.name)
        print(list_commands)
        if not(arg in list_commands):
            embed = discord.Embed(
            title = "``I don`t know this command``",
            color = discord.Colour.dark_gold())
            embed.set_image(url='https://cdn.discordapp.com/attachments/904289207739093013/904688195873148938/hz.jpg')
            await ctx.send(embed=embed)
        else:
            if arg == 'hello':
                embed = discord.Embed(
                title = "Command ``hello``",
                color = discord.Colour.dark_gold(),
                description = 'This command will welcome you.')
                await ctx.send(embed=embed)
            if arg == 'repeat':
                embed = discord.Embed(
                title = "Command ``repeat``",
                color = discord.Colour.dark_gold(),
                description = 'Bot will repeat your text.')
                await ctx.send(embed=embed)
            if arg == 'write':
                embed = discord.Embed(
                title = "Command ``write``",
                color = discord.Colour.dark_gold(),
                description = f'Bot will send to user your text. \nBut it`s command only for admins.\nExample: {settings["prefix"]}write [WHO] [TEXT]')
                await ctx.send(embed=embed)
            if arg == 'friend':
                embed = discord.Embed(
                title = "Command ``friend``",
                color = discord.Colour.dark_gold(),
                description = 'Just a fun GIF)')
                await ctx.send(embed=embed)
            if arg == 'fire':
                embed = discord.Embed(
                title = "Command ``fire``",
                color = discord.Colour.dark_gold(),
                description = 'Will just send :fire:')
                await ctx.send(embed=embed)
            if arg == 'addlogin':
                embed = discord.Embed(
                title = "Command ``addlogin``",
                color = discord.Colour.dark_gold(),
                description = f'With this command you can add your login to the database.\nExample: {settings["prefix"]}addlogin [YOUR LOGIN]')
                await ctx.send(embed=embed)
            if arg == 'addpass':
                embed = discord.Embed(
                title = "Command ``addpass``",
                color = discord.Colour.dark_gold(),
                description = f'With this command you can add your password to the database.\nExample: {settings["prefix"]}addlogin [YOUR PASS]')
                await ctx.send(embed=embed)
            if arg == 'passwd':
                embed = discord.Embed(
                title = "Command ``passwd``",
                color = discord.Colour.dark_gold(),
                description = 'You can see your login and password.')
                await ctx.send(embed=embed)
            if arg == 'setbad':
                embed = discord.Embed(
                title = "Command ``setbad``",
                color = discord.Colour.dark_gold(),
                description = f'Set bad word into the data base\nBut it`s command only for admins.\nExample: {settings["prefix"]}setbad [BAD WORD]')
                await ctx.send(embed=embed)
            if arg == 'delbad':
                embed = discord.Embed(
                title = "Command ``delbad``",
                color = discord.Colour.dark_gold(),
                description = f'Delete bad word from the data base\nBut it`s command only for admins.\nExample: {settings["prefix"]}delbad [BAD WORD]')
                await ctx.send(embed=embed)
            if arg == 'setwelcomechannel':
                embed = discord.Embed(
                title = "Command ``setwelcomechannel``",
                color = discord.Colour.dark_gold(),
                description = f'Set welcome channel.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setwelcomechannel [#CHANNEL]')
                await ctx.send(embed=embed)
            if arg == 'setwelcomemessageserver':
                embed = discord.Embed(
                title = "Command ``setwelcomemessageserver``",
                color = discord.Colour.dark_gold(),
                description = f'Set welcome message in server.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setwelcomemessageserver [TEXT]')
                await ctx.send(embed=embed)
            if arg == 'setwelcomemessageprivate':
                embed = discord.Embed(
                title = "Command ``setwelcomemessageprivate``",
                color = discord.Colour.dark_gold(),
                description = f'Set welcome message in PV.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setwelcomemessageprivate [TEXT]')
                await ctx.send(embed=embed)
            if arg == 'setmaxwarnslimit':
                embed = discord.Embed(
                title = "Command ``setmaxwarnslimit``",
                color = discord.Colour.dark_gold(),
                description = f'Set max warns limit in server.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setmaxwarnslimit [NUM]')
                await ctx.send(embed=embed)
            if arg == 'setblack':
                embed = discord.Embed(
                title = "Command ``setblack``",
                color = discord.Colour.dark_gold(),
                description = 'This is a secret command that can only be used by the bot creator. \nThis command will add a word or more to the BLACK LIST. \nIf someone writes these words, they will immediately be banned everywhere. \nFor example, for fraudulent links such as with free nitro')
                await ctx.send(embed=embed)
            if arg == 'trusted':
                embed = discord.Embed(
                title = "Command ``trusted``",
                color = discord.Colour.dark_gold(),
                description = f'This is a secret command that can only be used by bot creator. \nThis command will add member to the TRUSTED LIST. \nThis member becomes with the rights of the bot creator.')
                await ctx.send(embed=embed)
                return
            if arg == 'admhelp':
                embed = discord.Embed(
                title = "Command ``admhelp``",
                color = discord.Colour.dark_gold(),
                description = 'This command will see all admin`s commands.')
                await ctx.send(embed=embed)    
    log(ctx=ctx, Description='help', Comment=ctx.message.content)

@bot.command()
async def admhelp(ctx):
    if check_for_bot_admin(message=ctx.message) is True:
        embed = discord.Embed(
        title = "``Commands for admin``",
        color = discord.Colour.dark_gold(),
        description = admincommands)
        await ctx.send(embed=embed)   
    else:
        await ctx.send('You arn`t an admin...') 

@bot.command()
async def play(ctx, *, arg):
    # results = YoutubeSearch('search terms', max_results=10).to_dict()
    # for v in results:
    #     print(v)
    global vc
    if 'youtube.com' in arg:
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You're not connected to any voice channel !")
        else:
            vc = get(bot.voice_clients, guild=ctx.guild)
            if vc and vc.is_connected():
                await vc.move_to(channel)
            else:
                vc = await channel.connect()
        if vc.is_playing():
            await ctx.send(f'{ctx.message.author.mention}, музыка уже проигрывается.')
        else:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(arg, download=False)
            URL = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source = URL, **FFMPEG_OPTIONS))       
            while vc.is_playing():
                await sleep(1)
            if not vc.is_paused():
                await vc.disconnect()
    else:
        result_serch = YoutubeSearch(arg, max_results=1).to_dict()
        results = f'https://www.youtube.com{result_serch[0]["url_suffix"]}'
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You're not connected to any voice channel !")
        else:
            vc = get(bot.voice_clients, guild=ctx.guild)
            if vc and vc.is_connected():
                await vc.move_to(channel)
            else:
                vc = await channel.connect()
        if vc.is_playing():
            await ctx.send(f'{ctx.message.author.mention}, music is already playing.')
        else:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(results, download=False)
            URL = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source = URL, **FFMPEG_OPTIONS))       
            while vc.is_playing():
                await sleep(1)
            if not vc.is_paused():
                await vc.disconnect()

@bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def hello(ctx): # Создаём функцию и передаём аргумент ctx.
    """Welcome you)))"""
    await ctx.message.delete()
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Hello, {author.mention}!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.
    log(ctx=ctx, Description='hello', Comment=ctx.message.content)

@bot.command()
async def repeat(ctx, *, arg=None):
    """Will repeat what you write next"""
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``repeat``",
        color = discord.Colour.dark_gold(),
        description = f'**This command will repeat your text.\nExample: {settings["prefix"]}repeat [TEXT]**')
        await ctx.send(embed=embed)
        return
    await ctx.send(arg)
    log(ctx=ctx, Description='repeat', Comment=ctx.message.content)

@bot.command()
async def write(ctx, member: discord.Member=None, *, message=None):
    """Will write your message on behalf of the bot to the user)))! Write @User a message"""
    await ctx.message.delete()
    if not member:
        embed = discord.Embed(
        title = "Command ``write``",
        color = discord.Colour.dark_gold(),
        description = f'**This command will write your text to person.\nExample: {settings["prefix"]}write [@MEMBER] [TEXT]**')
        await ctx.send(embed=embed)
        return
    try:
        member.name
    except:
        embed = discord.Embed(
        title = "Command ``write``",
        color = discord.Colour.dark_gold(),
        description = f'**This command will write your text to person.\nExample: {settings["prefix"]}write [@MEMBER] [TEXT]**')
        await ctx.send(embed=embed)
    author = ctx.message.author
    if check_for_bot_admin(author) == True:
        try:
            await member.send(message)
        except: # this will error if the user has blocked the bot or has server dms disabled
            await ctx.send(f"Sadly (((This user has forbidden to send him messages (((")
        else:
            await ctx.send(f"It was possible to send a message to {member}!")
    else:
        await ctx.send(f'{author.mention}, you do not have sufficient rights for this operation ...')
    log(ctx=ctx, Description='write', Comment=ctx.message.content)

@bot.command(aliases=["rule34"])   #aliases=["rule34"]
async def friend(ctx):
    """Just a fun GIF"""
    await ctx.message.delete()
    embed = discord.Embed(
        title="Say friend and the doors will open",
        color=discord.Colour.dark_gold())
    embed.set_image(url="https://cdn.discordapp.com/attachments/867495470989443137/878686286368636978/XAbh.gif")
    await ctx.send(embed=embed)
    log(ctx=ctx, Description='friend', Comment=ctx.message.content)
    
@bot.command()
async def fire(ctx):
    """Will just send :fire:"""
    await ctx.message.delete()
    await ctx.send(f":fire:")
    log(ctx=ctx, Description='fire', Comment=ctx.message.content)

@bot.command()
async def addlogin(ctx, *, login=None):
    """With this command you can add your login to the database"""
    await ctx.message.delete()
    if not login:
        embed = discord.Embed(
        title = "Command ``addlogin``",
        color = discord.Colour.dark_gold(),
        description = f'**This command will add your login to data base.\nExample: {settings["prefix"]}addlogin [TEXT]**')
        await ctx.send(embed=embed)
        return
    try:
        cur.execute('UPDATE passwords SET Login == ? WHERE WhoId == ?', (str(login), int(ctx.author.id)))
        base.commit()
        await ctx.send(f"Your login has been updated))))\nOnly **YOU** will be able to find it out (unless it's a server ...))))")
    except:  
        cur.execute('INSERT INTO passwords VALUES(?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), str(login), None))
        base.commit()
        await ctx.send(f"Your login has been added, but there is no password ... You can enter the '{settings['prefix']}addpass' and add it")
    log(ctx=ctx, Description='addlogin', Comment=ctx.message.content)

@bot.command()
async def addpass(ctx, *, login=None):
    """With this command you can add your password to the database"""
    await ctx.message.delete()
    if not login:
        embed = discord.Embed(
        title = "Command ``addpass``",
        color = discord.Colour.dark_gold(),
        description = f'**This command will add your login to data base.\nExample: {settings["prefix"]}addpass [TEXT]**')
        await ctx.send(embed=embed)
        return
    try:  
        base.execute('INSERT INTO passwords VALUES(?, ?, ?, ?, ?)', (time_now, ctx.author.name, int(ctx.author.id), None, str(login)))
        base.commit()
        await ctx.send(f"Your password has been added, but there is no login...\nYou can enter the '{settings['prefix']}addlogin' and add it")
    except:
        base.execute('UPDATE passwords SET Password == ? WHERE WhoId == ?', (str(login), int(ctx.author.id)))
        base.commit()
        await ctx.send(f"Your password has been updated))))\nOnly **YOU** will be able to find it out (unless it's a server ...))))")
    log(ctx=ctx, Description='addpass', Comment=ctx.message.content)

@bot.command()
async def passwd(ctx):
    """With this command you can see your username and password"""
    global msg
    log_list.append({'Author': ctx.author.id, 'Atcion': 'UsePasswd'})
    await ctx.send('Send here?')
    msg = ctx.message.id
    for emoji in ['☑', '🚫']:
       await ctx.message.add_reaction(emoji)
    log(ctx=ctx, Description='passwd', Comment=ctx.message.content)

@bot.command()
async def setbad(ctx, *, arg=None):
    '''Set bad word into the black list'''
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``setbad``",
        color = discord.Colour.dark_gold(),
        description = f'**Set bad word into the data base\nBut it`s command only for admins.\nExample: {settings["prefix"]}setbad [BAD WORD]**')
        await ctx.send(embed=embed)
        return
    if check_for_bot_admin(ctx) == True:
        try:
            base.execute('INSERT INTO bads VALUES(?, ?)', (str(arg).lower(), 0))
            base.commit()
        except:
            await ctx.send("This word is already in the database.")
        else:
            await ctx.send("Bad word set to data base)))")
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...") 
    log(ctx=ctx, Description='setbad', Comment=ctx.message.content)

@bot.command()
async def delbad(ctx, *, arg=None):
    '''Del from base bad word'''
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``delbad``",
        color = discord.Colour.dark_gold(),
        description = f'**Delete bad word from the data base\nBut it`s command only for admins.\nExample: {settings["prefix"]}delbad [BAD WORD]**')
        await ctx.send(embed=embed)
        return
    if check_for_bot_admin(ctx) == True: 
        try:
            cur.execute('DELETE FROM bads WHERE Word == ?', (str(arg),))
            base.commit()
        except:
            await ctx.send('Bad word wasn`t in base.')
        else:
            await ctx.send("Bad word delete from data base.")
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
    log(ctx=ctx, Description='delbad', Comment=ctx.message.content)
    
@bot.command()
async def setwelcomechannel(ctx, channel: discord.TextChannel=None):
    '''Set welcome channel'''
    await ctx.message.delete()
    if not channel:
        embed = discord.Embed(
        title = "Command ``setwelcomechannel``",
        color = discord.Colour.dark_gold(),
        description = f'**Set welcome channel.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setwelcomechannel [#CHANNEL]**')
        await ctx.send(embed=embed)
        return
    if check_for_bot_admin(message=ctx) == True:
        update_in_db_server(ctx=ctx, WelcomeChat=channel)
        await ctx.send("Welcome chat was update)))")
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
    log(ctx=ctx, Description='setwelcomechannel', Comment=ctx.message.content)

@bot.command()
async def setwelcomemessageserver(ctx, *, arg=None):
    '''Set welcome message'''
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``setwelcomemessageserver``",
        color = discord.Colour.dark_gold(),
        description = f'**Set welcome message in server.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setwelcomemessageserver [TEXT]**')
        await ctx.send(embed=embed)
        base_sq = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (ctx.guild.id, )).fetchone()
        embed = discord.Embed(
        title = "``Now welcome message``",
        color = discord.Colour.dark_gold(),
        description = base_sq[-2])
        await ctx.send(embed=embed)
        return
    if check_for_bot_admin(ctx) == True:
        try:
            check_in_db_server(ctx=ctx, WelcomeServerMessage=arg)
            await ctx.send("Welcome message was update)))")
        except:
            print('ERROR WITH UPDATE SERVER WELCOME')
            await ctx.send("ERROR")                                         #ErrorLog 1
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
    log(ctx=ctx, Description='setwelcomemessageserver', Comment=ctx.message.content)

@bot.command()
async def setwelcomemessageprivate(ctx, *, arg=None):
    '''Set welcome message'''
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``setwelcomemessageprivate``",
        color = discord.Colour.dark_gold(),
        description = f'**Set welcome message in PV.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setwelcomemessageprivate [TEXT]**')
        await ctx.send(embed=embed)
        base_sq = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (ctx.guild.id, )).fetchone()
        embed = discord.Embed(
        title = "``Now welcome message``",
        color = discord.Colour.dark_gold(),
        description = base_sq[-1])
        await ctx.send(embed=embed)
        return
    if check_for_bot_admin(ctx) == True:
        try:
            check_in_db_server(ctx=ctx, WelcomeMessagePivate=arg)
            await ctx.send("Welcome message was update)))")
        except:                                             #ErrorLog: 2
            print('ERROR WITH UPDATE PRIVATE WELCOME')
            await ctx.send("ERROR")
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
    log(ctx=ctx, Description='setwelcomemessageprivate', Comment=ctx.message.content)

@bot.command()
async def setmaxwarnslimit(ctx, arg=None):
    '''Set max warns limit'''
    await ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``setmaxwarnslimit``",
        color = discord.Colour.dark_gold(),
        description = f'**Set max warns limit in server.\nBut it`s command only for admins.\nExample: {settings["prefix"]}setmaxwarnslimit [NUM]**')
        await ctx.send(embed=embed)
        return
    try:
        if int(arg) <= 0:
            await ctx.send('**The number of warnings cannot be <= 0 !!!**')
            return
    except:
        await ctx.send('**The argument must be an integer !!!**')
        return
    if check_for_bot_admin(ctx) == True: 
        try:
            update_in_db_server(ctx=ctx, CounterMaxWARNS=arg)
        except:                         #ErrorLog: 1
            await ctx.send('ERROR')
        else:
            await ctx.send("Max counter warns was update.")
    else:
        await ctx.send(f"{ctx.author.mention}, you aren't an admin...")
        await ctx.message.delete()
    log(ctx=ctx, Description='setmaxwarnslimit', Comment=ctx.message.content)

@bot.command()
async def setblack(ctx, *, arg=None):
    ctx.message.delete()
    if not arg:
        embed = discord.Embed(
        title = "Command ``setblack``",
        color = discord.Colour.dark_gold(),
        description = f'**This is a secret command that can only be used by the bot creator. \nThis command will add a word or more to the BLACK LIST. \nIf someone writes these words, they will immediately be banned everywhere. \nFor example, for fraudulent links such as with free nitro**')
        await ctx.send(embed=embed)
        return
    base = cur.execute('SELECT * FROM nice WHERE whoId == ?', (ctx.member.id,)).fetchone()
    if not base:
        ctx.send('You aren`t developer!!!')
        log(ctx=ctx, Description='try setblack', Comment=ctx.message.content)
        return
    try:
        cur.execute('INSERT INTO blacklist VALUES(?, ?)', (str(arg), 0))
        base.commit()
        await ctx.channel.send('Set to black list.')
    except:
        await ctx.channel.send('Already in base.')
    log(ctx=ctx, Description='setblack', Comment=ctx.message.content)

@bot.command()
async def trusted(ctx, *, member: discord.Member=None):
    ctx.message.delete()
    if not member:
        embed = discord.Embed(
        title = "Command ``trusted``",
        color = discord.Colour.dark_gold(),
        description = f'**This is a secret command that can only be used by bot creator. \nThis command will add member to the TRUSTED LIST. \nThis member becomes with the rights of the bot creator.**')
        await ctx.send(embed=embed)
        return
    if ctx.author.id == 561181047317069827:
        cur.execute('INSERT INTO nice VALUES(?, ?)', (member.name, member.id))
        base.commit()
        embed = discord.Embed(
            title = f"You have become a trusted person!",
            description = 'Now the commands are available to you: \n``setblack``',
            color = discord.Colour.dark_gold())
        await member.send(embed=embed)
        await ctx.send('Ok')
# @bot.event
# async def yt(ctx, url):

#     author = ctx.message.author
#     voice_channel = author.voice_channel
#     vc = await bot.join_voice_channel(voice_channel)

#     player = await vc.create_ytdl_player(url)
#     player.start()

@bot.event
async def on_raw_reaction_add(payload):
    member = payload.member
    try:
        pass_base = None
        channel = bot.get_channel(payload.channel_id)
        for i in log_list:
            if i['Author'] == member.id:
                if payload.user_id != bot.user.id:
                    try:
                        pass_base = cur.execute('SELECT * FROM passwords WHERE WhoId == ?', (int(member.id),)).fetchone()
                        if not pass_base:
                            vizov_iscluchenija
                    except:       
                        await channel.send(f"Sorry, but you are not in my database... \nYou can enter yourself by writing the command **addlogin** and **addpass**")
                        return
                    #await channel.send(f'Получена реакция: {payload.emoji}')
                    if f'{str(payload.emoji)}' == '☑':        
                        await channel.send(f'Well, as you know ... If this is a server chat, then blame yourself ....')
                        await channel.send(f'Here is your username and password))) Use it 😉\nLogin: **{pass_base[3]}**\nPassword: **{pass_base[4]}**')       
                    else:    
                        await channel.send("That's right!)\nCheck a PV)))")
                        temp_bool = await member.send(f'Here is your username and password))) Use it 😉\nLogin: **{pass_base[3]}**\nPassword: **{pass_base[4]}**')  
                        if temp_bool == False:
                            await channel.send(f'{member.mention}, you blocked my messages(((')
                log_list.remove(i)
                break
    except:
        pass
    log(ctx=payload, Description='on_raw_reaction_add', Comment=f'Reaction: {str(payload.emoji)}', Action='Event')

@bot.event
async def on_message(message: discord.Message):
    message_content = {i.lower().translate(str.maketrans('','', string.punctuation)) for i in message.content.split(' ')}
    if message.content[1:7] != 'setbad' and message.content[1:7] != 'delbad'and message.content[1:7] != 'delbad'and message.content[1:7] != 'delbad':
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
                log(ctx=message, Action='Warn', Description=message.content, ErrorLog='Ok', Comment=f'Word: ' + i)
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
    check_in_db_server(ctx=message)
    admin_level = check_for_bot_admin(message=message)
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, message.author.name, int(message.author.id), message.author.guild.name, message.author.guild.id, 'Write', message.content, admin_level, 'Ok', None))
    base.commit()
    await bot.process_commands(message)

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
    welcome_message = server_base[-1]
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
        max_counter_warns = give_max_counter_warns(member=member)
        if arg >= max_counter_warns:
            #await message.author.ban(reason= "{}: {}".format(message.author, "Warning limit reached"))
            await member.kick(reason= "{}: {}".format(member, "Warning limit reached"))
            await member.author.send(f'You were kicked from the server because you have too many warnings. This server has a maximum of ``{max_counter_warns}`` warnings, well, you have ``{arg}`` of them.')
            for ch in bot.get_guild(member.guild.id).channels:
                if ch.id == server_base[3]:
                    await bot.get_channel(ch.id).send('Warning limit reached... He is a bag guy...')
                log(ctx=member, Description='Too many warns', Action='kicked')
            return
    else:
        base.execute('INSERT INTO warns VALUES(?, ?, ?)', (int(idperson), str(member.name), 0))
        base.commit()
    welcome_message = server_base[-2]
    try:
        for ch in bot.get_guild(member.guild.id).channels:
            if ch.id == server_base[6]:
                await bot.get_channel(ch.id).send(welcome_message.format(prefix=settings["prefix"], member=member.mention))
    except:
        try:
            for ch in bot.get_guild(member.guild.id).channels:
                if ch.id == server_base[6]:
                    await bot.get_channel(ch.id).send(welcome_message.format(prefix=settings["prefix"]))
        except:
            try:
                for ch in bot.get_guild(member.guild.id).channels:
                    if ch.id == server_base[6]:
                        await bot.get_channel(ch.id).send(welcome_message.format(member=member.mention))
            except:   
                for ch in bot.get_guild(member.guild.id).channels:
                    if ch.id == server_base[6]:
                        await bot.get_channel(ch.id).send(welcome_message)
    log(ctx=member, Description=f'To {member.guild.name}', Action='Join')

@bot.event
async def on_member_remove(member):
    print(f'{member.name} was remove')
    this_guild = bot.get_guild(member.guild.id)
    guild_id = this_guild.id
    server_base = cur.execute('SELECT * FROM servers WHERE ServerID == ?', (int(guild_id),)).fetchone()
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.id == server_base[-3]:
            await bot.get_channel(ch.id).send(f'{member.mention}, we will miss you (((((((')
    log(member=member, Description=f'From {member.guild.name}', Action='Remove')

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
    base.execute('CREATE TABLE IF NOT EXISTS {}(ServerName, ServerID PRIMARY KEY, AdminRole, CounterMembers, CounterMaxWARNS, WelcomeChatName, WelcomeChatId, WelcomeServerMessage, WelcomeMessagePivate)'.format('servers'))#9
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(Word PRIMARY KEY, CounterUse)'.format('bads'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(WhenTime, WhoName, WhoId, WhereName, WhereId, Action, Description, AdminStatus, ErrorLog, Comment)'.format('logs'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(Word PRIMARY KEY, CounterUse)'.format('blacklist'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(Time, Who, WhoId PRIMARY KEY, Login, Password)'.format('passwords'))
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS {}(Who, whoId PRIMARY KEY)'.format('nice'))
    base.commit()
    cur.execute('INSERT INTO logs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (time_now, 'Bot', None, 'Global', None, 'Start', 'Bot started', 666, 'Ok', None))
    base.commit()
    await bot.change_presence(activity=discord.Game(name="{}help".format(settings["prefix"])))
    #await bot.change_presence(activity=discord.Streaming(name="My Stream", url='test'))

@bot.command()
async def test(ctx):
    global a
    a = 'Bla'

@bot.command()
async def test1(ctx):
    print(a)
@bot.command()
async def test2(ctx):
    global a
    del(a)

bot.run(settings['token']) # Обращаемся к словарю settings с ключом token, для получения токена
