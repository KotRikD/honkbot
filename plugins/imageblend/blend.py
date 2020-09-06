from kutana import Plugin
from database import *
import operator
from PIL import Image
from PIL import ImageDraw

from utils import priviligeshelper
from utils.static_text import need_vip
import io
import os
import aiohttp
import random

plugin = Plugin(name="Набор смешиваний", cmds=[{'command': 'тлен <фото>', 'desc': 'сделать тлен картинку', 'vip': True},
                                               {'command': 'вьетнам <фото>', 'desc': 'сделать вьетнам картинку', 'vip': True}])

PATH = "plugins/imageblend/"

@plugin.on_startswith_text("тлен")
async def on_message(message, attachments, env):
    if not await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_VIP>0:
        return await env.reply(need_vip)

    photo = False
    for x in attachments:
        if x.type == "photo":
            photo = True
            break

    if not photo:
        return await env.reply('Вы не прислали фото!')

    attach = attachments[0]

    if not attach.link:
        return await env.reply('Вы не прислали фото!')

    async with aiohttp.ClientSession() as sess:
        async with sess.get(attach.link) as response:
            img1 = Image.open(io.BytesIO(await response.read()))

    if not img1:
        return await env.reply('К сожалению, ваше фото исчезло!')

    tlen = os.listdir(PATH+"tlen")
    nameimg = random.choice(tlen)

    img2 = Image.open(f'{PATH+"tlen"}/{nameimg}')
    img2 = img2.resize(img1.size, Image.BILINEAR)

    if img1.size[0] >1000:
        img1 = img1.resize((img1.size[0], img2.size[1]), Image.BILINEAR)

    if img1.size[1]>1000:
        img1 = img1.resize((img2.size[0], img1.size[1]), Image.BILINEAR)

    shift = (0, 0)
    nw, nh = map(max, map(operator.add, img2.size, shift), img1.size)

    newimg1 = Image.new('RGBA', size=img1.size, color=(0, 0, 0, 0))
    newimg1.paste(img2, shift)
    newimg1.paste(img1, (0, 0))

    newimg2 = Image.new('RGBA', size=img1.size, color=(0, 0, 0, 0))
    newimg2.paste(img1, (0, 0))
    newimg2.paste(img2, shift)

    result = Image.blend(newimg1, newimg2, alpha=0.5)

    buffer = io.BytesIO()
    result.convert('LA').save(buffer, format='PNG')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    await env.reply('Держи', attachment=result)

@plugin.on_startswith_text("вьетнам")
async def on_message(message, attachments, env):
    if not await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
        return await env.reply(need_vip)

    photo = False
    for x in attachments:
        if x.type == "photo":
            photo = True
            break

    if not photo:
        return await env.reply('Вы не прислали фото!')

    attach = attachments[0]

    if not attach.link:
        return await env.reply('Вы не прислали фото!')

    async with aiohttp.ClientSession() as sess:
        async with sess.get(attach.link) as response:
            img1 = Image.open(io.BytesIO(await response.read()))

    if not img1:
        return await env.reply('К сожалению, ваше фото исчезло!')

    vietnam = os.listdir(PATH+"vietnam")
    nameimg = random.choice(vietnam)

    img2 = Image.open(f'{PATH+"vietnam"}/{nameimg}')
    img2 = img2.resize(img1.size, Image.BILINEAR)

    if img1.size[0] >1000:
        img1 = img1.resize((img1.size[0], img2.size[1]), Image.BILINEAR)

    if img1.size[1]>1000:
        img1 = img1.resize((img2.size[0], img1.size[1]), Image.BILINEAR)

    shift = (0, 0)
    nw, nh = map(max, map(operator.add, img2.size, shift), img1.size)

    newimg1 = Image.new('RGBA', size=img1.size, color=(0, 0, 0, 0))
    newimg1.paste(img2, shift)
    newimg1.paste(img1, (0, 0))

    newimg2 = Image.new('RGBA', size=img1.size, color=(0, 0, 0, 0))
    newimg2.paste(img1, (0, 0))
    newimg2.paste(img2, shift)

    result = Image.blend(newimg1, newimg2, alpha=0.5)

    buffer = io.BytesIO()
    result.convert('LA').save(buffer, format='PNG')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    await env.reply('Держи', attachment=result)
