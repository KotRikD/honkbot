import io
import aiohttp
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from utils import priviligeshelper
from utils.static_text import need_vip
from kutana import Plugin
from database import *

plugin = Plugin(name="Генератор мемов", cmds=[{'command': 'мем <вверхний текст>\n<нижний текст>', 'desc': 'добавляет текст к картинке', 'vip': True}])

fonts = []
sizes = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100, 90, 80, 70, 60, 50, 40, 30, 20]
bg = None

PATH = "plugins/mem_generator/"


with open(PATH+"default.jpg", "rb") as f:
    bg = f.read()

for size in sizes:
    fonts.append(ImageFont.truetype(PATH+"Impact.ttf", size))

@plugin.on_startswith_text("мем")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("Пожалуйста, укажите текст для картинки!")

    if not await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
        return await env.reply(need_vip)

    photo = None

    if attachments:
        for x in attachments:
            if x.type == "photo":
                photo = x

    img = None

    if not photo or not photo.link:
        img = Image.open(io.BytesIO(bg))

    if not img:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(photo.link) as response:
                img = Image.open(io.BytesIO(await response.read()))

    if not img:
        return await env.reply('К сожалению, ваше фото исчезло!')

    strings = env['body'].upper().split("\n")

    if len(strings) < 2:
        return await env.reply("Второй строки нетууу. Создать ничего не могу.")

    if len(strings) < 2:
        strings += [""]

    left_font = 0
    right_font = len(fonts)

    max_h = 0.15
    max_w = 0.9

    fits = False

    while right_font - left_font > 1:
        current_font = (right_font + left_font) // 2

        font = fonts[current_font]

        top_text_size = font.getsize(strings[0])
        bottom_text_size = font.getsize(strings[1])

        if top_text_size[0] >= img.size[0] * max_w or top_text_size[1] >= img.size[1] * max_h \
                or bottom_text_size[0] >= img.size[0] * max_w or bottom_text_size[1] >= img.size[1] * max_h:
            left_font = current_font
        else:
            fits = True

            right_font = current_font

    if fits:
        font = fonts[right_font]
        top_text_size = font.getsize(strings[0])
        bottom_text_size = font.getsize(strings[1])

    else:
        return await env.reply("Ваш текст не влезает! Простите!")

    top_text_position = img.size[0] / 2 - top_text_size[0] / 2, 0
    bottom_text_position = img.size[0] / 2 - bottom_text_size[0] / 2, img.size[1] - bottom_text_size[1] * 1.17

    draw = ImageDraw.Draw(img)

    outline_range = int(top_text_size[1] * 0.12)
    for x in range(-outline_range, outline_range + 1, 2):
        for y in range(-outline_range, outline_range + 1, 2):
            draw.text((top_text_position[0] + x, top_text_position[1] + y), strings[0], (0, 0, 0), font=font)
            draw.text((bottom_text_position[0] + x, bottom_text_position[1] + y), strings[1], (0, 0, 0), font=font)

    draw.text(top_text_position, strings[0], (255, 255, 255), font=font)
    draw.text(bottom_text_position, strings[1], (255, 255, 255), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='png')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    return await env.reply('Результат:', attachment=result)
