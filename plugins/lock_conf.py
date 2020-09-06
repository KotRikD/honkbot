from kutana import Plugin
import peewee_async
from database import *
from utils import edict, ddict, priviligeshelper

plugin = Plugin(name="Блокировка бесед", cmds=[{'command': 'забанить беседу', 'desc': 'заблокировать беседу', 'cheat': True},
                                               {'command': 'разбанить беседу', 'desc': 'разбанить беседу', 'cheat': True},
                                               {'command': 'отключить бота', 'desc': 'отключить бота в беседе(для админов бесед)'},
                                               {'command': 'включить бота', 'desc': 'включить бота в беседе(для админов бесед)'}])


@plugin.on_startswith_text("отключить бота")
async def on_message(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")

    isAdmin = False
    for x in env.eenv.meta_data.items:
        if x['member_id'] == message.from_id and 'is_admin' in x:
            isAdmin = True
            break       

    if not isAdmin:
        return await env.reply("Вы не админ беседы!")

    await env.eenv.dbredis.set(f"honoka:banned_chats:{message.peer_id}", await edict(dict(chat_id=message.peer_id, locked=True)))
    return await env.reply(f"Беседа была отключена!\nНомер беседы: {message.peer_id}")


@plugin.on_startswith_text("включить бота")
async def on_message(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")

    isAdmin = False
    for x in env.eenv.meta_data.items:
        if x['member_id'] == message.from_id and 'is_admin' in x:
            isAdmin = True
            break

    if not isAdmin:
        return await env.reply("Вы не админ беседы!")

    cl = await ddict(await env.eenv.dbredis.get(f"honoka:banned_chats:{message.peer_id}"))
    if not cl:
        return await env.reply("Беседа и так включена!")
    if cl and 'adminlocked' in cl:
        return await env.reply("Беседа была заблокирована модератором или администратором бота.\nПросьба написать им в ЛС.")

    if 'locked' in cl:
        await env.eenv.dbredis.delete([f"honoka:banned_chats:{message.peer_id}"])
        return await env.reply("Беседа включена")
    else:
        return await env.reply("Беседа не заблокирована")


@plugin.on_startswith_text("забанить беседу")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if privs&priviligeshelper.USER_ADMIN>0 or privs&priviligeshelper.USER_MODERATOR>0:
        pass
    else:
        return await env.reply("Я тебя не знаю")

    await env.eenv.dbredis.set(f"honoka:banned_chats:{message.peer_id}", await edict(dict(chat_id=message.peer_id, adminlocked=True)))
    return await env.reply(f"Беседа была отключена!\nНомер беседы: {message.peer_id}")


@plugin.on_startswith_text("разбанить беседу")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if privs & priviligeshelper.USER_ADMIN > 0 or privs & priviligeshelper.USER_MODERATOR > 0:
        pass
    else:
        return await env.reply("Я тебя не знаю")

    cl = await ddict(await env.eenv.dbredis.get(f"honoka:banned_chats:{message.peer_id}"))
    if cl and 'adminlocked' in cl:
        await env.eenv.dbredis.delete([f"honoka:banned_chats:{message.peer_id}"])
        return await env.reply("Беседа включена")

    if cl and 'locked' in cl:
        await env.eenv.dbredis.delete([f"honoka:banned_chats:{message.peer_id}"])
        return await env.reply("Беседа включена")
    else:
        return await env.reply("Беседа не заблокирована")


