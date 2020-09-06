from PIL import Image
from database import *
import io
import aiohttp
from kutana import Plugin
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Из шакалю есть же!", cmds=[{'command': 'шакализм <качество> [фото]', 'desc': 'чё шакалишь да?', 'vip': True}])


@plugin.on_startswith_text("шакализм")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_VIP > 0):
        return await env.reply(need_vip)

    if not env['args'] or not env['args'][0].isdigit():
        return await env.reply("Аргументы введены не вверно.")

    if int(env['args'][0]) > 100:
        return await env.reply("Больше низзззззя")

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

    buffer = io.BytesIO()
    img.save(buffer, "jpeg", quality=int(env['args'][0]))
    buffer.seek(0)

    result = await env.upload_photo(buffer)

    return await env.reply("Чё, шакалишь да?", attachment=result)


