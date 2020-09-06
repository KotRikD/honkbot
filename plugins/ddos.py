from kutana import Plugin
import asyncio
import random
from database import *
from utils import priviligeshelper
import utils.logs as Logs


plugin = Plugin(name="Ддос фан", cmds=[{'command': 'ддос', 'desc': 'админ тебя задудосит', 'cheat': True}])


@plugin.on_startswith_text("ддос")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_ADMIN > 0):
        return await env.reply("Ты не админ")

    if not env['args']:
        return await env.reply("А кого дудосить буим?")

    method = random.choice(["L4", "L7"])

    await env.reply(f"ДДОС начался\nIP жертвы: {' '.join(env['args'])}\nМетод доса: {method}\nСкорость: 1TB\nУдачи поцану!")
    await asyncio.sleep(5)
    await env.reply("Пингуем IP")
    await env.reply("Не пингуется, ддос удался")
    await Logs.create_log(env, message.from_id, 0, 8, 'Выпустил DDoS легушку на человека!')
    return "DONE"