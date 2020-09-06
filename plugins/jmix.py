
from PIL import Image
from database import *
import base64
import io
import aiohttp
from kutana import Plugin
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Жмыхает фоточки", cmds=[{'command': 'жмых [фото]', 'desc': 'делает упоротую фотку', 'vip': True}])
ACCESS_TOKEN = "my-api-token he he boi"

@plugin.on_startswith_text("жмых")
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

    image = None
    async with aiohttp.ClientSession() as sess:
        async with sess.get(attach.link) as resp:
            image = Image.open(io.BytesIO(await resp.read()))

    if image is None:
        await env.reply("Ерунда какая-то! Ошибка...")
        return "DONE"

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    await env.reply("Начался процесс обработки вашей фотографии жмыха. Он может занимать от одной до пяти минут.")
    #try:
    form = aiohttp.FormData()
    form.add_field('photo', buffer, filename="lel.jpg", content_type='application/octet-stream')

    result = None
    async with aiohttp.ClientSession() as sess:
        async with sess.post(f'https://api.kotrik.ru/api/distortKEKLOL?token={ACCESS_TOKEN}',
                                data=form) as resp:
            try:
                await resp.json(content_type=None)
                return await env.reply("Ошибка при запросе на сервер!")
            except:
                result = await env.upload_photo(io.BytesIO(await resp.read()))

    return await env.reply("Держи", attachment=result)