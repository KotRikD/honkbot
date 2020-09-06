from kutana import Plugin
import datetime
from database import *
from utils import edict, ddict, parse_user_id, priviligeshelper

plugin = Plugin(name="Узнать свой id", cmds=[{'command': 'id <user>', 'desc': 'узнать id'}])

fmt = '%d-%m-%Y %H:%M:%S'

async def getuserinformation(env, isd):
    u = await env.request('users.get', user_ids=isd, fields='verified,sex,photo_100,online,site,status,last_seen,followers_count', name_case='abl')
    return u.response[0]

@plugin.on_startswith_text("id")
async def on_message(message, attachments, env):
    if env['args']:
        user = await parse_user_id(message, env, custom_text=env['args'][0])
        if not user:
            return await env.reply("Пользователь не найден!")

        user = await getuserinformation(env, user[0])
    else:
        user = await getuserinformation(env, message.from_id)

    s = ""
    try:
        dt1 = datetime.datetime.fromtimestamp(user['last_seen']['time'])
        dt = dt1.strftime(fmt)

        s += f"Информация о пользователе [id{user['id']}|{user['first_name']}]:\n"
        s += f"- ID пользователя: {user['id']}\n\n"

        privs = await priviligeshelper.getUserPriviliges(env, user['id'])
        if privs&priviligeshelper.USER_ADMIN>0:
            s += f"- Админ бота: ✅\n"
        else:
            s += f"- Админ бота: ⛔\n"

        if privs&priviligeshelper.USER_MODERATOR>0:
            s += f"- Модер у бота: ✅\n"
        else:
            s += f"- Модер у бота: ⛔\n"

        if privs&priviligeshelper.USER_VIP>0:
            s += f"- Вип у бота: ✅\n"
        else:
            s += f"- Вип у бота: ⛔\n"

        ll = await ddict(await env.eenv.dbredis.get(f"honoka:banned_users:{user['id']}"))
        if ll:
            s += f"- В ЧС бота?: ✅\nПо причине: {str(ll['reason'])}\n"
        else:
            s += "- В ЧС бота?: ⛔\n"

        kk = await ddict(await env.eenv.dbredis.get(f"honoka:muted_users:{user['id']}"))
        if kk:
            s += f"- Замучен (временный бан)?: ✅ Замучен до {datetime.datetime.fromtimestamp(kk['time_to']).strftime(fmt)}\nПо причине: {str(kk['reason'])}\n\n"
        else:
            s += "- Замучен (временный бан)?: ⛔\n\n"


        if user['sex'] == 1:
            s += "- Пол: Женский\n"
        else:
            s += "- Пол: Мужской\n"

        if user['online'] == 0:
            s += "- Онлайн? Нет\n"
        else:
            s += "- Онлайн? Да\n"

        if user['last_seen']['platform'] == 1:
            s += "- Откуда вход: Мобильная версия\n"
        elif user['last_seen']['platform'] == 2:
            s += "- Откуда вход: Iphone\n"
        elif user['last_seen']['platform'] == 3:
            s += "- Откуда вход: Ipad\n"
        elif user['last_seen']['platform'] == 4:
            s += "- Откуда вход: Android\n"
        elif user['last_seen']['platform'] == 5:
            s += "- Откуда вход: Windows Phone\n"
        elif user['last_seen']['platform'] == 6:
            s += "- Откуда вход: Windows 10\n"
        elif user['last_seen']['platform'] == 7:
            s += "- Откуда вход: Полная версия\n"

        s += f"- Последний вход: {str(dt)}\n"
        s += f"- Количество подписчиков: {str(user['followers_count'])}\n"

    except Exception as e:
        print(e)
        s += "Такой профиль не был найден"

    return await env.reply(s)