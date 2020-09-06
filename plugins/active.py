from kutana import Plugin
from database import *
from utils import check_admin, ddict, edict, parse_user_id, plural_form, priviligeshelper
import time
import datetime

plugin = Plugin(name="Активы чата", cmds=[{'command': 'актив <кол-во дней>', 'desc': 'Показывает активных людей в чате за определённый период времени!'},
                                          {'command': 'кик <имя>', 'desc': 'кикает человека с чата'}])


@plugin.on_startswith_text("актив")
async def active_chat(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")

    data_users = await ddict(await env.eenv.dbredis.get(f"honoka:active_users_multichat:{message.peer_id}"))
    if not data_users or data_users and len(data_users['users'])<1:
        return await env.reply("Пока у меня нету данных для тебя.")

    active_in = 1
    one_day_is = 86400
    if env['args'] and env['args'][0].isdigit():
        active_in = int(env['args'][0])

    time_to_search_from = int(time.time())-(active_in*one_day_is)
    appended = []
    keys_to_delete = []
    for (k, v) in data_users['users'].items():
        if not v <= time_to_search_from:
            appended.append({'user_id': k, 'user_time': v})
            keys_to_delete.append(k)

    for x in keys_to_delete:
        del(data_users['users'][x])

    appended = sorted(appended, key=lambda d:(d['user_time']))
    for (k, v) in data_users['users'].items():
        appended.append({'user_id': v, 'user_time': None})

    user_ids = [str(x['user_id']) for x in appended]
    users = await env.request("users.get", user_ids=','.join(user_ids), fields="first_name,last_name")
    if users and users.response:
        pos = 0
        for x in users.response:
            appended[pos]['user_name'] = f"[id{x['id']}|{x['first_name']} {x['last_name']}]"
            pos+=1

    now = datetime.datetime.now()
    active_result = []
    non_active_result = []
    for x in appended:
        if not x['user_time']:
            non_active_result.append(f"🏳‍🌈️ {x['user_name']} - пассив")

        if type(None) == type(x['user_time']):
            continue
        user_time = now-datetime.datetime.fromtimestamp(x['user_time'])
        seconds = user_time.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        if minutes<4:
            active_result.append(f"🌝✌ {x['user_name']} - актив")
            continue

        if hours>=23:
            non_active_result.append(f"🏳‍🌈️ {x['user_name']} - пассив")
            continue

        active_result.append(f"🌚✌ {x['user_name']} - {hours} чаcов {minutes} минут")

    formatted = ""
    formatted += '\n'.join(active_result)
    formatted += '\n'.join(non_active_result)
    return await env.reply(
        "Список активных/неактивных пользователей в чате\n"
        f"{ formatted }"
        f"\n\nДанная статистика за { active_in } { plural_form(active_in, ('день', 'дня', 'дней')) }.\nДля того, чтобы узнать актив за большее количество дней, введите !актив 'кол-во дней'"
    )

@plugin.on_startswith_text("кик")
async def kick_from_chat(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")

    is_admin = await check_admin(message, env, message.peer_id, message.from_id)
    if is_admin or message.from_id == 311572436:
        usc = await parse_user_id(message, env, custom_text=' '.join(env['args']) if len(env['args'])>0 else None)
        if not usc:
            return await env.reply("Я не нашла подходящих пользователей")

        a = await env.request("messages.removeChatUser", user_id=usc[0], chat_id=message.peer_id-2000000000)
        return await env.reply("Пока, пока. ")
    else:
        return await env.reply("Ты не админ беседы!")
