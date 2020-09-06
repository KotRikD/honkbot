from kutana import Plugin
import os
import sys
import random
from utils import get_nekos_attach
from PIL import Image
import io

plugin = Plugin(name="Чёрно-белые фоточки", cmds=[{'command': 'kiss <текст>', 'desc': 'поцеловать кого-то'},
                                                  {'command': 'hug <текст>', 'desc': 'обнять кого-то'},
                                                  {'command': 'tickle <текст>', 'desc': 'пощекатать кого-то'},
                                                  {'command': 'кусь <текст>', 'desc': 'укусить кого-то'}])

PATH = "plugins/kisshug/"

@plugin.on_startswith_text("kiss")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("Кого целовать?")

    u = await env.request('users.get', user_ids=message.from_id, fields='sex', name_case='Nom')
    result = await get_nekos_attach(env, "kiss")

    #Temp = [id{u['id']}|{u['first_name']}]
    if u.response[0]['sex'] == 1:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] поцеловала {' '.join(env['args'])}", attachment=result)
    if u.response[0]['sex'] == 2:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] поцеловал {' '.join(env['args'])}", attachment=result)

@plugin.on_startswith_text("hug")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("Кого обнимать?")

    u = await env.request('users.get', user_ids=message.from_id, fields='sex', name_case='Nom')
    result = await get_nekos_attach(env, random.choice(["cuddle", "hug"]))

    #Temp = [id{u['id']}|{u['first_name']}]
    if u.response[0]['sex'] == 1:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] обняла {' '.join(env['args'])}", attachment=result)
    if u.response[0]['sex'] == 2:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] обнял {' '.join(env['args'])}", attachment=result)

@plugin.on_startswith_text("tickle")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("Кого обнимать?")

    u = await env.request('users.get', user_ids=message.from_id, fields='sex', name_case='Nom')
    result = await get_nekos_attach(env, "tickle")

    #Temp = [id{u['id']}|{u['first_name']}]
    if u.response[0]['sex'] == 1:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] пощекотала {' '.join(env['args'])}", attachment=result)
    if u.response[0]['sex'] == 2:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] пощекотал {' '.join(env['args'])}", attachment=result)

@plugin.on_startswith_text("кусь")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("Кого кусать?")

    kusimgs = os.listdir(PATH+"kusimgs")
    nameimg = random.choice(kusimgs)

    img = Image.open(f'{PATH+"kusimgs"}/{nameimg}')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    u = await env.request('users.get', user_ids=message.from_id, fields='sex', name_case='Nom')
    result = await env.upload_photo(buffer)

    #Temp = [id{u['id']}|{u['first_name']}]
    if u.response[0]['sex'] == 1:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] укусила {' '.join(env['args'])}", attachment=result)
    if u.response[0]['sex'] == 2:
        await env.reply(f"[id{u.response[0]['id']}|{u.response[0]['first_name']}] укусил {' '.join(env['args'])}", attachment=result)