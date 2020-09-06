from kutana import Plugin

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

import io

plugin = Plugin(name="Лебедев", cmds=[
    {'command': 'лебедев <слово>', 'desc': 'Делает картинку аля "Ну бот и бот"'}
])

PATH = "plugins/lebedev/"
sizes = (815, 815)

@plugin.on_startswith_text("лебедев")
async def lebedev(msg, att, env):
    if not env.args:
        return await env.reply("нужен хотя-бы один аргумент(")

    base_img = Image.open(PATH+"base.jpg")
    draw = ImageDraw.Draw(base_img)

    font_size = 60

    args = ' '.join(env.args)
    string = f"Ну {args.lower()} и {args.lower()}"

    font = ImageFont.truetype(PATH+"arial.ttf", font_size)
    w, _ = draw.textsize(string, font=font)

    while w+20 > sizes[0]:
        font_size-=1
        font = ImageFont.truetype(PATH+"arial.ttf", font_size)
        w, _ = draw.textsize(string, font=font)

    draw.text(( (sizes[0]-w)/2 , 690), string, fill=(255,255,255), font=font)

    buffer = io.BytesIO()
    base_img.save(buffer, format='png')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    return await env.reply('держи!', attachment=result)
