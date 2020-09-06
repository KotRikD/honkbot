from kutana import Plugin
import re
import asyncio
from database import *
import random
from utils import parse_user_id, VKKeyboard, get_nekos_attach

plugin = Plugin(name="Отношения", cmds=[{'command': 'отношения встречаться <id>', 'desc': 'начать встречаться с <id>'},
                                        {'command': 'отношения поцеловать', 'desc': 'поцеловать свою девушку/парня'},
                                        {'command': 'отношения обнять', 'desc': 'обнять свою девушку/парня'},
                                        {'command': 'отношения погладить', 'desc': 'погладить свою девушку/парня'},
                                        {'command': 'отношения порвать', 'desc': 'порвать с отношениями'},
                                        {'command': 'отношения заняться сексом', 'desc': 'ну тут я думаю вы всё поняли ;D'},
                                        {'command': 'отношения шлёпнуть', 'desc': 'шлёпнуть своего партнёра по попе ;D'},
                                        {'command': 'отношения инфа', 'desc': 'информация об отношениях'}])

relationtemp = {}

@plugin.on_startswith_text("отношения поцеловать")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))
    if not idl:
        return await env.reply("Отношения: У тебя парня/девушки нет.")

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '💖 поцеловать ещё раз', 'payload': {'command': f'{env.eenv.prefix}отношения поцеловать'}, 'color': 'positive'}
        ]
    })

    userinfo = await env.request('users.get', user_ids=f'{idl.user1}, {idl.user2}', fields="sex")
    userinfo = userinfo.response
    suptext = 'поцеловал свою тян' if userinfo[0]['sex'] == 2 else 'поцеловала своего куна'
    await env.reply(f"[id{userinfo[0]['id']}|{userinfo[0]['first_name']} {userinfo[0]['last_name']}] { suptext } [id{userinfo[1]['id']}|{userinfo[1]['first_name']} {userinfo[1]['last_name']}]", 
                    keyboard=kb.dump_keyboard(),
                    attachment=await get_nekos_attach(env, "kiss"))

@plugin.on_startswith_text("отношения обнять")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))
    if not idl:
        return await env.reply("Отношения: У тебя парня/девушки нет.")

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '💑 обнять ещё раз', 'payload': {'command': f'{env.eenv.prefix}отношения обнять'}, 'color': 'positive'}
        ]
    })
    userinfo = await env.request('users.get', user_ids=f'{idl.user1}, {idl.user2}', fields="sex")
    userinfo = userinfo.response
    suptext = 'обнял свою тян' if userinfo[0]['sex'] == 2 else 'обняла своего куна'
    await env.reply(f"[id{userinfo[0]['id']}|{userinfo[0]['first_name']} {userinfo[0]['last_name']}] { suptext } [id{userinfo[1]['id']}|{userinfo[1]['first_name']} {userinfo[1]['last_name']}]", 
                    keyboard=kb.dump_keyboard(),
                    attachment=await get_nekos_attach(env, random.choice(['hug', 'cuddle'])))


@plugin.on_startswith_text("отношения погладить")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))
    if not idl:
        return await env.reply("Отношения: У тебя парня/девушки нет.")

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '💑 погладить ещё раз', 'payload': {'command': f'{env.eenv.prefix}отношения погладить'}, 'color': 'positive'}
        ]
    })
    userinfo = await env.request('users.get', user_ids=f'{idl.user1}, {idl.user2}', fields="sex")
    userinfo = userinfo.response
    suptext = 'погладил свою тян' if userinfo[0]['sex'] == 2 else 'погладила своего куна'
    await env.reply(f"[id{userinfo[0]['id']}|{userinfo[0]['first_name']} {userinfo[0]['last_name']}] { suptext } [id{userinfo[1]['id']}|{userinfo[1]['first_name']} {userinfo[1]['last_name']}]", 
                    keyboard=kb.dump_keyboard(),
                    attachment=await get_nekos_attach(env, 'pat'))


