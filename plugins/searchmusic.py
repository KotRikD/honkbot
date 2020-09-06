from kutana import Plugin
from database import *
import aiohttp
import json

plugin = Plugin(name="музычка v2", cmds=[{'command': 'музыка найди', 'desc': 'Найти музычку'},
                                         {'command': 'музыка порекомендуй', 'desc': 'Порекомендуем мызчку'}])

async def audio_api(method, **kwargs):
    db_query = await get_or_none(DynamicSettings, key="KATE_TOKEN")
    if not db_query:
        return False

    API_URL = "https://api.vk.com/method/"
    TOKEN = db_query.value
    headers = {
            "Host":"api.vk.com",
            "User-Agent": ("KateMobileAndroid/45 lite-421 (Android 5.0; SDK 21; armeabi-v7a; LENOVO Lenovo A1000; ru)")
    }

    params = {}
    for (k, v) in kwargs.items():
        params[k] = v

    params['access_token'] = TOKEN
    params['v'] = "5.78"

    async with aiohttp.ClientSession() as sess:
        async with sess.get(API_URL + str(method), params=params, headers=headers) as resp:
            response = await resp.read()
            if not response:
                return {}
            return json.loads(response)

@plugin.on_startswith_text("музыка найди")
async def search_music(message, attachments, env):
    if not env['args']:
        return await env.reply("а какую мызыку буим искать?")

    query = ' '.join(env['args'])

    result = await audio_api('audio.search',  q=query)
    if not result or not 'response' in result or not 'items' in result['response']:
        return await env.reply("К сожалению, музыка сдохла или вы дорогой пользователь криво написали запрос.")

    music = []
    for m in result['response']['items']:
        music.append(f"audio{m['owner_id']}_{m['id']}")
    print(music)
    return await env.reply("держи", attachment=','.join(music))

@plugin.on_startswith_text("музыка порекомендуй")
async def recommend_music(message, attachments, env):
    result = await audio_api("audio.getRecommendations", user_id=message.from_id, shuffle=1)
    if not result or not 'response' in result or not 'items' in result['response']:
        return await env.reply("К сожалению, музыка сдохла или у вас закрыта библиотека с музыкой.")

    music = []
    for m in result['response']['items']:
        music.append(f"audio{m['owner_id']}_{m['id']}")

    return await env.reply("держи", attachment=','.join(music))
