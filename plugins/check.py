from kutana import Plugin
from kutana.controller_vk import VKController
import random
from utils import priviligeshelper
from utils import static_text, parse_user_id

plugin = Plugin(name="Чекни",
                cmds=[{'command': 'чекни', 'desc': 'чекает ваши говно-паблики'},
                      {'command': 'чекни <id>', 'desc': 'чекает говно-паблики пользователя', 'vip': True}])

tokens = ["token array"]

bad_groups = '''музыка
кино
мания
igm
mdk
ёп
лепра
борщ
корпорация
лайфхак
юмор
наука
факты
приколы
кулинари
чёткие
лайфхак
рэп
подслушано
юмор
auto
авто
бот
мысли
цитаты
анекдот
идей
улыбнуло
позитив
футбол
football
сервер
minecraft
майнкрафт
япония
tumblr
аниме
anime
сейю
лаунчер
давно не дети
непаблик
фотошоп
пздц
aliexpress
гифки
gif
видео
лоли
loli
кун
kun
vkcoin
-coin
coin'''.splitlines()

@plugin.on_startswith_text("чекни")
async def check(message, attachments, env):
    user_id = message.from_id
    if env['args']:
        if not await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
            return await env.reply(static_text.need_vip)

        user_id = await parse_user_id(message, env, custom_text=env['args'][0])
        if not user_id:
            return await env.reply("Мы не можем получить данного пользователя")

        user_id = user_id[0]

    async with VKController(random.choice(tokens)) as user_api:
        datad = await user_api.raw_request('groups.get', user_id=user_id, extended=1)
        list_groups = datad.response

    if datad.error:
        return await env.reply("не могу выполнить! Попробуйте позже")

    bad_groups_ids = []
    res = False
    for x in list_groups['items']:
        for d in bad_groups:
            if x['name'].lower().find(d) != -1:
                res = True

        if res == True:
            bad_groups_ids.append(f"{x['name']}")
            res = False

    if len(bad_groups_ids) < 1:
        koficient = 0.00
    else:
        kof1 = int(list_groups['count']) / len(bad_groups_ids)
        koficient = 100 / kof1

    result = ""
    if koficient < 5.00:
        result += ";3 Девственно чист\n"
    else:
        result += "🚮Биомусор\n"

    result += f"👉Коэфициент мусора: ~{int(koficient)}% ({len(bad_groups_ids)}/{int(list_groups['count'])})"
    result += f"\n\n💩 Воняет от:\n"

    for x in bad_groups_ids:
        result += f"{x}\n"

    return await env.reply(result)