@plugin.on_startswith_text("отношения шлёпнуть")
async def slap(msg, att, env):
    idl = await get_or_none(Relations, user1=int(msg.from_id))
    if not idl:
        return await env.reply("Отношения: У тебя парня/девушки нет.")

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '💟 шлёпнуть ещё раз', 'payload': {'command': f'{env.eenv.prefix}отношения шлёпнуть'}, 'color': 'positive'}
        ]
    })

    userinfo = await env.request('users.get', user_ids=f'{idl.user1}, {idl.user2}', fields="sex")
    userinfo = userinfo.response
    suptext = 'шлёпнул свою тян по попе' if userinfo[0]['sex'] == 2 else 'шлёпнула по попе своего куна'
    await env.reply(f"[id{userinfo[0]['id']}|{userinfo[0]['first_name']} {userinfo[0]['last_name']}] { suptext } [id{userinfo[1]['id']}|{userinfo[1]['first_name']} {userinfo[1]['last_name']}]\n😜😜😜👋👋 &#128075;&#127825;", 
                    keyboard=kb.dump_keyboard(),
                    attachment=await get_nekos_attach(env, 'slap'))

@plugin.on_startswith_text("отношения заняться сексом")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))
    if not idl:
        return await env.reply("Отношения: У тебя парня/девушки нет.")

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '💟 заняться сексом ещё раз', 'payload': {'command': f'{env.eenv.prefix}отношения заняться сексом'}, 'color': 'positive'}
        ]
    })
    userinfo = await env.request('users.get', user_ids=f'{idl.user1}, {idl.user2}', fields="sex")
    userinfo = userinfo.response
    suptext = 'занялся сексом со своею тянкой' if userinfo[0]['sex'] == 2 else 'занялась сексом с своим куном'
    await env.reply(f"[id{userinfo[0]['id']}|{userinfo[0]['first_name']} {userinfo[0]['last_name']}] { suptext } [id{userinfo[1]['id']}|{userinfo[1]['first_name']} {userinfo[1]['last_name']}]\n😜😜😜👉👌💦💦💦", 
                    keyboard=kb.dump_keyboard(),
                    attachment=await get_nekos_attach(env, random.choice(['classic', 'boobs'])))

@plugin.on_startswith_text("отношения встречаться")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))

    if not env['args']:
        return await env.reply("Отношения: С кем встречаться та буишь?")

    usera = idl
    if not usera:
        usc = await parse_user_id(message, env)
        if usc:
            if await get_or_none(Relations, user1=usc[0]):
                return await env.reply("Отношения: Он/Она уже с кем-то.")

            sex = await env.request('users.get', user_ids=f'{usc[0]},{message.from_id}', fields='sex')
            sex = sex.response
            if usc[0] == message.from_id:
                return await env.reply("Отношения: А, как с самим собой встречаться чёт я хз.")

            kb = VKKeyboard()
            kb.set_inline(True)
            kb.add_row()
            kb.edit_row(0).add_button("💝 Согласиться", payload={'command': f"{env.eenv.prefix}отношения принять"}, color="positive")
            kb.add_row()
            kb.edit_row(1).add_button("💘 Отказать", payload={'command': f"{env.eenv.prefix}отношения отказать"}, color="negative")

            r = await env.request('messages.send', keyboard=kb.dump_keyboard(), user_id=usc[0], message=f"Отношения: [id{usc[0]}|{sex[0]['first_name']}], тебе предложил(-а) встречаться [id{message.from_id}|{sex[1]['first_name']} {sex[1]['last_name']}]\nНапишите команду '!отношения принять' или '!отношения отказать', у вас 120 секунд")
            if not r.error:
                await env.reply("Отношения: Ну я написал ждёмс 120 секунд")
            else:
                return await env.reply("Отношения: Личка не доступна\nЧеловек с которым вы хотите встречаться должен написать боту в лс vk.me/honkbot")

            relationtemp[f'{str(usc[0])}'] = message.from_id
            await asyncio.sleep(120)
            if str(usc[0]) in relationtemp:
                await env.reply("Отношения: К сожалению прошло 120 секунд, а ответа не поступило.")
                await env.request('messages.send', user_id=env['args'], message=f"Отношения: Отмена.....")

                del(relationtemp[f'{str(usc[0])}'])
        else:
            return await env.reply("Отношения: Вы должны были написать упоминание о человеке.")
    else:
        return await env.reply("Отношения: А изменять не очень хорошо, я слышала.")

