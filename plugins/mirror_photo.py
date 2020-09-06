import io
import aiohttp
from PIL import Image

from kutana import Plugin
from database import *
from utils.static_text import need_vip
from utils import priviligeshelper

FAIL_MSG = 'К сожалению, произошла какая-то ошибка :('

plugin = Plugin(name="Зеркало", cmds=[{'command': 'отзеркаль <фото>', 'desc': 'отзеркаливает фото', 'vip': True}])


@plugin.on_startswith_text("отзеркаль")
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
            img = Image.open(io.BytesIO(await response.read()))

    if not img:
        return await env.reply('К сожалению, ваше фото исчезло!')

    w, h = img.size

    part = img.crop((0, 0, w / 2, h))
    part1 = part.transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(part1, (round(w / 2), 0))

    buffer = io.BytesIO()
    img.save(buffer, format='png')
    buffer.seek(0)
    result = await env.upload_photo(buffer)

    return await env.reply('Держи', attachment=result)