import asyncio
import random
from plugins.check import tokens
#import smbclient

from kutana import Plugin
from kutana.controller_vk import VKController
import random
from database import *
from kutana.plugin import Attachment
import aiohttp
from utils.static_text import need_vip
from utils import VKKeyboard

import io
from PIL import Image

from utils import priviligeshelper

plugin = Plugin(name="ANIME-MEMES!!!!", cmds=[
    {'command': 'лоли', 'desc': 'случайные лоли'},
    {'command': 'аниму', 'desc': 'случайные аниме-приколы'},
    {'command': 'чулочки', 'desc': 'случайные тян с чулочками', 'vip': True},
    {'command': 'кантай', 'desc': 'случайные корабли.'},
    {'command': 'ловлайв', 'desc': 'рандом канон с Love Live!'},
    {'command': 'яой', 'desc': 'Аниме кун с куном'},
    {'command': 'юри', 'desc': 'Аниме тян с тян'},
    {'command': 'fap', 'desc': 'ya iz anglii pribil', 'cheat': True},
    # {'command': 'хентай', 'desc': 'рандомный хентай из личного архива', 'vip': True},
    {'command': 'волк', 'desc': 'Волк в цирке не выступает'}
])

# Стоп лист для текста в посте
stop_list = ['http', '[club', '[public', '[id']

# Функция проверки вхождения элементов списка a в строку "b"
any_in = lambda word_list, string: any(i in string for i in word_list)

def convert_to_attachment_d(attachment, attachment_type=None):
    if "type" in attachment and attachment["type"] in attachment:
        body = attachment[attachment["type"]]
        attachment_type = attachment["type"]
    else:
        body = attachment

    if "sizes" in body:
        m_s_ind = -1
        m_s_wid = 0

        for i, size in enumerate(body["sizes"]):
            if size["width"] > m_s_wid:
                m_s_wid = size["width"]
                m_s_ind = i

        link = body["sizes"][m_s_ind]["url"]  # src

    elif "url" in body:
        link = body["url"]

    else:
        link = None

    return Attachment(
        attachment_type,
        body.get("id"),
        body.get("owner_id"),
	"0",
        link,
        attachment
    )

async def give_memes_with_reupload(env, group_id):
    """Получает фотографию из случайного поста выбранной группы"""
    answer = ''
    photo = None
    attach = None

    # Пока мы не нашли фотографию
    while not photo:
        # Получаем 10 постов и перемешиваем их
        async with VKController(random.choice(tokens)) as user_api:
            datad = await user_api.raw_request('wall.get', owner_id=group_id, count=1)
            data = datad.response

            datad = await user_api.raw_request('wall.get', owner_id=group_id, offset=random.randint(1, data['count']-1), count=10)
            data = datad.response

        if datad.error:
            break

        items = random.sample(data.get('items'), len(data.get('items')))
        for item in items:
            content = item['text']
            attaches = item.get('attachments')
            # Если в тексте поста есть запрещенные слова или нет документов
            if any_in(stop_list, content) or not attaches:
                continue
            # Если одна картинка
            if len(attaches) == 1:
                answer = content if content else ''
                photo = convert_to_attachment_d(attaches[0], "photo")

        async with aiohttp.ClientSession() as sess:
            async with sess.get(photo.link) as resp:
                attach = await env.upload_photo(await resp.read())

    await env.reply("", attachment=attach)

async def give_memes(env, group_id, type):
    """Получает фотографию из случайного поста выбранной группы"""
    answer = ''
    photo = None

    # Пока мы не нашли фотографию
    while not photo:
        # Получаем 10 постов и перемешиваем их
        async with VKController(random.choice(tokens)) as user_api:
            datad = await user_api.raw_request('wall.get', owner_id=group_id, count=1)
            data = datad.response
            print(data['count'])
            datad = await user_api.raw_request('wall.get', owner_id=group_id, offset=random.randint(1, data['count']-1), count=10)
            data = datad.response

        if datad.error:
            break

        items = random.sample(data.get('items'), len(data.get('items')))
        for item in items:
            content = item['text']
            attaches = item.get('attachments')
            # Если в тексте поста есть запрещенные слова или нет документов
            if any_in(stop_list, content) or not attaches:
                continue
            # Если одна картинка
            if len(attaches) == 1:
                answer = content if content else ''
                photo = attaches[0].get('photo')
    if not photo:
        return 
    oid = photo['owner_id']
    att_id = photo['id']

    attachment = f'photo{oid}_{att_id}'
    kb = await get_keyboard(type, env.eenv)
    await env.reply("", attachment=attachment, keyboard=kb)

async def get_keyboard(type, eenv):
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': f'Ещё {type}', 'payload': {'command': f'{eenv.prefix}{type}'}, 'color': 'primary'}
        ]
    })
    return kb.dump_keyboard()

@plugin.on_startswith_text("аниму")
async def lolies(message, attachments, env):
    group_id = -84054237
    await give_memes(env, group_id, "аниму")

@plugin.on_startswith_text("яой")
async def lolies(message, attachments, env):
    group_id = -38230251
    #if not await get_or_none(Role, user_id=message.from_id, role="vips"):
    await give_memes(env, group_id, "яой")

@plugin.on_startswith_text("юри")
async def lolies(message, attachments, env):
    group_id = -120926022
    await give_memes(env, group_id, "юри")

@plugin.on_startswith_text("чулочки")
async def lolies(message, attachments, env):
    group_id = -102853758
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_VIP>0:
        await give_memes(env, group_id, "чулочки")
    else:
        await env.reply(need_vip)

@plugin.on_startswith_text("ловлайв")
async def lolies(message, attachments, env):
    group_id = random.choice([-68517027, -146263552, -128660232])

    await give_memes(env, group_id, "ловлайв")

@plugin.on_startswith_text("кантай")
async def kantai(message, attachments, env):
    group_id = -30953411
    await give_memes(env, group_id, "кантай")

@plugin.on_startswith_text("fap")
async def fap(message, attachments, env):
    group_id = -100326393
    await give_memes(env, group_id, "fap")

@plugin.on_startswith_text("волк")
async def wolf(message, attachments, env):
    group_id = -186768719
    await give_memes(env, group_id, "волк")

@plugin.on_startswith_text("лоли")
async def lolies(message, attachments, env):
    public_ids = [
    #    -146095564,
        -157516431,
        -182894249,
        -101072212,
        -77770779,
        -173849123,
        -143737998  
    ]

    await give_memes(env, random.choice(public_ids), "лоли")

# @plugin.on_startswith_text("хентай")
# async def fap(message, attachments, env):
#     if not await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
#         return await env.reply(need_vip)
    
#     public_ids = [
#         -145446964,
#         -119561847,


#     ]

#     await give_memes(env, random.choice(public_ids), "лоли")

#@plugin.on_startswith_text("хентай")
#async def hentai(message, attachments, env):
#    if not await get_or_none(Role, user_id=message.from_id, role="vips"):
#        return await env.reply("Ты не вип!")

#    hentai_imgs = smb.listdir("/")
#    image = Image.open(io.BytesIO(smb.open(random.choice(hentai_imgs), 'rb').read()))
#    buffer = io.BytesIO()
#    image.save(buffer, format='PNG')
#    buffer.seek(0)

#    result = await env.upload_photo(buffer)

#    return await env.reply("Держи!", attachment=result)


