import io
import aiohttp
from PIL import Image
import PIL.ImageOps
from database import *
from kutana import Plugin
from utils import priviligeshelper

FAIL_MSG = 'К сожалению, произошла какая-то ошибка :('

plugin = Plugin(name="Инверт", cmds=[{'command': 'инверт <фото>', 'desc': 'инвертирует фото', 'vip': True}])


@plugin.on_startswith_text("инверт")
async def on_message(message, attachments, env):
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

    img2 = PIL.ImageOps.invert(img)

    buffer = io.BytesIO()
    img2.save(buffer, format='png')

    buffer.seek(0)
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_VIP>0:
        result = await env.upload_photo(buffer)
        return await env.reply('Держи', attachment=result)
    else:
        return await env.reply("У тебя нету доступа к этой команде.\n Подробнее на моей стене.")