@plugin.on_startswith_text("отношения порвать")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))
    if not idl:
        return await env.reply("Отношения: У тебя парня/девушки нет как я буду проверять.")

    await env.reply("Отношения: Надеюсь, ты принял нужноё решение, удаление из бд....")

    userlovedestroy = idl.user2
    await manager.execute(Relations.delete().where(Relations.user1 == int(message.from_id)))
    await manager.execute(Relations.delete().where(Relations.user2 == int(message.from_id)))
    await env.request('messages.send', user_id=userlovedestroy, message='Отношения: Уведомляю вас о том, что ваша тян/кун окончила отношения.')
    return await env.reply("Отношения: Вся информация о вас была стёрта.")


@plugin.on_startswith_text("отношения")
async def on_message(message, attachments, env):
    idl = await get_or_none(Relations, user1=int(message.from_id))
    if not env['args']:
        await env.reply(f"Аргументы:\n"
                                f"отношения принять - принять предложение.\n"
                                f"отношения отказать - отказаться от предложения.\n"
                                f"отношения инфа - инфа об твоих отношениях")
        return "GOON"

    if env['args'][0].lower() == "инфа":
        if not idl:
            return await env.reply("Отношения: У тебя парня/девушки нет.")

        relays = idl
        info = await env.request('users.get', user_ids=relays.user2, fields='sex')
        info = info.response

        user1, user2 = await get_or_none(PxUser, iduser=message.from_id), await get_or_none(PxUser, iduser=relays.user2)
        if not user1:
            return env.reply("[Отношения] пожалуйста введите !rank для просмотра этой команды!")
        if not user2:
            return env.reply("[Отношения] пожалуйста попросите своего партнёра прописать !rank, чтобы взглянуть на статистику отношений")

        kb = VKKeyboard()
        kb.set_inline(True)
        if not env.eenv.is_multichat:
            kb.add_row()
            kb.edit_row(0).add_button("Порвать отношения", payload={'command': f"{env.eenv.prefix}отношения порвать"}, color="negative")

        xpuser1 = user1.xpcount
        xpuser2 = user2.xpcount
        allcount = int(xpuser1) + int(xpuser2)

        mxpuser1 = user1.messcount
        mxpuser2 = user2.messcount
        mess = int(mxpuser1) + int(mxpuser2)

        strdt = datetime.datetime.fromtimestamp(relays.datetime).strftime('%Y-%m-%d %H:%M:%S')

        if info[0]['sex'] == 1:
            return await env.reply(f"💞Твоя тян: [id{info[0]['id']}|{info[0]['first_name']} {info[0]['last_name']}]\n"
                                    f"💡Ваш общий опыт: {allcount}xp\n"
                                    f"📮Ваше общее количество сообщений: {mess}\n"
                                    f"📅Когда были зарегестрированы: {strdt}", keyboard=kb.dump_keyboard())
        elif info[0]['sex'] == 2:
            return await env.reply(f"💞Твой кун: [id{info[0]['id']}|{info[0]['first_name']} {info[0]['last_name']}]\n"
                                    f"💡Ваш общий опыт: {allcount}xp\n"
                                    f"📮Ваше общее количество сообщений: {mess}\n"
                                    f"📅Когда были зарегестрированы: {strdt}", keyboard=kb.dump_keyboard())

    if str(message.from_id) in relationtemp:
        if env['args'][0].lower() == "принять":
            await env.request('messages.send', user_id=relationtemp[f'{str(message.from_id)}'], message=f"Отношения: [id{relationtemp[f'{str(message.from_id)}']}|Поздравляем], твоё предложение приняли.")
            await env.reply("Отношения: Поздравляем, теперь вы пара.")
            user_1 = relationtemp[f'{str(message.from_id)}']
            user_2 = message.from_id
            timestamp = int(datetime.datetime.now().timestamp())

            await peewee_async.create_object(Relations, user1=user_1, user2=user_2, datetime=timestamp)
            await peewee_async.create_object(Relations, user1=user_2, user2=user_1, datetime=timestamp)
            del(relationtemp[f'{str(message.from_id)}'])
        elif env['args'][0].lower() == "отказать":
            await env.reply("Отношения: Спасибо, что написали, пойду сообщу эту грустную новость тому человеку, чьи чувства были разбиты.")
            await env.request('messages.send', user_id=relationtemp[f'{str(message.from_id)}'], message=f"Отношения: [id{relationtemp[f'{str(message.from_id)}']}|К сожалению], тебе отказали.")
            del(relationtemp[f'{str(message.from_id)}'])
    else:
        pass

    return "DONE"


