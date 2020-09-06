from kutana import Plugin
from database import *

plugin = Plugin(name="Ударить", cmds=[{'command': 'уебу <имя человека>', 'desc': 'у*бать человека'}])

import random
from PIL import Image
import io

imgs = ['1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg']
PATH="plugins/yeby/"

@plugin.on_startswith_text("уебу")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("А кого бить будем?")

    text = ' '.join(env['args'])
    img = Image.open(PATH+random.choice(imgs))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    result = await env.upload_photo(buffer)

    return await env.reply(f"[id{message.from_id}|Этот парень взял и уебал] {text}", attachment=result)