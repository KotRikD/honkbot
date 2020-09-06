from kutana import Plugin
from database import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from utils import priviligeshelper
from utils.static_text import need_vip

import io
import aiohttp

plugin = Plugin(name="Этот пользователь!", cmds=[{'command': 'этот пользователь <текст>', 'desc': 'делает карточку "этот пользователь"', 'vip': True}])

PATH = "plugins/this_user/"
textd = "Этот пользователь "
sizes = (668, 189)  # In-card space sizes
limit = 27  # Limit an symbols in one line
limit_lines = 4  # Limit lines!
fd = ImageFont.truetype(PATH + "font.ttf", 30)
color_font = (242, 174, 127)


def chuncked_text(l, n):
    for i in range(0, len(l), n + 2):
        yield l[i:i + n + 2]


@plugin.on_startswith_text("этот пользователь")
async def on_message(message, attachments, env):
    if not await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
        return await env.reply(need_vip)

    base_img = Image.open(PATH + "this_user.png").covert("RGBA")

    u = await env.request("users.get", user_ids=message.from_id, fields="photo_max")
    img_u_url = u.response[0]['photo_max']

    text = textd+' '.join(env['args'])

    async with aiohttp.ClientSession() as sess:
        async with sess.get(img_u_url) as response:
            avatar = Image.open(io.BytesIO(await response.read()))
            avatar = avatar.resize((188, 188), Image.ANTIALIAS)

    draw = ImageDraw.Draw(base_img)
    if len(text) >= limit:
        new_text = list(chuncked_text(text, limit))
        if len(new_text) > limit_lines:
            return await env.reply("К сожалению не получилось сделать карточку!")
        text = '\n'.join(new_text)
    #            if len(text) > limit_lines:
    #                return await msg.answer("К сожалению не получилось сделать карточку!")

    w, h = draw.textsize(text, font=fd)

    draw.text(((sizes[0] - w) / 2 + 219, (sizes[1] - h) / 2 + 17), text, fill=color_font, font=fd, align="center")
    base_img.paste(avatar, (16, 15))

    f = io.BytesIO()
    base_img.save(f, format='png')
    f.seek(0)
    attachment = await env.upload_photo(f)
    f.close()

    return await env.reply("держи!", attachment=attachment)
