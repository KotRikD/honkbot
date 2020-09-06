from database import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

import aiohttp
import datetime, io
import os

from utils import priviligeshelper
from utils.static_text import need_vip

import numpy as np
import aiohttp

from kutana import Plugin

plugin = Plugin(name="Echo", cmds=[{'command': 'цитата [титул]', 'desc': 'Перешлите сообщение и укажите титул (по желанию) и получите цитату!'},
                                   {'command': 'цитата фон (сброс)', 'desc': 'Установить свой фон для цитат', 'vip': True}])

PATH = "plugins/quote/"

q = Image.open(PATH+"q.png").resize((40, 40), Image.LANCZOS)
qf = q.copy().transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)

font1 = ImageFont.truetype(PATH+"font.ttf", 20)
fs = ImageFont.truetype(PATH+"font.ttf", 14)

@plugin.on_startup()
async def on_startup(update, env):
    if not os.path.exists(f"{PATH}quote_bgs/"):
        os.makedirs(f"{PATH}quote_bgs/")

@plugin.on_startswith_text("цитата фон")
async def on_message(message, attachments, env):
    if not await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
        return await env.reply(need_vip)

    if not len(env['args'])<1 and env['args'][0].startswith("сброс"):
        try:
            os.remove(PATH+f"quote_bgs/{message.from_id}.png")
        except:
            pass
        return await env.reply("Готово")

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
            img = Image.open(io.BytesIO(await response.read()))

    width, height = img.size

    if width < 700 or width > 700 or height < 400 or height > 400:
        img = img.resize((700, 400), Image.ANTIALIAS)
        await env.reply("Изображение было сконвертировано под 700x400")

    img.save(f"{PATH}quote_bgs/{message.from_id}.png", format='PNG')
    await env.reply("Готово")
    return "DONE"

@plugin.on_startswith_text("цитата")
async def on_message(message, attachments, env):
    if env['args']:
        otext = ' '.join(env['args'])
    else:
        otext = False

    i, url, name, last_name, idu = None, None, None, None, None

    for m in message.raw_update["object"]["fwd_messages"]:
        if m['text']:
            if i == m['from_id']:
                text += "\n" + m['text']
                continue
            elif i is not None:
                break

            i = m['from_id']

            u = await env.request('users.get', user_ids=i, fields="photo_max")
            if not u: continue

            if len(u.response)<1:
                return await env.reply("Нечего цитировать!")
            u = u.response[0]

            url = u["photo_max"]
            name = u["first_name"]
            last_name = u["last_name"]
            idu = u["id"]

            text = m['text']
    else:
        if i is None:
            return await env.reply("Нечего цитировать!")

    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as response:
            img = Image.open(io.BytesIO(await response.read())).convert("RGB")
            img = img.resize((200, 200))

            ll_size = (1000, 1000)
            mask = Image.new('L', ll_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + ll_size, fill=255)

            mask = ImageOps.fit(mask, img.size, method=Image.BICUBIC, centering=(0.5, 0.5))
            img.putalpha(mask)

    rsize = (700, 400)

    if os.path.isfile(f"{PATH}quote_bgs/{idu}.png"):
        res = Image.open(f"{PATH}quote_bgs/{idu}.png").convert('RGBA')
    else:
        res = Image.open(PATH+"bg.png").convert('RGBA')

    data = np.array(res)
    red, green, blue, alpha = data.T

    if any(number > 186 for number in (red*0.299 + green*0.587 + blue*0.114)[0]):
        color = (0,0,0)
    else:
        color = (255,255,255)

    res.paste(img, (25, 100), img)

    tex = Image.new("RGBA", rsize, color=(0, 0, 0, 0))

    draw = ImageDraw.Draw(tex)

    sidth = draw.textsize(" ", font=font1)[0]
    seight = int(draw.textsize("I", font=font1)[1] * 1.05)

    text = text.splitlines()

    midth = 0
    width = 0
    height = 0
    for line in text:
        for word in line.split(" "):
            size = draw.textsize(word, font=font1)

            if width + size[0] >= rsize[0] - 340:
                height += seight
                width = 0

            draw.text((width, height), word, font=font1, fill=color)
            width += sidth + size[0]

            if width > midth:
                midth = width

        height += seight
        width = 0

    y = rsize[1] // 2 - height // 2
    x = 300 + (rsize[0] - 370 - midth) // 2
    res.alpha_composite(tex, (x, y))

    if height < 210:
        height = 210
        y = rsize[1] // 2 - height // 2

    res.alpha_composite(q, (250, y + 10))
    res.alpha_composite(qf, (rsize[0] - 75, y + int(height - seight * 2 + 10)))

    draw = ImageDraw.Draw(res)
    draw.multiline_text((25, 310), f"© {name} {last_name}{' - ' + otext if otext else ''}\n"
                                   f"@ {datetime.date.today()}", font=fs, fill=color)

    f = io.BytesIO()
    res.save(f, format='png')
    f.seek(0)
    attachment = await env.upload_photo(f)
    f.close()

    return await env.reply('Забирай', attachment=attachment)
