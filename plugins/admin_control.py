from kutana import Plugin
from database import *
from utils import edict, parse_user_id, priviligeshelper
import utils.logs as Logs
import peewee_async

plugin = Plugin(name="Админ-система")

async def ban(dbredis, user_id, reason):
    t = await dbredis.set(f"honoka:banned_users:{user_id}", await edict({'banned': True, 'reason': reason}))
    us1 = await get_or_none(Priviliges, user_id=user_id)
    if us1:
        us1.priv = 0
        await manager.update(us1)
    return t

async def unban(dbredis, user_id):
    us1 = await get_or_none(Priviliges, user_id=user_id)
    if us1:
        us1.priv = 2
        await manager.update(us1)
    return await dbredis.delete([f"honoka:banned_users:{user_id}"])

async def add_to_list(msg, env, args, role):
    if not args:
        await env.reply("Вы не указали ID пользователя!")
        return "DONE"

    if len(args)<2:
        await env.reply("Укажи причину пожалуйста ;3")
        return "DONE"

    in_text = await parse_user_id(msg, env, custom_text=args[0])
    if not in_text:
        return await env.reply("Такого пользователя не найдено")

    can_touch = await priviligeshelper.canTouch(await priviligeshelper.getUserPriviliges(env, msg.from_id), int(in_text[0]))
    if not can_touch:
        return await env.reply("Вы не можете изменять права этого пользователя!")

    if role == priviligeshelper.USER_BANNED:
        await ban(env.eenv.dbredis, in_text[0], ' '.join(args[1:]))
    else:
        previous_user = await get_or_none(Priviliges, user_id=in_text[0])
        if not previous_user:
            new_user = priviligeshelper.addPrivilige(priviligeshelper.USER_NORMAL, role)
            await manager.create_or_get(Priviliges, user_id=in_text[0], priv=new_user, last_update_reason=' '.join(args[1:]))
        else:
            new_privs = priviligeshelper.addPrivilige(previous_user.priv, role)
            previous_user.priv = new_privs
            await manager.update(previous_user)

    await Logs.create_log(env, msg.from_id, in_text[0], 0, f"группа: {priviligeshelper.strpriv(role)}\nПо причине: {' '.join(args[1:])}")

    await env.reply("Готово!")
    return "DONE"

async def remove_from_list(msg, env, args, role):
    if not args:
        await env.reply("Вы не указали ID пользователя!")
        return "DONE"

    in_text = await parse_user_id(msg, env, custom_text=args[0])

    if not in_text:
        return await msg.answer("Такого пользователя не найдено")

    can_touch = await priviligeshelper.canTouch(await priviligeshelper.getUserPriviliges(env, msg.from_id), int(in_text[0]))
    if not can_touch:
        return await env.reply("Вы не можете изменять права этого пользователя!")

    if role == priviligeshelper.USER_BANNED:
        await unban(env.eenv.dbredis, in_text[0])
    else:
        previous_user = await get_or_none(Priviliges, user_id=in_text[0])
        if not previous_user:
            return "DONE"
        else:
            new_privs = priviligeshelper.removePrivilige(previous_user.priv, role)
            previous_user.priv = new_privs
            await manager.update(previous_user)

    await Logs.create_log(env, msg.from_id, in_text[0], 1, f"группа: {role}")
    await env.reply("Готово!")
    return "DONE"

@plugin.on_startswith_text("выключить")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN>0:
        await Logs.create_log(env, message.from_id, 0, 9, "Перезагрузил зачем-то бота, мб, я не знаю!")
        await env.reply('Выключаюсь, мой господин...')
        exit()
    else:
        await env.reply('Я бы с радостью, но вы не мой администратор :)')
        return "DONE"


@plugin.on_startswith_text("добавить в чс")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if privs&priviligeshelper.USER_ADMIN>0 or privs&priviligeshelper.USER_MODERATOR>0:
        await add_to_list(message, env, env['args'], priviligeshelper.USER_BANNED)
        return "DONE"

@plugin.on_startswith_text("добавить в адм")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN<=0:
        return "DONE"
    return await add_to_list(message, env, env['args'], priviligeshelper.USER_ADMIN)

@plugin.on_startswith_text("добавить в випы")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN<=0:
        return "DONE"
    return await add_to_list(message, env, env['args'], priviligeshelper.USER_VIP)

@plugin.on_startswith_text("убрать из випов")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN<=0:
        return
    return await remove_from_list(message, env, env['args'], priviligeshelper.USER_VIP)

@plugin.on_startswith_text("добавить в модеры")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN<=0:
        return "DONE"
    return await add_to_list(message, env, env['args'], priviligeshelper.USER_MODERATOR)

@plugin.on_startswith_text("убрать из модеров")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN<=0:
        return "DONE"
    return await remove_from_list(message, env, env['args'], priviligeshelper.USER_MODERATOR)

@plugin.on_startswith_text("убрать из чс")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if privs & priviligeshelper.USER_ADMIN > 0 or privs & priviligeshelper.USER_MODERATOR > 0:
        return await remove_from_list(message, env, env['args'], priviligeshelper.USER_BANNED)

@plugin.on_startswith_text("убрать из адм")
async def on_message(message, attachments, env):
    if await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN<=0:
        return "DONE"

    return await remove_from_list(message, env, env['args'], priviligeshelper.USER_ADMIN)

@plugin.on_startswith_text("чёрный список", "админы", "модеры", "випы")
async def on_message(message, attachments, env):
    return await env.reply("Проверяй на моём сайте.")

@plugin.on_startswith_text("logs on")
async def on_enable_logging(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not privs&priviligeshelper.USER_MODERATOR>0:
        return await env.reply("А ти кто такой то?!")
    
    is_logged = await get_or_none(Log, type='NOTIFY_ME', from_id=message.from_id)
    if is_logged:
        return await env.reply("Вы уже подключены на оповещения бота!")
    
    await manager.get_or_create(Log, type='NOTIFY_ME', from_id=message.from_id, to_id=0, body="logs on!")
    return await env.reply("Вы включили логи бота, готовьтесь к аду ;D")

@plugin.on_startswith_text("logs off")
async def disable_logging(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not privs&priviligeshelper.USER_MODERATOR>0:
        return await env.reply("А ти кто такой то?!")
    
    is_logged = await get_or_none(Log, type='NOTIFY_ME', from_id=message.from_id)
    if not is_logged:
        return await env.reply("Вы не подключали уведомления")
    
    await peewee_async.delete_object(is_logged)
    return await env.reply("Вы выключили уведомления от бота! Спите спокойно!")