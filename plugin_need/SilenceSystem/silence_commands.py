import time
from database import *
from kutana import Plugin
from utils import edict,ddict,parse_user_id, priviligeshelper
import utils.logs as Logs

plugin = Plugin(name="Мут-система")

@plugin.on_startswith_text("мут")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if (privs & priviligeshelper.USER_MODERATOR > 0) or (privs & priviligeshelper.USER_ADMIN > 0):
        pass
    else:
        return await env.reply("У вас нету прав!")

    if not env['args']:
        return await env.reply("Команда введена не верно")

    if len(env['args'])<3:
        return await env.reply("Недостаточно аргументов")

    if not env['args'][1].isdigit():
        return await env.reply("Некоторые аргументы должны быть числовыми")

    ct = int(time.time())
    ctt = ct+int(int(env['args'][1]))*60

    userc = await parse_user_id(message, env, custom_text=str(env['args'][0]))
    if not userc:
        return await env.reply("Я не могу замутить несуществующего человека")

    oh_you_can = await priviligeshelper.canTouch(privs, userc[0])
    if not oh_you_can:
        return await env.reply("К сожалению, у этого человека больше прав чем у тебя) Мут невозможен!")

    u = await ddict(await env.eenv.dbredis.get(f"honoka:muted_users:{userc[0]}"))
    if u:
        return await env.reply("Пользователь уже замучен")

    u = await env.eenv.dbredis.set(f"honoka:muted_users:{userc[0]}", await edict(dict(time_to=ctt, reason=' '.join(env['args'][1:]))))
    await env.eenv.dbredis.expire(f"honoka:muted_users:{userc[0]}", int(int(env['args'][1]))*60)

    await Logs.create_log(env, message.from_id, userc[0], 6, ' '.join(env['args'][1:]))
    return await env.reply(f"Начался сайленс на {env['args'][1]} минут")

@plugin.on_startswith_text("снять мут")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if (privs & priviligeshelper.USER_MODERATOR > 0) or (privs & priviligeshelper.USER_ADMIN > 0):
        pass
    else:
        return await env.reply("У вас нету прав!")

    if not env['args']:
        return await env.reply("Команда введена не верно!")

    userc = await parse_user_id(message, env, custom_text=str(env['args'][0]))
    if not userc:
        return await env.reply("Я не могу замутить несуществующего человека")

    u = await ddict(await env.eenv.dbredis.get(f"honoka:muted_users:{userc[0]}"))
    if not u:
        return await env.reply("Пользователь не замучен")

    await Logs.create_log(env, message.from_id, userc[0], 7)
    await env.eenv.dbredis.delete([f"honoka:muted_users:{userc[0]}"])
    return await env.reply("Сайленс снят!")
