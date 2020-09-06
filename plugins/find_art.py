from lxml import html
import random
import aiohttp
from kutana import Plugin
from database import *
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Поиск артов", cmds=[{'command': 'арт <Имя персонажа на английском>', 'desc': 'найти арты с персонажем', 'vip': True}])

async def upload_images(env, imglist):
    result = []
    for x in imglist:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(x) as resp:
                attach = await env.upload_photo(await resp.read())
                attach = f"photo{attach.owner_id}_{attach.id}"
                result.append(attach)

    return result

@plugin.on_startswith_text("арт")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_VIP > 0):
        return await env.reply(need_vip)

    if not env['args']:
        return await env.reply("Нету имени персонажа")

    name = '+'.join(env['args'])

    rand_count = random.randint(1, 5)

    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"http://anime.reactor.cc/search/{name}/{rand_count}",
                             headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}) as resp:
            fs_paged_res = html.fromstring(await resp.text())

    images = fs_paged_res.cssselect('div.image>a>img')

    if not images:
        return await env.reply("Арты не были найдены")

    images_list = []
    for x in images:
        images_list.append(x.attrib["src"])

    result = await upload_images(env, images_list[:5])
    await env.reply("Держи", attachment=','.join(result))
