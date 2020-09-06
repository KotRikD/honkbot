from kutana import Plugin
from utils import priviligeshelper, VKKeyboard, get_nekos_attach
import aiohttp
import io
import json

plugin = Plugin(name="Nekos life", cmds=[{'command': 'nekos [аргумент]', 'desc': 'рандом пикчи с nekolife', 'vip': True}])

types = ['feet', 'yuri', 'trap', 'futanari', 'hololewd', 'lewdkemo',
         'solog', 'feetg', 'cum', 'erokemo', 'wallpaper', 'lewdk',
         'ngif', 'meow', 'tickle', 'lewd', 'feed', 'gecg', 'eroyuri', 'eron',
         'cum_jpg', 'bj', 'nsfw_neko_gif', 'solo', 'kemonomimi', 'nsfw_avatar',
         'gasm', 'poke', 'anal', 'slap', 'hentai', 'avatar', 'erofeet', 'holo',
         'keta', 'blowjob', 'pussy', 'tits', 'holoero', 'lizard', 'pussy_jpg',
         'pwankg', 'classic', 'kuni', 'waifu', 'pat', '8ball', 'kiss', 'femdom',
         'neko', 'spank', 'cuddle', 'erok', 'fox_girl', 'boobs', 'random_hentai_gif',
         'smallboobs', 'hug', 'ero']


@plugin.on_startswith_text("nekos")
async def nekos(msg, attach, env):
    if not await priviligeshelper.getUserPriviliges(env, msg.from_id) & priviligeshelper.USER_VIP > 0:
        return await env.reply("стоять! Вам нужен вип-статус, чтобы выполнять эту команду!")

    if not env.args or env.args[0] not in types:
        formatted = ', '.join(types)
        return await env.reply(f'Доступные аругменты:\n\n{formatted}')

    attach = await get_nekos_attach(env, env.args[0])
    if not attach:
        return await env.reply("Пикча потерялась не сервере, попробуй позже!")

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': 'Ещё такую пикчу', 'payload': {'command': f'{env.eenv.prefix}nekos {env.args[0]}'}, 'color': 'primary'}
        ]
    })

    return await env.reply("Держи", attachment=attach, keyboard=kb.dump_keyboard())


