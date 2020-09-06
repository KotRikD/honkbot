from kutana import Plugin
from database import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import io

from utils import priviligeshelper
from utils.static_text import need_vip

plugin = Plugin(name="Банка с колой", cmds=[{'command': 'cola <текст>', 'desc': 'создать колу с текстом', 'vip': True}])

PATH = "plugins/coca/"

@plugin.on_startswith_text("cola")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_VIP<=0:
        return await env.reply(need_vip)

    if not env['args']:
        return await env.reply("Нету имени")

    img = Image.open(PATH+"bg.png")
    name = ' '.join(env['args'])
    if len(name) > 14:
        return await env.reply("Максимум 15 символов")

    imageSize = img.size
    fontSize = int(imageSize[1] / 4 - len(name) / 2 - 20)
    font = ImageFont.truetype(PATH+"font.ttf", fontSize)
    bottomTextSize = font.getsize(name)

    bottomTextPositionX = 58
    bottomTextPositionY = 87 + int(imageSize[1] / 4 - 40)
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)

    draw = ImageDraw.Draw(img)
    draw.text(bottomTextPosition, name, (255,255,255), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='png')
    buffer.seek(0)
    result = await env.upload_photo(buffer)
    await env.reply('Держи', attachment=result)
