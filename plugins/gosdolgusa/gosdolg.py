from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from kutana import Plugin
from utils import DebtCalc

import io

plugin = Plugin(name="Узнать внешний долг США",
                cmds=[{'command': 'госдолг США', 'desc': 'узнать внешний долг США на сегодняшний день'}])

PATH = "plugins/gosdolgusa/"

font = ImageFont.truetype(PATH + "font.ttf", 82)
color = (219, 41, 37)

sizes = (673, 79)
paddings = (173, 248)


def humanize(value):
    return "{:,}".format(round(value))


@plugin.on_startswith_text("госдолг США", "госдолг")
async def gosdolgusa(message, attachs, env):
    base_img = Image.open(PATH + "mem.png").convert("RGBA")

    draw = ImageDraw.Draw(base_img)

    count = "$" + humanize(int(DebtCalc().debt))

    w, h = draw.textsize(count, font=font)

    draw.text(((sizes[0] - w) / 2 + paddings[0], (sizes[1] - h) / 2 + paddings[1]), count, fill=color, font=font,
              align="center")

    buffer = io.BytesIO()
    base_img.save(buffer, format='PNG')
    buffer.seek(0)

    result = await env.upload_photo(buffer)

    return await env.reply("На сегодняшний день, долг составляет:", attachment=result)
