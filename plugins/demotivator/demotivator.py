from kutana import Plugin

from utils import priviligeshelper
from utils.static_text import need_vip

import aiohttp
import io

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

plugin = Plugin(name="Демотиваторы", cmds=[
    {'command': 'демотиватор <текст сверху> <текст снизу C НОВОЙ СТРОКИ!> [вложение(фото)]', 'desc': 'бот делает пикчу 2013 года LoL', 'vip': True}
])

PATH = "plugins/demotivator/"
sizes = (571, 604)

@plugin.on_startswith_text("демотиватор")
async def demotivator(msg, att, env):
    if not await priviligeshelper.getUserPriviliges(env, msg.from_id) & priviligeshelper.USER_VIP > 0:
        return await env.reply(need_vip)

    strings = env['body'].split("\n")
    if not env.args or len(strings) < 2:
        return await env.reply("нужно больше аргументов(")
    if not att or att[0].type != "photo":
        return await env.reply("пришли картиночку(")
    
    img_to_paste = None
    async with aiohttp.ClientSession() as sess:
        async with sess.get(att[0].link) as response:
            img_to_paste = Image.open(io.BytesIO(await response.read()))

    base_img = Image.open(PATH+"base.jpg")
    draw = ImageDraw.Draw(base_img)

    big_font_size = 43
    small_font_size = 19

    font = ImageFont.truetype(PATH+"ariblk.ttf", big_font_size)
    font2 = ImageFont.truetype(PATH+"arial.ttf", small_font_size)

    w, _ = draw.textsize(strings[0], font=font)
    w1, _ = draw.textsize(strings[1], font=font2)

    while w+20 > sizes[0]:
        big_font_size-=1
        font = ImageFont.truetype(PATH+"ariblk.ttf", big_font_size)
        w, _ = draw.textsize(strings[0], font=font)

    while w1+20 > sizes[0]:
        small_font_size-=1
        font2 = ImageFont.truetype(PATH+"arial.ttf", small_font_size)
        w1, _ = draw.textsize(strings[1], font=font2)

    draw.text(( (sizes[0]-w)/2 , 490), strings[0], fill=(255,255,255), font=font)
    draw.text(( (sizes[0]-w1)/2, 550), strings[1], fill=(255,255,255), font=font2)

    img_to_paste = img_to_paste.resize((451, 448), Image.ANTIALIAS)
    base_img.paste(img_to_paste, (60, 37))

    buffer = io.BytesIO()
    base_img.save(buffer, format='png')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    return await env.reply('держи!', attachment=result)
