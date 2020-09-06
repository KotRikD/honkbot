import io
import PIL
import aiohttp
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from kutana import Plugin

plugin = Plugin(name="Я ...", cmds=[{'command': 'я', 'desc': 'делает я картинку'}])

PATH = "plugins/nikon/"

FAIL_MSG = 'К сожалению, произошла какая-то ошибка :('

@plugin.on_startswith_text("я")
async def on_message(message, attachments, env):
    img = Image.open(PATH+"ya.png")

    if not env['args']:
        return await env.reply(f"Текст укажи. я <текст>.\n Если хочешь использовать несколько слов в строке отбивай подчёркиванием слова")

    bottomString = ' '.join(env['args']).upper()

    if len(bottomString)>11:
        return await env.reply(f'Максимум 11 символов.')

    imageSize = img.size

    fontSize = int(imageSize[1] / 2 - len(bottomString) / 2 - 10)
    font = ImageFont.truetype(PATH+"Impact.ttf", fontSize)
    bottomTextSize = font.getsize(bottomString)

    bottomTextPositionX = 147
    bottomTextPositionY = 40
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)

    draw = ImageDraw.Draw(img)

    #outlineRange = int(fontSize/25)
    #for x in range(-outlineRange, outlineRange+1):
    #    for y in range(-outlineRange, outlineRange+1):
    #        draw.text((bottomTextPosition[0]+x, bottomTextPosition[1]+y), bottomString, (0,0,0), font=font), bottomTextPosition[1]+y), bottomString, (0,0,0), font=font)

    draw.text(bottomTextPosition, bottomString, (0,0,0), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='png')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    await env.reply('Держи', attachment=result)

