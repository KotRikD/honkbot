from kutana import Plugin
from PIL import Image
from database import *

import io
import aiohttp
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Полосочки", cmds=[{'command': 'line [фото]', 'desc': 'делает те самые полоски'}])

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def is_even(l):
    if l % 2 == 0:
        return True
    else:
        return False

@plugin.on_startswith_text("line")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_VIP > 0):
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
            image = Image.open(io.BytesIO(await response.read()))

    w,h = image.size

    mixed = chunks(list(range(h)), 2)

    str_pos = -1
    for x in mixed:
        str_pos+=1
        if not is_even(str_pos):
            continue

        for y in x:
            for d in range(w):
                image.putpixel((d, y), (0,0,0))

    #Если всё ок!
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    result = await env.upload_photo(buffer)

    return await env.reply("Держи", attachment=result)