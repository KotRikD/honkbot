
from PIL import Image
from database import *
import io
import aiohttp
from kutana import Plugin
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Чёрно-белые фоточки", cmds=[{'command': 'чб [фото]', 'desc': 'делает фоточку чёрно-белой', 'vip': True}])


@plugin.on_startswith_text("чб")
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
            img = Image.open(io.BytesIO(await response.read())).convert('LA')

    #Если всё ок!
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    result = await env.upload_photo(buffer)

    return await env.reply("Держи", attachment=result)