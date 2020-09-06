from kutana import Plugin, VKController
from database import *
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Поиск видео", cmds=[{'command': "видео", 'desc': 'поиск видео', 'vip': True}])

@plugin.on_startswith_text("видео")
async def video(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_VIP > 0):
        return await env.reply(need_vip)

    if not env['args']:
        return await env.reply('Какое видео вас интересует?')

    query = ' '.join(env['args'])
    async with VKController("0688302a8de51d784afafd73c761069978850c88f6c54ffbf28acd5aed42dd8f81fb59aa0e7d28b7f3f52") as user_api:
        data = await user_api.raw_request('video.search', q=query, sort=2, adult=1, count=5)
        resp = data.response

    vids = resp.get('items')
    # Если не нашли ни одного видео
    if not vids:
        return await env.reply('Ничего не найдено')
    resp = ','.join(f"video{vid['owner_id']}_{vid['id']}" for vid in vids)
    return await env.reply('Приятного просмотра!', attachment=resp)