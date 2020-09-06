from database import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

import aiohttp
from datetime import datetime
import io

from utils import priviligeshelper
from utils.static_text import need_vip

from kutana import Plugin

plugin = Plugin(name="Скрин диалога", cmds=[{'command': 'скрин диалога', 'desc': 'Скринит диалог из пересланных сообщений', 'vip': True}])

PATH = "plugins/dialogscreen/"
f_s = 13

font1 = ImageFont.truetype(PATH+"roboto.ttf", f_s)
font2 = ImageFont.truetype(PATH+"roboto_t.ttf", f_s)

def calculate_size(text):
    textsss = text.split("\n")
    minw = 0
    maxh = 0
    for x in textsss:
        if x == "":
            x = "1"
        fsd = font1.getsize(x)
        if fsd[0] > minw:
            minw = fsd[0]
        maxh+=fsd[1]

    return (minw, maxh)


class Message:

    def __init__(self, avatar, time, text, name):
        self.name = name
        self.avatar = avatar
        self.time = time
        self.text = text
        self.img = None

    def calc_image(self):
        font_size1 = font1.getsize(self.name)
        font_size15 = font1.getsize("00:00  ")
        font_size2 = font1.getsize(self.text) if not self.text.find("\n") != -1 else calculate_size(self.text)

        img = Image.new('RGB', (200+32+font_size2[0]+font_size15[0], 20+18+font_size1[1]+font_size2[1]), (255, 255, 255))

        avatar = Image.open(self.avatar).resize((42,42)) if type(self.avatar) == str else self.avatar.resize((42, 42))
        ll_size = (1000, 1000)
        mask = Image.new('L', ll_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + ll_size, fill=255)

        mask = ImageOps.fit(mask, avatar.size, method=Image.BICUBIC, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        img.paste(avatar, (f_s, f_s), avatar)
        draw = ImageDraw.Draw(img)

        draw.text((f_s+42+10,f_s), self.name, font=font1, fill=(66, 100, 139))
        draw.text((f_s+42+15+font_size1[0],f_s), self.time, font=font2, fill=(120,127,140))
        draw.text((f_s+42+10,f_s+13+6), self.text, font=font2, fill=(0,0,0))

        self.img = img


@plugin.on_startswith_text("скрин диалога")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_VIP<=0:
        return await env.reply(need_vip)

    posdd = 0
    messages = []

    i, url, name, last_name, idu = None, None, None, None, None
    for m in message.raw_update["object"]["fwd_messages"]:
        if m['text']:
            if i == m['from_id']:
                messages[posdd-1].text+="\n\n"+m['text']
                continue

            i = m['from_id']

            u = await env.request('users.get', user_ids=i, fields="photo_100")
            if not u: continue

            if len(u.response)<1:
                return await env.reply("Нечего цитировать!")
            u = u.response[0]

            url = u["photo_100"]
            name = u["first_name"]
            last_name = u["last_name"]

            async with aiohttp.ClientSession() as sess:
                async with sess.get(url) as response:
                    img = Image.open(io.BytesIO(await response.read()))

            text = m['text']
            date = m['date']
            messages.append(Message(img, datetime.utcfromtimestamp(date).strftime('%H:%M'), text, name+" "+last_name))
            posdd+=1
    else:
        if i is None:
            return await env.reply("Нечего цитировать!")

    width = 0
    height = 0

    for msg in messages:
        msg.calc_image()

        if width < msg.img.size[0]:
            width = msg.img.size[0]

        height+=msg.img.size[1]

    img = Image.new('RGB', (width, height), (255,255,255))
    last_pos_y = 0
    for msg in messages:
        if last_pos_y == 0:
            img.paste(msg.img, (0, last_pos_y))
        else:
            img.paste(msg.img, (0, last_pos_y))
        last_pos_y+=msg.img.size[1]-f_s+4

    f = io.BytesIO()
    img.save(f, format='png')
    f.seek(0)
    attachment = await env.upload_photo(f)
    f.close()

    return await env.reply('Забирай', attachment=attachment)
