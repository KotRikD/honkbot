from kutana import Plugin

import io
import aiohttp
import base64
import json
from PIL import Image
import datetime

ACCESS_TOKEN = "<trace.moe token>"


plugin = Plugin(name="Что за аниме?!", cmds=[{'command': 'что за аниме <фотография>', 'desc': 'узнать аниме по фотке.'}])


@plugin.on_startswith_text("что за аниме", "чо за аниме")
async def on_message(message, attachments, env):
    if not any(x.type and x.type == "photo" for x in attachments):
        await env.reply('Вы не прислали фото!\nВведите \
                        что за аниме <прикрепленная фотография>')
        return "DONE"

    photo_url = None
    for a in attachments:
        if a.type == "photo" and a.link:
            photo_url = a.link
            break
        else:
            await env.reply('Произошла какая-то ошибка. Попробуйте другую фотографию.')
            return "DONE"

    image = None
    async with aiohttp.ClientSession() as sess:
        async with sess.get(photo_url) as resp:
            image = Image.open(io.BytesIO(await resp.read()))

    if image is None:
        await env.reply("Ерунда какая-то! Ошибка...")
        return "DONE"

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(f'https://trace.moe/api/search?token={ACCESS_TOKEN}',
                                 data=f'image={base64.b64encode(buffer.getvalue()).decode()}',
                                 headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Host': 'trace.moe'}) as resp:
                finaljsonwithiwork = await resp.json(content_type=None)
                finaljsonwithiwork = finaljsonwithiwork['docs'][0]

        attach = None
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://trace.moe/thumbnail.php?anilist_id={finaljsonwithiwork['anilist_id']}&file={finaljsonwithiwork['filename']}&t={finaljsonwithiwork['at']}&token={finaljsonwithiwork['tokenthumb']}") as resp:
                attach = await env.upload_photo(io.BytesIO(await resp.read()))

        await env.reply(f"Я думаю это аниме: {finaljsonwithiwork['title_english']}/{finaljsonwithiwork['title']}\n"
                         f"Эпизод: {str(finaljsonwithiwork['episode'])} \n"
                         f"Время: {str(datetime.timedelta(seconds=finaljsonwithiwork['from'])).split('.')[0]}\n"
                         f"Шанс попадания: {int(finaljsonwithiwork['similarity'] * 100)}% \n\nКадр:",
                     attachment=attach)
    except Exception as e:
        #print(e)
        await env.reply("Чёт произошло не знаю чё.")

    return "DONE"
