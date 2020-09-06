from kutana import Plugin
import datetime
import random
import re
import time
from datetime import timedelta
from database import * 
import asyncio
from utils import priviligeshelper, schedule_task, parse_user_id, parse_user_name, VKKeyboard
import utils.logs as Logs

import aiohttp

plugin = Plugin(name="Economy-v5", cmds=[
    {'command': 'эко отнять', 'desc': 'отнять немного денжат у пользователя', 'cheat': True},
    {'command': 'эко удалить', 'desc': 'очистить профиль пользователя', 'cheat': True},
    {'command': 'профиль (ID)', 'desc': 'просмотр данных себя или пользователя'},
    {'command': 'эко баланс', 'desc': 'отображение вашего баланса'}, 
    {'command': 'эко банк {баланс/вложить/снять} {сумма}', 'desc': 'проверить/снятие/пополнение денег банковского счета'}, 
    {'command': 'эко рейтинг', 'desc': 'отображение вашего рейтинга'}, 
    {'command': 'эко магазин', 'desc': 'каталог товаров'}, 
    {'command': 'эко продать {предмет} (кол-во)', 'desc': 'продажа имущества'}, 
#    {'command': 'эко ферма', 'desc': 'статистика биткоин-фермы'}, 
#    {'command': 'эко ферма снять {сумма}', 'desc': 'снятие денег с биткоин-фермы'}, 
    {'command': 'эко передать {ID} {сумма}', 'desc': 'перевод денег между игроками'}, 
    {'command': 'эко топ', 'desc': 'топ-10 игроков по стоимости профиля'},
    {'command': 'эко биткоин (кол-во)', 'desc': 'приобретение BITCOIN-валюты'}, 
    {'command': 'эко работа', 'desc': 'список работ'}, 
    {'command': 'эко работать', 'desc': 'начинаем работать работяги'}, 
    {'command': 'эко уволиться', 'desc': 'покинуть работу'}, 
    {'command': 'эко бизнес', 'desc': 'статистика бизнеса'}, 
    {'command': 'эко бизнес нанять {1-2} {кол-во}', 'desc':'найм рабочих в бизнес'}, 
    {'command': 'эко бизнес снять {1-2} {кол-во}', 'desc': 'снятие денег со счета бизнеса'}, 
    {'command': 'эко бизнес улучшить {1-2}', 'desc': 'улучшение бизнеса'}, 
    {'command': 'эко копать {алмазы/железо/золото}', 'desc': 'добыча руд'}
])

@plugin.on_startup()
async def on_startup(kutana, update):
    plugin.dict = {}
    plugin.bitcoin = 0
    plugin.positive = random.choice(["😊", "😉", "😃", "😋", "😏", "😄"])
    plugin.negative = random.choice(["😩", "😰", "😒", "😔", "😢"])
    plugin.user_jobs = {}
    plugin.is_active = {}
    plugin.jobs_user = {}
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://blockchain.info/ru/ticker") as resp:
            res = await resp.json()
            data = res["USD"]["sell"]
            plugin.bitcoin = toFixed(data)
            plugin.full_bitcoin = data

    schedule_task(get_btc)
    return "GOON"

async def get_btc(*args, **kwargs):
    while True:
        async with aiohttp.ClientSession() as sess:
            async with sess.get("https://blockchain.info/ru/ticker") as resp:
                res = await resp.json()
                data = res["USD"]["sell"]
                plugin.bitcoin = toFixed(data)
                plugin.full_bitcoin = data

        await asyncio.sleep(900) 


def toFixed(f: float, n=0):
    a, b = str(f).split(".")
    return "{}{}{}".format(a, b[:n], "0" * (n - len(b)))


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return hours, minutes, seconds


cases = (2, 0, 1, 1, 1, 2)


def plural_form(n: int, v: (list, tuple), need_n=False, need_cases=False):
    """Функция возвращает число и просклонённое слово после него

    Аргументы:
    :param n: число
    :param v: варианты слова в формате (для 1, для 2, для 5)

    Пример:
    plural_form(difference.days, ("день", "дня", "дней"))

    :return: Число и просклонённое слово после него
    """

    return f"{n if need_n is False else ''}  {v[2 if (4 < n % 100 < 20) else cases[min(n % 10, 5)]] if need_cases is False else ''}"


def digits_recursive(nonneg):
    digits = []
    while nonneg:
        digits += [nonneg % 10]
        nonneg //= 10
    return digits[::-1] or [0]


def num_to_smile(num):
    if num <= 10:
        numbers = {
            0: "0⃣",
            1: "1⃣",
            2: "2⃣",
            3: "3⃣",
            4: "4⃣",
            5: "5⃣",
            6: "6⃣",
            7: "7⃣",
            8: "8⃣",
            9: "9⃣",
            10: "🔟",
        }
        return numbers[num]
    numbers = {
        0: "0⃣.",
        1: "1⃣",
        2: "2⃣",
        3: "3⃣",
        4: "4⃣",
        5: "5⃣",
        6: "6⃣",
        7: "7⃣",
        8: "8⃣",
        9: "9⃣",
        10: "🔟",
    }
    digits = digits_recursive(num)
    result = ""
    for i in digits:
        result += numbers[i]
    return result


def text_to_value(value, text):
    value2 = 1000
    if text == "к" or text == "k":
        return int(value) * int(value2)
    if text == "кк" or text == "kk":
        return int(value) * (int(value2) ** 2)
    if text == "ккк" or text == "kkk":
        return int(value) * (int(value2) ** 3)
    if text == "кккк" or text == "kkkk":
        return int(value) * (int(value2) ** 4)
    if text == "ккккк" or text == "kkkkk":
        return int(value) * (int(value2) ** 5)
    if text == "кккккк" or text == "kkkkkk":
        return int(value) * (int(value2) ** 6)
    if text == "ккккккк" or text == "kkkkkkk":
        return int(value) * (int(value2) ** 7)
    if text == "кккккккк" or text == "kkkkkkkk":
        return int(value) * (int(value2) ** 8)
    return int(value)


def textify_value(value):
    avalue = abs(value)
    if (
        avalue
        >= 1_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000
    ):
        return (
            str(
                round(
                    value
                    / 1_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000,
                    2,
                )
            )
            + "*"
        )
    if avalue >= 1_000_000_000_000_000_000_000_000_000_000_000:
        return (
            str(round(value / 1_000_000_000_000_000_000_000_000_000_000_000, 2))
            + " дец."
        )
    if avalue >= 1_000_000_000_000_000_000_000_000_000_000:
        return (
            str(round(value / 1_000_000_000_000_000_000_000_000_000_000, 2)) + " нон."
        )
    if avalue >= 1_000_000_000_000_000_000_000_000_000:
        return str(round(value / 1_000_000_000_000_000_000_000_000_000, 2)) + " окт."
    if avalue >= 1_000_000_000_000_000_000_000_000:
        return str(round(value / 1_000_000_000_000_000_000_000_000, 2)) + " сптл."
    if avalue >= 1_000_000_000_000_000_000_000:
        return str(round(value / 1_000_000_000_000_000_000_000, 2)) + " скст."
    if avalue >= 1_000_000_000_000_000_000:
        return str(round(value / 1_000_000_000_000_000_000, 2)) + " квинт."
    if avalue >= 1_000_000_000_000_000:
        return str(round(value / 1_000_000_000_000_000, 2)) + " квдр."
    if avalue >= 1_000_000_000_000:
        return str(round(value / 1_000_000_000_000, 2)) + " трлн."
    if avalue >= 1_000_000_000:
        return str(round(value / 1_000_000_000, 2)) + " млрд."
    if avalue >= 1_000_000:
        return str(round(value / 1_000_000, 2)) + " млн."
    if avalue >= 100_000:
        return str(round(value / 100_000)) + "00K"
    if avalue >= 1000:
        return str(round(value / 1000)) + "K"
    return str(value)


def humanize(value):
    return "{:,}".format(round(value)).replace(",", ".")


async def parse_business_name(uid, b_id):
    p = await get_or_create_profile(uid)
    if int(b_id) == int(1):
        if int(p.business1_level) == 1:
            return p.business1.level1_name
        elif int(p.business1_level) == 2:
            return p.business1.level2_name
        else:
            return p.business1.level3_name
    elif int(b_id) == int(2):
        if int(p.business2_level) == 1:
            return p.business2.level1_name
        elif int(p.business2_level) == 2:
            return p.business2.level2_name
        else:
            return p.business2.level3_name


async def parse_business_smile(uid, b_id):
    p = await get_or_create_profile(uid)
    if int(b_id) == int(1):
        return p.business1.smile
    elif int(b_id) == int(2):
        return p.business2.smile


async def get_or_create_profile(user_id):
    try:
        shopcenters = shopcenter.select()
        job = jobs.select()
        profiles = Profile.select().where(Profile.user_id == user_id)

        profile = list(await manager.prefetch(profiles, shopcenters, job))[0]
    except IndexError:
        profile = await peewee_async.create_object(Profile, user_id=user_id)
    return profile


# @plugin.on_has_text()
# async def register(msg, ats, env):
#     if not msg.text:
#         return "GOON"
#     u, c = await manager.get_or_create(user_info, user_id=msg.from_id)
#     if u.is_banned > 0:
#         return "DONE"
#     await manager.update(u)
#     profile = await get_or_create_profile(msg.from_id)
#     if not profile.last_bonus:
#         profile.last_bonus = datetime.datetime.now()
#         await manager.update(profile)
#     if profile.energy_days <= 0:
#         profile.energy_days = 10
#         await manager.update(profile)
#     if profile.reg == 0:
#         profile.datareg = datetime.date.today()
#         profile.reg = 1
#         return await manager.update(profile)
#     return "GOON"

@plugin.on_startswith_text("эко отнять")
async def ungivemoney(msg, ats, env):
    if not await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_ADMIN>0:
        return await env.reply("вы не можете забирать деньги")
    profile = await get_or_create_profile(msg.from_id)
    try:
        if not env['args']:
            raise ValueError()
        user_idd = env['args'][0]
        amount = env['args'][1]
    except (ValueError, KeyError, IndexError):
        return
    if not await get_or_none(Profile, id=user_idd):
        return await env.reply("пользователя с данным ID не существует")
    c, cr = await manager.get_or_create(Profile, id=user_idd)
    data = c.user_id
    username = await parse_user_name(env, data)
    try:
        value = re.findall(r"\d+", amount)
        text = re.sub(r"[^\w\s]+|[\d]+", r"", amount).strip()
        result = text_to_value(value[0], text)
    except:
        return await env.reply("что-то пошло не так")
    if int(result) < 1:
        return await env.reply("число должно быть больше 0.")
    c.money -= Decimal(result)
    await env.reply(
        f"вы отняли у пользователя {username} сумму в размере {humanize(result)}$"
    )
    user_from = await parse_user_name(env, msg.from_id)
    send = await env.request(
        "messages.send",
        user_id=data,
        message=f"Игрок @id{msg.from_id} ({user_from}) отнял у вас сумму в размере {humanize(result)}$.",
    )
    await Logs.create_log(env, msg.from_id, data, 3, f"Отнял сумму в размере {humanize(result)}$.")
    await manager.update(profile)
    return await manager.update(c)


@plugin.on_startswith_text("эко удалить")
async def ungivemoney(msg, ats, env):
    if not await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_ADMIN>0:
        return await env.reply("вы не можете удалять аккаунт")
    profile = await get_or_create_profile(msg.from_id)
    try:
        if not env['args']:
            raise ValueError()
        user_idd = env['args'][0]
    except (ValueError, KeyError, IndexError):
        return
    if not await get_or_none(Profile, id=user_idd):
        return await env.reply("пользователя с данным ID не существует")
    c, cr = await manager.get_or_create(Profile, id=user_idd)
    data = c.user_id
    username = await parse_user_name(env, data)
    await env.reply(f"аккаунт пользователя {username} очищен")
    await Logs.create_log(env, msg.from_id, data, 13, f"Удалён аккаунт {username}.")
    return await manager.execute(Profile.delete().where(Profile.user_id == data))


def parse_rank_name(rank):
    if rank == 1:
        return "рядовой"
    if rank == 2:
        return "офицер"
    if rank == 3:
        return "заместитель"
    if rank == 4:
        return "основатель"

    # user_privs = await priviligeshelper.getUserPriviliges(env, msg.from_id)
    # cleared_privs = priviligeshelper.strpriv(user_privs)
    # if 'USER_ADMIN' in cleared_privs:
    #     return ""


@plugin.on_startswith_text("профиль")
async def profile(msg, ats, env):
    puid = await parse_user_id(msg, env)
    nextline = "\n"
    if puid:
        if not await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_VIP>0:
            return await env.reply("Вам нужен статус VIP, о нём можно прочитать у меня в группе(в закреплённом посте)")
        username = await parse_user_name(env, puid[0])
        if not await get_or_none(Profile, user_id=puid[0]):
            return await env.reply("запрашиваемый вами пользователь не найден.")
        
        kb = VKKeyboard()
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': '🔝 Топ пользователей', 'payload': {'command': '!эко топ'}, 'color': 'primary'}
            ]
        })
        c = await get_or_create_profile(puid[0])
        text = f"профиль пользователя {username}:\n🆔ID: {c.id}\n💰Баланс: {humanize(c.money)}$ ({textify_value(c.money)})\n{f'💳Банковский счет: {humanize(c.bankmoney)}$ ({textify_value(round(c.bankmoney))}){nextline}' if c.bankmoney > 0 else ''}💱Биткоинов: {humanize(c.btc)}Ƀ\n💹Курс биткоина: {textify_value(int(plugin.bitcoin))}$\n👑Рейтинг: {humanize(round(c.rg))}\n"
        text += f"🏋Энергия: {c.energy_days if not c.last_energy_end > datetime.datetime.now() else 0}\n🏆Опыт: {c.energy_worked}\n📎Железо: {c.iron}\n💰Золото: {c.gold}\n💎Алмазы: {c.diamond}\n"
        if c.job:
            text += f"📋Профессия: {c.job.name}\n"
        if (
            c.house
            or c.car
            or c.airplane
            or c.helicopter
            or c.apartment
            or c.mobile
            or c.other
            or c.yacht
            or c.business1
            or c.business2
        ):
            text += "🏡Ваше имущество:\n"
        if c.house:
            text += f"&#12288;🏠Дом: {c.house.name} (🆔: {c.house_id})\n"
        if c.car:
            text += f"&#12288;🚗Автомобиль: {c.car.name} (🆔: {c.car_id})\n"
        if c.apartment:
            text += f"&#12288;🌇Квартира: {c.apartment.name} (🆔: {c.apartment_id})\n"
        if c.airplane:
            text += f"&#12288;🛩Самолет: {c.airplane.name} (🆔: {c.airplane_id})\n"
        if c.helicopter:
            text += f"&#12288;🚁Вертолет: {c.helicopter.name} (🆔: {c.helicopter_id})\n"
        if c.mobile:
            text += f"&#12288;📱Телефон: {c.mobile.name} (🆔: {c.mobile_id})\n"
        if c.yacht:
            text += f"&#12288;🛥Яхта: {c.yacht.name} (🆔: {c.yacht_id})\n"
#        if c.other:
#            text += f"&#12288;🔋Биткоин ферма: {c.other.name} (🆔: {c.other_id}/Кол-во: {c.btc_amount})\n"
        if c.business1 or c.business2:
            text += "&#12288;💼Бизнесы:\n"
        if c.business1:
            business_name = await parse_business_name(puid, 1)
            smile = await parse_business_smile(puid, 1)
            text += f"&#12288; {smile}{business_name}\n"
        if c.business2:
            smile = await parse_business_smile(puid, 2)
            business_name = await parse_business_name(puid, 2)
            text += f"&#12288; {smile}{business_name}\n"
        if c.clan:
            clan = await get_or_none(clans, id=c.clan)
            role = await get_or_none(clan_members, user_id=puid[0], clan_tag=clan.tag)

            text += f"🏜Клан:\n&#12288;🆔Клан-тэг: {clan.tag}\n&#12288;👔Звание: {parse_rank_name(role.rank)}\n&#12288;🎓В клане с: {role.join_date.split()[0]}\n"
        text += f"💾 Дата регистрации: {c.datareg}"
        return await env.reply(text, keyboard=kb.dump_keyboard())

    kb = VKKeyboard()
    kb.set_inline(True)
    profile = await get_or_create_profile(msg.from_id)
    text = f"ваш профиль:\n🆔ID: {profile.id}\n\n💰Баланс: {humanize(profile.money)}$ ({textify_value(round(profile.money))})\n{f'💳Банковский счет: {humanize(profile.bankmoney)}$ ({textify_value(round(profile.bankmoney))}){nextline}' if profile.bankmoney > 0 else ''}💱Биткоинов: {humanize(profile.btc)}Ƀ\n💹Курс биткоина:{textify_value(int(plugin.bitcoin))}$\n👑Рейтинг: {humanize(round(profile.rg))}\n"
    text += f"🏋Энергия: {profile.energy_days if not profile.last_energy_end > datetime.datetime.now() else 0}\n🏆Опыт: {profile.energy_worked}\n📎Железо: {profile.iron}\n💰Золото: {profile.gold}\n💎Алмазы: {profile.diamond}\n"
    kb.add_row()
    kb.edit_row(0).add_button("🔝 Топ пользователей", payload={'command': f'{env.eenv.prefix}эко топ'}, color="primary")
    if profile.job:
        text += f"📋Профессия: {profile.job.name}\n"   
        
        kb.edit_row(0).add_button("🔨 Работать по профессии", payload={'command': f'{env.eenv.prefix}эко работать'}, color="primary")
    if (
        profile.house
        or profile.car
        or profile.airplane
        or profile.helicopter
        or profile.apartment
        or profile.mobile
        or profile.other
        or profile.yacht
        or profile.business1
        or profile.business2
    ):
        text += "🏡Ваше имущество:\n"
    if profile.house:
        text += f"&#12288;🏠Дом: {profile.house.name} (🆔: {profile.house_id})\n"
    if profile.car:
        text += f"&#12288;🚗Автомобиль: {profile.car.name} (🆔: {profile.car_id})\n"
    if profile.apartment:
        text += (
            f"&#12288;🌇Квартира: {profile.apartment.name} (🆔: {profile.apartment_id})\n"
        )
    if profile.airplane:
        text += (
            f"&#12288;🛩Самолет: {profile.airplane.name} (🆔: {profile.airplane_id})\n"
        )
    if profile.helicopter:
        text += f"&#12288;🚁Вертолет: {profile.helicopter.name} (🆔: {profile.helicopter_id})\n"
    if profile.mobile:
        text += f"&#12288;📱Телефон: {profile.mobile.name} (🆔: {profile.mobile_id})\n"
    if profile.yacht:
        text += f"&#12288;🛥Яхта: {profile.yacht.name} (🆔: {profile.yacht_id})\n"
    pos_b = 1
    #if profile.other:
    #    pos_b+=1
    #    kb.add_row()
    #    kb.edit_row(1).add_button("🔋 статус фермы", payload={'command': f'{env.eenv.prefix}эко ферма'}, color="positive")
    #    text += f"&#12288;🔋Биткоин ферма: {profile.other.name} (🆔: {profile.other_id}/Кол-во: {profile.btc_amount})\n"
    if profile.business1 or profile.business2:
        text += "&#12288;💼Бизнесы:\n"
    if profile.business1:
        kb.add_row()
        kb.edit_row(pos_b).add_button("1 бизнес", payload={'command': f'{env.eenv.prefix}эко бизнес 1'}, color="positive")
        smile = await parse_business_smile(msg.from_id, 1)
        business_name = await parse_business_name(msg.from_id, 1)
        text += f"&#12288;&#12288; {smile}{business_name}\n"
        pos_b+=1
    if profile.business2:
        kb.edit_row(pos_b-1).add_button("2 бизнес", payload={'command': f'{env.eenv.prefix}эко бизнес 2'}, color="positive")
        smile = await parse_business_smile(msg.from_id, 2)
        business_name = await parse_business_name(msg.from_id, 2)
        text += f"&#12288;&#12288; {smile}{business_name}\n"
    if profile.clan:
        clan = await get_or_none(clans, id=profile.clan)
        role = await get_or_none(clan_members, user_id=msg.from_id, clan_tag=clan.tag)
        
        kb.add_row()
        kb.edit_row(pos_b).add_button("🏜 Статистика клана", payload={'command': f'{env.eenv.prefix}клан'}, color="negative")
        pos_b+=1
        text += f"🏜Клан:\n&#12288;🆔Клан-тэг: {clan.tag}\n&#12288;👔Звание: {parse_rank_name(role.rank)}\n&#12288;🎓В клане с: {role.join_date.split()[0]}\n"
    text += f"💾 Дата регистрации: {profile.datareg}\n"
    if await get_or_none(clan_invites, whom_id=msg.from_id):
        kb.add_row()
        kb.edit_row(pos_b).add_button("🏜 Приглашения в кланы", payload={'command': f'{env.eenv.prefix}клан приглашения'}, color="primary")
        text += '\nВас пригласили в клан, чтобы посмотреть список приглашений, введите "приглашения".'
    return await env.reply(text, keyboard=kb.dump_keyboard())


@plugin.on_startswith_text("эко продать бизнес")
async def sell_bus(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if (
        not profile.business1
        and not profile.business2
        or not profile.business2
        and not profile.business1
    ):
        return await env.reply("у вас нет бизнесов, приобрести вы их можете в магазине")
    try:
        amount = env['args'][0]
        if not amount or int(amount) <= 0 or int(amount) > 2:
            raise ValueError()
        num = int(amount)
    except (ValueError, KeyError, IndexError) as e:
        return await env.reply('используйте "продать бизнес [номер бизнеса]"')
    data = profile.business1 if num == 1 else profile.business2
    if not data:
        return await env.reply("у вас нет данного имущества")
    if num == 1:
        price = Decimal((int(profile.business1.price // 1.5)))
        profile.business1 = None
        profile.business1_works = 1
        profile.business1_level = 1
        profile.money += price
        profile.business1_money = 0
    else:
        price = Decimal((int(profile.business2.price // 1.5)))
        profile.business2 = None
        profile.business2_works = 1
        profile.business2_level = 1
        profile.business2_money = 0
        profile.money += price
    await manager.update(profile)
    return await env.reply(f"вы продали бизнес #{num} за {humanize(price)}$.")


@plugin.on_startswith_text("эко магазин")
async def shop(msg, ats, env):
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '🚗', 'payload': {'command': f'{env.eenv.prefix}эко машины'}, 'color': 'primary'},
            {'text': '🛩', 'payload': {'command': f'{env.eenv.prefix}эко самолеты'}, 'color': 'primary'},
            {'text': '🚁', 'payload': {'command': f'{env.eenv.prefix}эко вертолеты'}, 'color': 'primary'},
            {'text': '🛥', 'payload': {'command': f'{env.eenv.prefix}эко яхты'}, 'color': 'primary'},
            {'text': '🏠', 'payload': {'command': f'{env.eenv.prefix}эко дома'}, 'color': 'primary'},
            {'text': '🌇', 'payload': {'command': f'{env.eenv.prefix}эко квартиры'}, 'color': 'primary'},
            {'text': '📱', 'payload': {'command': f'{env.eenv.prefix}эко телефоны'}, 'color': 'primary'},
#            {'text': '⭐', 'payload': {'command': f'{env.eenv.prefix}эко фермы'}, 'color': 'primary'},
            {'text': '💼', 'payload': {'command': f'{env.eenv.prefix}эко бизнесы'}, 'color': 'primary'}
        ]
    })
    data = f'''разделы магазина:
🚙Транспорт:
&#12288;🚗 Машины
&#12288;🛩 Самолеты
&#12288;🚁 Вертолеты
&#12288;🛥 Яхты

🏘Недвижимость:
&#12288;🏠Дома
&#12288;🌇Квартиры
📌 Остальное:
&#12288;📱 Телефоны
&#12288;💼Бизнесы
&#12288;👑 Рейтинг [кол-во] - $100млн.
&#12288;🌐 Биткоин [кол-во]

🔎 Для покупки используйте "эко [категория] [номер]".
&#12288;Например: "эко дома 8"'''
    return await env.reply(data, keyboard=kb.dump_keyboard())


@plugin.on_startswith_text("эко продать железо")
async def sell_iron(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.iron:
        return await env.reply("у вас нет железа")
    pay = random.randint(100, 3000)
    is_vip = False
    if await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_VIP>0:
        pay *= 2
        is_vip = True
    result = int(pay) * int(profile.iron)
    profile.iron = 0
    profile.money += result
    await manager.update( profile)
    return await env.reply(f"вы продали железо за {textify_value(result)}  { ('x2 т.к вы вип' if is_vip else '') }")


@plugin.on_startswith_text("эко продать золото")
async def sell_iron(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.gold:
        return await env.reply("у вас нет золота")
    pay = random.randint(3000, 4500)
    is_vip = False
    if await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_VIP>0:
        pay *= 2
        is_vip = True
    result = int(pay) * int(profile.gold)
    profile.gold = 0
    profile.money += result
    await manager.update(profile)
    return await env.reply(f"вы продали золото за {textify_value(result)}  { ('x2 т.к вы вип' if is_vip else '') }")


@plugin.on_startswith_text("эко продать алмазы")
async def sell_iron(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.diamond:
        return await env.reply("у вас нет алмазов")
    pay = random.randint(5000, 10000)
    is_vip = False
    if await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_VIP>0:
        pay *= 2.5
        is_vip = True
    result = int(pay) * int(profile.diamond)
    profile.diamond = 0
    profile.money += result
    await manager.update(profile)
    return await env.reply(f"вы продали алмазы за {textify_value(result)} { ('x2.5 т.к вы вип' if is_vip else '') }")


@plugin.on_startswith_text("эко баланс")
async def balance(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    vk_message = f"на руках: {humanize(profile.money)}$\n"
    if profile.bankmoney > 0:
        vk_message += f"💳 В банке: {humanize(profile.bankmoney)}$\n"
    if profile.btc > 0:
        vk_message += f"🌐 Биткоинов: {profile.btc}฿\n"
    return await env.reply(vk_message)


@plugin.on_startswith_text("эко машины")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "car")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"машины:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко машины [номер]"')
    else:
        if profile.car:
            return await env.reply(
                f'у вас уже есть машина ({profile.car.name}), введите "эко продать машину"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.car = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили машину ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


#@plugin.on_startswith_text("эко фермы")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "other")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"фермы:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n&#12288;Прибыль: нач. {humanize(shopcenters[i].moneymin)}Ƀ\n"
        return await env.reply(
            text + f'\nДля покупки используйте "эко фермы [номер] [кол-во]"'
        )
    else:
        if not check[0].isdigit():
            return await env.reply("вы не правильно ввели команду, проверьте синтаксис!")

        try:
            amount = env['args'][1]
            if not amount or int(amount) <= 0:
                raise ValueError()
            num = int(amount)
        except (ValueError, KeyError, IndexError) as e:
            num = 1

        if profile.other and profile.other_id != shopcenters[int(check[0]) - 1].id:
            return await env.reply(
                f'у вас уже есть ферма ({profile.other.name}), введите "эко продать ферму"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price * int(num):
            return await env.reply(
                f"у вас недостаточно средств (не хватает {textify_value((shopcenters[int(check[0]) - 1].price * int(num)) - int(profile.money))}$) {plugin.negative} "
            )
        a = datetime.datetime.now().minute
        profile.last_btc_payout = datetime.datetime.now() + timedelta(minutes=-a)
        profile.money -= Decimal(shopcenters[int(check[0]) - 1].price * int(num))
        if profile.other and profile.other_id == shopcenters[int(check[0]) - 1].id:
            profile.btc_amount += int(num)
        else:
            profile.other = shopcenters[int(check[0]) - 1]
            profile.btc_amount = int(num)

        notify_msg = "ваш майнер был остановлен, так как вы купили новую ферму!\n"
        show_msg = True if profile.minercheck == 1 else False
        if profile.minercheck == 1:
            profile.minercheck = 0
        await manager.update(profile)
        return await env.reply(
            f"вы купили {plural_form(num, ('ферму', 'фермы', 'ферм'))} ({shopcenters[int(check[0]) - 1].name}) за {humanize(int(shopcenters[int(check[0]) - 1].price) * int(num))}$ {plugin.positive} {notify_msg if show_msg else ''}"
        )


#@plugin.on_startswith_text("эко продать ферму")
async def miner_sold(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.other:
        return await env.reply("у вас нет ферм, приобрести вы их можете в магазине")
    try:
        amount = env['args'][0]
        if not amount or int(amount) <= 0:
            raise ValueError()
        if amount == "всё" or amount == "все":
            amount = profile.btc_amount
        num = int(amount)
    except (ValueError, KeyError, IndexError) as e:
        num = 1
    if num > int(profile.btc_amount):
        return await env.reply(f"у вас нет столько ферм {plugin.negative}")
    shopcenters = await manager.get(shopcenter, shopcenter.id == profile.other_id)
    profile.money += Decimal((int(shopcenters.price) * int(num)) // 1.5)
    if profile.btc_amount == num:
        profile.other = None
    else:
        profile.btc_amount -= int(num)
    await manager.update(profile)
    return await env.reply(
        f"вы продали {plural_form(num, ('ферму', 'фермы', 'ферм'))} за {humanize((int(shopcenters.price) * int(num))// 1.5)}$."
    )


#plugin.on_text("эко ферма снять")
async def miner_minus(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.other:
        return await env.reply(f"у вас нет фермы, купить её можно в магазине")
    if profile.minercheck == 0:
        return await env.reply("введите 'ферма' , чтобы запустить майнер")
    if not profile.last_btc_payout:
        a = datetime.datetime.now().minute
        profile.last_btc_payout = datetime.datetime.now() + timedelta(minutes=-a)
        await manager.update(profile)
    a = time.time()
    b = time.mktime(profile.last_btc_payout.timetuple())
    res = (a - b) // 3600
    if (profile.other.moneymin / 10) * res <= 0:
        return await env.reply(f"вы еще ничего не заработали {plugin.negative}")
    profile.btc += (profile.other.moneymin) * res * profile.btc_amount
    profile.tt = time.time()
    profile.minercheck = 0
    profile.last_btc_payout = datetime.datetime.now()
    await manager.update(profile)
	
    kb = VKKeyboard()
    kb.lazy_buttons({
		'inline': True,
		'buttons': [
			{'text':'🔛 Включить майнер снова', 'payload': {'command': f'{env.eenv.prefix}эко ферма'}, 'color':'positive'},
			{'text':'Ƀ Продать заработанные биткоины', 'payload': {'command': f'{env.eenv.prefix}эко продать биткоин {round((profile.other.moneymin) * res * profile.btc_amount)}'}, 'color':'primary'}
		]
	})
    return await env.reply(
        f"вы заработали {round((profile.other.moneymin) * res * profile.btc_amount)}₿.\nНе забудьте включить майнер!",
		keyboard=kb.dump_keyboard()
    )


#@plugin.on_text("эко ферма")
async def miner(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.other:
        return await env.reply(f"у вас нет фермы, купить её можно в магазине")
    if profile.minercheck == 0:
        a = datetime.datetime.now().minute
        profile.last_btc_payout = datetime.datetime.now() + timedelta(minutes=-a)
        profile.minercheck = 1
        await manager.update(profile)
        await env.reply("Майнер запущен.")
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': 'Снять заработок и отключить майнер', 'payload': {'command': f'{env.eenv.prefix}эко ферма снять'}, 'color': 'negative'}
        ]
    })
    data = "🔋Статистика биткоин фермы:\n"
    a = time.time()
    b = time.mktime(profile.last_btc_payout.timetuple())
    d = str(datetime.datetime.now() - profile.last_btc_payout).split(":")
    res = (a - b) // 3600
    data += f"♻Ферма: {profile.other.name} (кол-во: {profile.btc_amount})\n"
    data += f"⌛Время работы: {d[0]}hours, {d[1]}minutes\n"
    data += f"📈Скорость работы: {(profile.other.moneymin) * profile.btc_amount}₿/ч\n"
    data += f'💰Текущий заработок: {round((profile.other.moneymin) * res * profile.btc_amount)}₿\nЧтобы снять текущий заработок, введите "ферма снять"'
    return await env.reply(data, keyboard=kb.dump_keyboard())


@plugin.on_startswith_text("эко яхты")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "yacht")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"яхты:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко яхты [номер]"')
    else:
        if profile.yacht:
            return await env.reply(
                f'у вас уже есть яхта ({profile.yacht.name}), введите "эко продать яхту"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.yacht = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили яхту ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


@plugin.on_startswith_text("эко самолеты")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "airplane")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"самолеты:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко амолеты [номер]"')
    else:
        if profile.airplane:
            return await env.reply(
                f'у вас уже есть самолет ({profile.airplane.name}), введите "эко продать самолет"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.airplane = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили самолет ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


@plugin.on_startswith_text("эко вертолеты")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "helicopter")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"вертолеты:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко вертолеты [номер]"')
    else:
        if not check[0].isdigit():
            return await env.reply("вы не правильно ввели команду, проверьте синтаксис!")

        if profile.helicopter:
            return await env.reply(
                f'у вас уже есть вертолет ({profile.helicopter.name}), введите "эко продать вертолет"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.helicopter = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили вертолет ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


@plugin.on_startswith_text("эко дома")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "house")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"дома:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко дома [номер]"')
    else:
        if profile.house:
            return await env.reply(
                f'у вас уже есть дом ({profile.house.name}), введите "продать дом"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.house = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили дом ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


@plugin.on_startswith_text("эко квартиры")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "apartment")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"квартиры:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко квартиры [номер]"')
    else:
        if profile.apartment:
            return await env.reply(
                f'у вас уже есть квартира ({profile.apartment.name}), введите "эко продать квартиру"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.apartment = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили квартиру ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


@plugin.on_startswith_text("эко телефоны")
async def cars(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    shopcenters = list(
        await manager.execute(
            shopcenter.select()
            .where(shopcenter.slot == "mobile")
            .order_by(shopcenter.price)
        )
    )
    if len(check) < 1:
        text = f"телефоны:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].name} - {humanize(shopcenters[i].price)}$\n"
        return await env.reply(text + f'\nДля покупки используйте "эко телефоны [номер]"')
    else:
        if profile.mobile:
            return await env.reply(
                f'у вас уже есть телефон ({profile.mobile.name}), введите "эко продать телефон"'
            )
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        profile.mobile = shopcenters[int(check[0]) - 1]
        await manager.update(profile)
        return await env.reply(
            f"вы купили телефон ({shopcenters[int(check[0]) - 1].name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}"
        )


@plugin.on_startswith_text("эко продать биткоин")
async def btc(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    try:
        amount = env['args'][0]
        if not amount or int(amount) <= 0:
            raise ValueError()
        if amount == "всё" or amount == "все":
            amount = profile.btc
        num = int(amount)
    except (ValueError, KeyError, IndexError) as e:
        num = 1
    if num > int(profile.btc):
        return await env.reply("недостаточно биткоинов")
    profile.money += int(plugin.bitcoin) * int(num)
    profile.btc -= int(num)

    kb = VKKeyboard()
    kb.set_inline(True)
    kb.add_row()
    kb.edit_row(0).add_button("₿ продать столько же", payload={'command': f'{env.eenv.prefix}эко продать биткоин {num}'})
    if profile.btc > 0:
        kb.add_row()
        kb.edit_row(1).add_button("₿ продать всё", payload={'command': f'{env.eenv.prefix}эко продать биткоин {profile.btc}'})
    await manager.update(profile)
    return await env.reply(
        f"вы продали {int(num)}Ƀ за {humanize(int(plugin.bitcoin) * int(num))}$.",
        keyboard=kb.dump_keyboard()
    )


@plugin.on_startswith_text("эко рейтинг")
async def raiting(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    try:
        amount = env['args'][0]
        if not amount.isdigit():
            return await env.reply("число отрицательное")
    except (ValueError, KeyError, IndexError):
        if profile.rg > 0:
            return await env.reply(f"ваш рейтинг - {profile.rg}👑")
        return await env.reply(f"у вас нет рейтинга {plugin.negative}")
    if int(amount) * int(100_000_000) > int(profile.money):
        return await env.reply(
            f"недостаточно средств для покупки рейтинга {plugin.negative}"
        )
    profile.money -= int(100_000_000) * int(amount)
    profile.rg += int(amount)
    
    kb = None
    if profile.money > (int(100_000_00) * int(amount)):
        kb = VKKeyboard()
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': 'Купить столько же', 'payload': {'command': f'{env.eenv.prefix}эко рейтинг {amount}'}, 'color': 'positive'}
            ]
        })
    await manager.update(profile)
    return await env.reply(
        f"вы приобрели {int(amount)}👑 за {humanize(int(100000000) * int(amount))}$.",
        keyboard=kb.dump_keyboard() if kb else "{}"
    )


@plugin.on_startswith_text("эко продать рейтинг")
async def raiting_sell(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    try:
        amount = env['args'][0]
        if not amount or int(amount) <= 0:
            raise ValueError()
        if amount == "всё" or amount == "все":
            amount = profile.rg
        num = int(amount)
    except (ValueError, KeyError, IndexError) as e:
        num = 1
    if num > int(profile.rg):
        return await env.reply("у вас нет столько рейтинга")
    profile.money += int(100_000_000) * int(num)
    profile.rg -= int(num)
    await manager.update(profile)
    return await env.reply(
        f"вы продали {int(num)}👑 за {humanize(int(100000000) * int(num))}$."
    )


@plugin.on_startswith_text("эко продать")
async def sell(msg, ats, env):
    try:
        slot = env['args'][0]
    except (ValueError, KeyError, IndexError):
        return
    if slot.lower() not in (
        "дом",
        "машину",
        "вертолет",
        "квартиру",
        "самолет",
        "телефон",
        "яхту",
    ):
        return
    profile = await get_or_create_profile(msg.from_id)
    amount = 1
    data = None
    d_type = 0
    if slot.lower() == "дом":
        data = profile.house_id
        profile.house_id = None
    if slot.lower() == "машину":
        data = profile.car_id
        profile.car_id = None
    if slot.lower() == "вертолет":
        data = profile.helicopter_id
        profile.helicopter_id = None
    if slot.lower() == "квартиру":
        data = profile.apartment_id
        profile.apartment_id = None
    if slot.lower() == "самолет":
        data = profile.airplane_id
        profile.airplane_id = None
    if slot.lower() == "телефон":
        data = profile.mobile_id
        profile.mobile_id = None
    if slot.lower() == "яхту":
        data = profile.yacht
        profile.yacht_id = None
    try:
        if data is None:
            return await env.reply(
                "у вас нет данного предмета {}".format(plugin.negative)
            )
    except (TypeError):
        return await env.reply("у вас нет данного предмета {}".format(plugin.negative))
    if d_type == 1:
        shopcenters = await manager.get(business_shop, business_shop.id == data)
    else:
        shopcenters = await manager.get(shopcenter, shopcenter.id == data)
    pr = (shopcenters.price * amount) // 1.5
    profile.money += int(pr)
    await manager.update(profile)
    return await env.reply(f"вы продали {slot.lower()} за {humanize(pr)}$")


@plugin.on_startswith_text("эко передать")
async def btc_send(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    try:
        user_idd, amount = env['args'][0], env['args'][1]
    except (ValueError, KeyError, IndexError):
        return
    if not await get_or_none(Profile, id=user_idd):
        return await env.reply("пользователя с данным ID не существует")
    if int(user_idd) == profile.id:
        return await env.reply("передавать самому себе бессмысленно.")
    c, cr = await manager.get_or_create(Profile, id=user_idd)
    data = c.user_id
    username = await parse_user_name(env, data)
    if amount == "всё" or amount == "все":
        amount = profile.money
        result = amount
    else:
        if not amount.isdigit():
            return await env.reply("Сумма должна быть числом")

        result = int(amount)

    if int(result) < 1:
        return await env.reply("число должно быть больше 0.")
    if int(profile.money) < result:
        return await env.reply("на вашем счете недостаточно средств.")
    c.money += result
    profile.money -= result
    await env.reply(
        f"вы передали пользователю {username} сумму в размере {humanize(result)}$ ."
    )
    user_from = await parse_user_name(env, msg.from_id)
    await env.request(
        "messages.send",
        user_id=c.user_id,
        message=f"Игрок @id{msg.from_id} ({user_from}) передал вам сумму в размере {humanize(result)}$.",
    )
    await manager.update(profile)
    return await manager.update(c)


@plugin.on_startswith_text("эко биткоин")
async def btc(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    try:
        amount = env['args'][0]
        if not amount or int(amount) <= 0:
            raise ValueError()
    except (ValueError, KeyError, IndexError):
        if int(profile.btc) > 0:
            return await env.reply(f"на вашем счете {profile.btc}₿")
        return await env.reply(f"у вас нет биткоинов {plugin.negative}")
    if int(profile.money) < int(plugin.bitcoin) * int(amount):
        return await env.reply(
            "недостаточно денег {}\nКурс биткоина: {}$".format(
                plugin.negative, humanize(plugin.full_bitcoin)
            )
        )
    profile.money -= int(plugin.bitcoin) * int(amount)
    profile.btc += int(amount)
    await manager.update(profile)

    kb = None
    if profile.money > (int(plugin.bitcoin) * int(amount)):
        kb = VKKeyboard()
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': '₿ купить столько же', 'payload': {'command': f'{env.eenv.prefix}эко биткоин {amount}'}, 'color': 'positive'}
            ]
        })
    return await env.reply(
        f"вы приобрели {int(amount)}Ƀ за {humanize(int(plugin.bitcoin) * int(amount))}$.",
        keyboard=kb.dump_keyboard() if kb else "{}"
    )

@plugin.on_startswith_text("эко банк")
async def bank_operation(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    # operation - 0
    # summ - 1
    operation = None
    args = env['args']
    
    if not args and len(args)<2:
        operation = "balance"
    elif args and len(args)<2:
        return await env.reply("Пожалуйста введите, что вы хотите сделать с банком")
    elif args[0] == "снять":
        operation = "payout"
    elif args[0] == "вложить":
        operation = "payin"
    else:
        operation = "balance"

    if operation == "balance":
        if int(profile.bankmoney) > 0:
            kb = VKKeyboard()
            kb.lazy_buttons({
                'inline': True,
                'buttons': [
                    {'text': '💸 100', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 100'}, 'color': 'primary'},
                    {'text': '💸 1000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 1000'}, 'color': 'primary'},
                    {'text': '💸 10 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 10000'}, 'color': 'primary'},
                    {'text': '💸 100 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 100000'}, 'color': 'primary'},
                    {'text': '💸 1 000 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 1000000'}, 'color': 'primary'},
                    {'text': '💸 100 000 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 100000000'}, 'color': 'primary'},
                    {'text': '💸 1 000 000 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 1000000000'}, 'color': 'primary'}
                ]
            })
            kb.add_row()
            kb.edit_row(2).add_button("Cнять всё", payload={'command': f'{env.eenv.prefix}эко банк снять все'}, color="positive")
            return await env.reply(
                f"на вашем банковском счете находится {humanize(profile.bankmoney)}$",
                keyboard=kb.dump_keyboard()
            )
        else:
            kb = VKKeyboard()
            kb.lazy_buttons({
                'inline': True,
                'buttons': [
                    {'text': '💸 100', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 100'}, 'color': 'primary'},
                    {'text': '💸 1000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 1000'}, 'color': 'primary'},
                    {'text': '💸 10 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 10000'}, 'color': 'primary'},
                    {'text': '💸 100 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 100000'}, 'color': 'primary'},
                    {'text': '💸 1 000 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 1000000'}, 'color': 'primary'},
                    {'text': '💸 100 000 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 100000000'}, 'color': 'primary'},
                    {'text': '💸 1 000 000 000', 'payload': {'command': f'{env.eenv.prefix}эко банк вложить 1000000000'}, 'color': 'primary'}
                ]
            })
            return await env.reply(
                "вы ничего не вкладывали в банк!",
                keyboard=kb.dump_keyboard()
            )
    
    amount = 0
    if args[1] == "всё" or args[1] == "все":
        amount = int(profile.bankmoney) - 100
    else:
        if args[1].isdigit():
            amount = int(args[1])
        else:
            return await env.reply("Сумма некорректна")
    if operation == "payout":
        if profile.bankmoney < amount:
            return await env.reply("На вашем банковском счету не достаточно денег")

        profile.bankmoney -= amount
        profile.money += amount
        await manager.update(profile)
        return await env.reply(
            "вы сняли {}$\n💳 Остаток на счёте: {}$\n💰 Ваш баланс: {}$".format(
                humanize(amount), humanize(profile.bankmoney), humanize(profile.money)
            )
        )

    if operation == "payin":
        if amount < 50:
            return await env.reply("минимальная сумма вклада 50$")
        if profile.money < amount:
            return await env.reply("Сумма на вашем аккаунте меньше чем вы хотите вложить")

        profile.bankmoney += amount
        profile.money -= amount
        await manager.update(profile) 
        return await env.reply(f"вы пополнили банковский счет на {humanize(amount)}$")

@plugin.on_text("эко топ")
async def top(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    top = list(
        await manager.execute(
            Profile.select()
            .where(Profile.money > 5000)
            .order_by(
                (
                    Profile.rg * int(100_000_000) + Profile.money + Profile.bankmoney
                ).desc()
            )
        )
    )
    data = []
    for u in top:
        privs = await priviligeshelper.getUserPriviliges(env, u.user_id)
        if privs&priviligeshelper.USER_ADMIN>0 or privs&priviligeshelper.USER_MODERATOR>0:
            continue
        data.append({"id": u.user_id, "rg": u.rg, "money": u.money, "bankmoney": u.bankmoney})

    mesto = list(z["id"] for z in data)
    text = "топ игроков:\n"
    for i in enumerate(data[:10], start=1):
        name = await parse_user_name(env, i[1]["id"])
        num = num_to_smile(i[0])
        text += f"{num}. @id{i[1]['id']} ({name}) -- 👑{textify_value(round(i[1]['rg']))} | {textify_value(int(i[1]['money'] + i[1]['bankmoney']))}$\n"
    if msg.from_id in mesto and mesto.index(int(msg.from_id)) + 1 > 10:
        name = await parse_user_name(env, msg.from_id)
        num = num_to_smile(mesto.index(int(msg.from_id)) + 1)
        text += f"----------------------------\n{num if int(mesto.index(int(msg.from_id)) + 1) < 100 else '▶' + '1⃣0⃣0⃣'}. {name} -- 👑{textify_value(round(profile.rg))} | {textify_value(int(profile.money + profile.bankmoney))}$"
    return await env.reply(text)


@plugin.on_text("эко работать")
async def working(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.job:
        return await env.reply(
            f'вы нигде не работаете {plugin.negative}\nДля трудоустройства введите "работа"'
        )
    if profile.last_job_end and profile.last_job_end > datetime.datetime.now():
        data = profile.last_job_end - datetime.datetime.now()
        hours, minutes, seconds = convert_timedelta(data)
        plural_h = plural_form(hours, ("час", "часа", "часов"))
        plural_m = plural_form(minutes, ("минута", "минуты", "минут"))
        return await env.reply(
            f"рабочая неделя завершена.\n⏳ Вы сможете работать через {minutes}:{seconds if seconds >= 10 else '0' + str(seconds)}"
        )
    if profile.job_days == 1:
        profile.last_job_end = datetime.datetime.now() + datetime.timedelta(hours=1)
    profile.job_days -= 1 if profile.job_days != 1 else -2
    pay = profile.job.pay + random.randint(100, 2000)
    profile.money += Decimal(pay)
    profile.job_worked += 1
    await manager.update(profile)
    vk_message = f"рабочий день закончен.\n💵Вы заработали {humanize(pay)}$\n"
    shopcenters = list(
        await manager.execute(
            jobs.select()
            .where(profile.job_worked >= jobs.need_days)
            .order_by(jobs.need_days)
        )
    )
    allowed_works = []
    for i in range(len(shopcenters)):
        if (
            shopcenters[i].need_days == profile.job_worked
            and shopcenters[i].name != profile.job.name
        ):
            allowed_works.append(
                f"&#12288;🔹 {shopcenters[i].type_name} - {shopcenters[i].name}"
            )
    if len(allowed_works) > 0:
        nextline = "\n"
        vk_message += f"💡 Доступны новые профессии:\n{nextline.join(allowed_works)}"

    kb = VKKeyboard()
    kb.set_inline(True)
    kb.add_row()
    kb.edit_row(0).add_button("💵 Работать ещё", payload={'command': f'{env.eenv.prefix}эко работать'}, color="positive")
    kb.add_row()
    kb.edit_row(1).add_button("💵 Уйти с работы", payload={'command': f'{env.eenv.prefix}эко уволиться'}, color="negative")
    return await env.reply(vk_message, keyboard=kb.dump_keyboard())


@plugin.on_text("эко уволиться")
async def leave_job(msg, ats, env):
    profile = await get_or_create_profile(msg.from_id)
    if not profile.job:
        return await env.reply(
            f'вы нигде не работаете {plugin.negative}\nДля трудоустройства введите "работа"'
        )
    profile.job = None
    await manager.update(profile)
    return await env.reply(f"вы уволились со своей работы {plugin.negative}")


@plugin.on_startswith_text("эко работа")
async def work(msg, ats, env):
    if "работать" in env['args']:
        return
    profile = await get_or_create_profile(msg.from_id)
    check = env['args'] if env['args'] else []
    num = 1
    if len(check) < 1:
        shopcenters = list(
            await manager.execute(
                jobs.select(jobs.type_name)
                .where(profile.job_worked >= jobs.need_days)
                .order_by(jobs.pay)
            )
        )
        text = f"вы можете устроиться на одну из работ:\n"
        jobs_type = []
        jobs_user = {}
        for i in range(len(shopcenters)):
            if shopcenters[i].type_name in jobs_type:
                continue
            text += f"🔹 {num_to_smile(num)}. {shopcenters[i].type_name}\n"
            num += 1
            jobs_type.append(shopcenters[i].type_name)
        plugin.jobs_user[msg.from_id] = jobs_type
        text += 'для просмотра списка профессий введите "работа [номер]"'
        plugin.is_active[msg.from_id] = 1
        return await env.reply(text)
    else:
        if msg.from_id not in plugin.is_active:
            return await env.reply(
                'используйте команду "работа" для просмотра списка профессий'
            )

        if not check[0].isdigit():
            return await env.reply("вы не правильно ввели команду, проверьте синтаксис!")

        if plugin.is_active[msg.from_id] == 1 and int(check[0]) - 1 > len(
            plugin.jobs_user[msg.from_id]
        ):
            return await env.reply(
                "у вас недостаточно опыта работы, список доступных для вас работ - работа"
            )
        if not check[0].isdigit():
            return await env.reply("Укажите номер желаемой категории.")
        numerate = 1
        if plugin.is_active[msg.from_id] == 1:
            user_jobs = []
            try:
                jobs_list = list(
                    await manager.execute(
                        jobs.select()
                        .where(
                            jobs.type_name
                            == plugin.jobs_user[msg.from_id][int(check[0]) - 1]
                        )
                        .order_by(jobs.pay)
                    )
                )
            except:
                return await env.reply("указанная вами работа недоступна")
            vk_message = (
                f"профессии ({plugin.jobs_user[msg.from_id][(int(check[0])-1)]}):\n"
            )
            for i in range(len(jobs_list)):
                if jobs_list[i].need_days > profile.job_worked:
                    continue
                user_jobs.append(jobs_list[i])
                vk_message += f"🔹 {num_to_smile(numerate)}. {jobs_list[i].name} - зарплата ~ {jobs_list[i].pay * 3}$\n"
                numerate += 1
            plugin.user_jobs[msg.from_id] = user_jobs
            vk_message += 'для трудоустройства введите "эко работа [номер]"'
            plugin.is_active[msg.from_id] = 2
            return await env.reply(vk_message)
        if plugin.is_active[msg.from_id] == 2:
            if profile.job:
                return await env.reply(
                    f'вы уже трудоустроены в {profile.job.type_name} - {profile.job.name}\n💾Введите команду "эко уволиться"'
                )
            if int(check[0]) - 1 > len(plugin.user_jobs[msg.from_id]):
                return await env.reply("данная работа не найдена")
            try:
                profile.job = plugin.user_jobs[msg.from_id][int(check[0]) - 1]
            except:
                return await env.reply("произошла ошибка при приёме на работу, возможно вам отказали!")
            plugin.is_active.pop(msg.from_id)
            vk_message = f'вы устроились работать в {plugin.user_jobs[msg.from_id][int(check[0]) - 1].type_name} - {plugin.user_jobs[msg.from_id][int(check[0]) - 1].name}\n👔Введите команду "эко работать".'
            await manager.update(profile)
            return await env.reply(vk_message)


@plugin.on_startswith_text("эко бизнесы")
async def businesses(msg, ats, env):
    check = env['args'] if env['args'] else []
    profile = await get_or_create_profile(msg.from_id)
    shopcenters = list(await manager.execute(business.select().order_by(business.price)))
    if len(check) < 1:
        text = f"бизнесы:\n"
        for i in range(len(shopcenters)):
            text += f"{'🔸' if profile.money < shopcenters[i].price else '🔹'} {i + 1}. {shopcenters[i].level1_name} - {humanize(shopcenters[i].price)}$\n&#12288;Прибыль: {humanize(shopcenters[i].pay)}\n"
        return await env.reply(text + f'\nДля покупки используйте "эко бизнесы [номер]"')
    else:
        if not check[0].isdigit():
            return
        if (
            profile.business1
            and profile.business2
            or profile.business2
            and profile.business1
        ):
            return await env.reply(
                f'у вас уже есть 2 бизнеса, введите "эко продать бизнес [номер]"'
            )
        if (
            profile.business1
            and profile.business1_id == shopcenters[int(check[0]) - 1].id
            or profile.business2
            and profile.business2_id == shopcenters[int(check[0]) - 1].id
        ):
            return await env.reply("у вас уже есть этот бизнес")
        if not check[0].isdigit():
            return
        if int(check[0]) > len(shopcenters):
            return
        if int(profile.money) < shopcenters[int(check[0]) - 1].price:
            return await env.reply(f"у вас недостаточно средств {plugin.negative}")
        profile.money -= shopcenters[int(check[0]) - 1].price
        if profile.business1 and not profile.business2:
            profile.business2 = shopcenters[int(check[0]) - 1]
            profile.business2_run = datetime.datetime.now()
            profile.business2_works = 1
            profile.business2_level = 1
            profile.business2_money = 0
        else:
            profile.business1 = shopcenters[int(check[0]) - 1]
            profile.business1_run = datetime.datetime.now()
            profile.business1_works = 1
            profile.business1_level = 1
            profile.business1_money = 0
        await manager.update(profile)
        return await env.reply(
            f'вы купили бизнес ({shopcenters[int(check[0]) - 1].level1_name}) за {humanize(shopcenters[int(check[0]) - 1].price)}$ {plugin.positive}\nЧтобы узнать статистику бизнесов, введите "эко бизнес [1-2]"'
        )


@plugin.on_startswith_text("эко бизнес")
async def business_menu(msg, ats, env):
    check = env['args'] if env['args'] else []
    check1 = env['args'] if env['args'] else []
    profile = await get_or_create_profile(msg.from_id)
    num = 1
    if (
        not profile.business1
        and not profile.business2
        or not profile.business2
        and not profile.business1
    ):
        return await env.reply(f"у вас нет бизнеса, купить его можно в магазине")
    if len(check) < 1:
        if (
            profile.business1
            and not profile.business2
            or profile.business2
            and not profile.business1
        ):
            business_name = await parse_business_name(
                msg.from_id, 1 if profile.business1 else 2
            )
            text = f'статистика "{business_name}":\n'
            if profile.business1:
                kb = VKKeyboard()
                kb.set_inline(True)
                kb.add_row()
                kb.edit_row(0).add_button("💰 Снять полученную прибыль", payload={'command': f'{env.eenv.prefix}эко бизнес снять 1 все'}, color="positive") 
                pay = profile.business1_works * 50_000 + profile.business1.pay
                text += f"💸 Прибыль: {humanize(pay)}$/час\n"
                if profile.business1_level == 1:
                    works = profile.business1.max_works
                elif profile.business1_level == 2:
                    works = profile.business1.max_works * 5
                else:
                    works = profile.business1.max_works * 5 * 3
                text += f"💼 Рабочих: {profile.business1_works}/{works}\n"
                a = time.time()
                b = time.mktime(profile.business1_run.timetuple())
                res = (a - b) // 3600
                profile.business1_money += (
                    Decimal(pay * res) if (pay) * res != profile.last_bus1_pay else 0
                )
                profile.last_bus1_pay = Decimal(pay * res)
                await manager.update(profile)
                text += f"💰 На счёте: {humanize(profile.business1_money)}$\n"
                if profile.business1_works < works:
                    text += '⚠ У вас работает недостаточно людей, от этого уменьшена прибыль. Введите "Бизнес нанять 1 [кол-во]"'
                if profile.business1_level < 3:
                    text += f'\n✅ Доступно улучшение! ({humanize(profile.business1.up_price * (profile.business1_level + 1) if profile.business1_level > 1 else profile.business1.up_price)}$)\nВведите "Бизнес улучшить 1" для улучшения бизнеса'
                return await env.reply(text, keyboard=kb.dump_keyboard())
            else:
                kb = VKKeyboard()
                kb.set_inline(True)
                kb.add_row()
                kb.edit_row(0).add_button("💰 Снять полученную прибыль", payload={'command': f'{env.eenv.prefix}эко бизнес снять 2 все'}, color="positive") 
                pay = profile.business2_works * 50_000 + profile.business2.pay
                text += f"💸 Прибыль: {humanize(pay)}$/час\n"
                if profile.business2_level == 1:
                    works = profile.business2.max_works
                elif profile.business2_level == 2:
                    works = profile.business2.max_works * 5
                else:
                    works = profile.business2.max_works * 5 * 3
                text += f"💼 Рабочих: {profile.business2_works}/{works}\n"
                a = time.time()
                b = time.mktime(profile.business2_run.timetuple())
                res = (a - b) // 3600
                profile.business2_money += (
                    Decimal(pay * res) if (pay) * res != profile.last_bus2_pay else 0
                )
                profile.last_bus2_pay = Decimal(pay * res)
                await manager.update(profile)
                text += f"💰 На счёте: {humanize(profile.business2_money)}$\n"
                if profile.business2_works < works:
                    text += '⚠ У вас работает недостаточно людей, от этого уменьшена прибыль. Введите "Бизнес нанять 2 [кол-во]"'
                if profile.business2_level < 3:
                    text += f'\n✅ Доступно улучшение! ({humanize(profile.business2.up_price * (profile.business2_level + 1) if profile.business2_level > 1 else profile.business2.up_price)}$)\nВведите "Бизнес улучшить 2" для улучшения бизнеса'
                return await env.reply(text, keyboard=kb.dump_keyboard())
        else:
            text = 'у вас в наличии 2 бизнеса.\nВведите "эко бизнес [1-2]" для выбора одного из них:\n'
            business1_name = await parse_business_name(msg.from_id, 1)
            business2_name = await parse_business_name(msg.from_id, 2)
            smile1 = await parse_business_smile(msg.from_id, 1)
            smile2 = await parse_business_smile(msg.from_id, 2)
            text += f"1⃣. {smile1}{business1_name}\n2⃣. {smile2}{business2_name}"
            return await env.reply(text)
    else:
        if check[0].lower() == "улучшить":
            if len(check) < 2:
                return
            if not check[1].isdigit() or int(check[1]) > 2 or int(check[1]) < 1:
                return
            if int(check[1]) == 2:
                if not profile.business2:
                    return
                if profile.business2_level >= 3:
                    return await env.reply("нет доступных улучшений")
                price = (
                    profile.business2.up_price * (profile.business2_level + 1)
                    if profile.business2_level > 1
                    else profile.business2.up_price
                )
                if profile.money < price:
                    return await env.reply("недостаточно средств")
                profile.business2_level += 1
                profile.money -= Decimal(price)
                await manager.update(profile)
                business_name = await parse_business_name(msg.from_id, 2)
                return await env.reply(f'вы улучшили свой бизнес до "{business_name}"')
            elif int(check[1]) == 1:
                if not profile.business1:
                    return
                if profile.business1_level >= 3:
                    return await env.reply("нет доступных улучшений")
                price = (
                    profile.business1.up_price * (profile.business1_level + 1)
                    if profile.business1_level > 1
                    else profile.business1.up_price
                )
                if profile.money < price:
                    return await env.reply("недостаточно средств")
                profile.business1_level += 1
                profile.money -= Decimal(price)
                await manager.update(profile)
                business_name = await parse_business_name(msg.from_id, 1)
                return await env.reply(f'вы улучшили свой бизнес до "{business_name}"')
        elif check[0].lower() == "снять":
#0 - снять
#1 - {1-2}
#2 - кол-во
            if len(check) < 3:
                return
            if not check[1].isdigit() or int(check[1]) > 2 or int(check[1]) < 1:
                return
            print(check)
            if check[2].lower() == "всё" or check[2].lower() == "все":
                amount = (
                    profile.business2_money
                    if int(check[1]) == 2
                    else profile.business1_money
                )
                result = amount
            else:
                value = re.findall(r"\d+", check[2].lower())
                text = re.sub(r"[^\w\s]+|[\d]+", r"", check[2].lower()).strip()
                result = text_to_value(value[0], text)
            if int(result) < 1:
                return await env.reply("число должно быть больше 0.")
            if int(check[1]) == 1:
                if not profile.business1:
                    return
                a = time.time()
                b = time.mktime(profile.business1_run.timetuple())
                res = (a - b) // 3600
                if profile.business1_money < result:
                    return await env.reply("на счету бизнеса нет столько средств")
                profile.business1_money -= Decimal(result)
                profile.business1_run = datetime.datetime.now()
                profile.money += Decimal(result)
            else:
                if not profile.business2:
                    return
                a = time.time()
                b = time.mktime(profile.business2_run.timetuple())
                res = (a - b) // 3600
                if profile.business2_money < result:
                    return await env.reply("на счету бизнеса нет столько средств")
                profile.business2_money -= Decimal(result)
                profile.business2_run = datetime.datetime.now()
                profile.money += Decimal(result)
            await manager.update(profile)
            return await env.reply(
                f"вы сняли со счета бизнеса #{check[1]} {humanize(result)}$\n\n⚠Учтите, что при найме рабочих время работы бизнеса сбрасывается в связи с предотвращением абуза денег."
            )
        elif check[0].lower() == "нанять":
            if len(check) < 2:
                return
            if not check[1].isdigit() or int(check[1]) > 2 or int(check[1]) < 1:
                return
            if not check[1].isdigit():
                return
            if int(check[1]) == 2:
                if not profile.business2:
                    print("start!4")
                    return
                if profile.business2_level == 1:
                    works = profile.business2.max_works
                elif profile.business2_level == 2:
                    works = profile.business2.max_works * 5
                else:
                    works = profile.business2.max_works * 5 * 3
                if (
                    profile.business2_works >= works
                    or profile.business2_works + int(check[2]) > works
                ):
                    return await env.reply(
                        "достигнуто макс. кол-во рабочих или количество превышает максимума"
                    )
                price = 750_000 * int(check[2])
                if profile.money < price:
                    return await env.reply(
                        f"недостаточно средств (требуется {humanize(price)}$)"
                    )
                profile.business2_works += int(check[2])
                profile.money -= Decimal(price)
                profile.business2_run = datetime.datetime.now()
                await manager.update(profile)
                return await env.reply(
                    f"вы наняли {plural_form(int(check[2]), ('рабочего', 'рабочих', 'рабочих'))}\n\n⚠Учтите, что при найме рабочих время работы бизнеса сбрасывается в связи с предотвращением абуза денег."
                )
            elif int(check[1]) == 1:
                if not profile.business1:
                    return
                if profile.business1_level == 1:
                    works = profile.business1.max_works
                elif profile.business1_level == 2:
                    works = profile.business1.max_works * 5
                else:
                    works = profile.business1.max_works * 5 * 3
                if (
                    profile.business1_works >= works
                    or profile.business1_works + int(check[2]) > works
                ):
                    return await env.reply(
                        "достигнуто макс. кол-во рабочих или количество превышает максимума"
                    )
                price = 750_000 * int(check[2])
                if profile.money < price:
                    return await env.reply(
                        f"недостаточно средств (требуется {humanize(price)}$)"
                    )
                profile.business1_works += int(check[2])
                profile.money -= Decimal(price)
                profile.business1_run = datetime.datetime.now()
                await manager.update(profile)
                return await env.reply(
                    f"вы наняли {plural_form(int(check[2]), ('рабочего', 'рабочих', 'рабочих'))}\n\n⚠Учтите, что при найме рабочих время работы бизнеса сбрасывается в связи с предотвращением абуза денег."
                )
        if not check[0].isdigit():
            return await env.reply("вы не правильно ввели команду, проверьте синтаксис!")

        if int(check[0]) > 2 or int(check[0]) < 1:
            return
        if (
            int(check[0]) == 1
            and not profile.business1
            or int(check[0]) == 2
            and not profile.business2
        ):
            return
        business_name = await parse_business_name(msg.from_id, int(check[0]))
        text = f'статистика "{business_name}":\n'
        if int(check[0]) == 1:
            kb = VKKeyboard()
            kb.set_inline(True)
            kb.add_row()
            kb.edit_row(0).add_button("💰 Снять полученную прибыль", payload={'command': f'{env.eenv.prefix}эко бизнес снять 1 все'}, color="positive") 
            pay = profile.business1_works * 50_000 + profile.business1.pay
            text += f"💸 Прибыль: {humanize(pay)}$/час\n"
            if profile.business1_level == 1:
                works = profile.business1.max_works
            elif profile.business1_level == 2:
                works = profile.business1.max_works * 5
            else:
                works = profile.business1.max_works * 5 * 3
            text += f"💼 Рабочих: {profile.business1_works}/{works}\n"
            a = time.time()
            b = time.mktime(profile.business1_run.timetuple())
            res = (a - b) // 3600
            profile.business1_money += (
                Decimal(pay * res) if (pay) * res != profile.last_bus1_pay else 0
            )
            profile.last_bus1_pay = Decimal(pay * res)
            await manager.update(profile)
            text += f"💰 На счёте: {humanize(profile.business1_money)}$\n"
            if profile.business1_works < works:
                text += '⚠ У вас работает недостаточно людей, от этого уменьшена прибыль. Введите "Бизнес нанять 1 [кол-во]"'
            if profile.business1_level < 3:
                text += f'\n✅ Доступно улучшение! ({humanize(profile.business1.up_price * (profile.business1_level + 1) if profile.business1_level > 1 else profile.business1.up_price)}$)\nВведите "Бизнес улучшить 1" для улучшения бизнеса'
            return await env.reply(text, keyboard=kb.dump_keyboard())
        else:
            kb = VKKeyboard()
            kb.set_inline(True)
            kb.add_row()
            kb.edit_row(0).add_button("💰 Снять полученную прибыль", payload={'command': f'{env.eenv.prefix}эко бизнес снять 2 все'}, color="positive") 
            pay = profile.business2_works * 50_000 + profile.business2.pay
            text += f"💸 Прибыль: {humanize(pay)}$/час\n"
            if profile.business2_level == 1:
                works = profile.business2.max_works
            elif profile.business2_level == 2:
                works = profile.business2.max_works * 5
            else:
                works = profile.business2.max_works * 5 * 3
            text += f"💼 Рабочих: {profile.business2_works}/{works}\n"
            a = time.time()
            b = time.mktime(profile.business2_run.timetuple())
            res = (a - b) // 3600
            profile.business2_money += (
                Decimal(pay * res) if (pay) * res != profile.last_bus2_pay else 0
            )
            profile.last_bus2_pay = Decimal(pay * res)
            await manager.update(profile)
            text += f"💰 На счёте: {humanize(profile.business2_money)}$\n"
            if profile.business2_works < works:
                text += '⚠ У вас работает недостаточно людей, от этого уменьшена прибыль. Введите "Бизнес нанять 2 [кол-во]"'
            if profile.business2_level < 3:
                text += f'\n✅ Доступно улучшение! ({humanize(profile.business2.up_price * (profile.business2_level + 1) if profile.business2_level > 1 else profile.business2.up_price)}$)\nВведите "Бизнес улучшить 2" для улучшения бизнеса'
            return await env.reply(text, keyboard=kb.dump_keyboard())


@plugin.on_startswith_text("эко копать")
async def working(msg, ats, env):
    if not env.body or env.body.lower() not in ("железо", "золото", "алмазы"):
        return await env.reply("использование: «эко копать железо/золото/алмазы» 😕")
    kb = VKKeyboard()
    kb.set_inline(True)
    profile = await get_or_create_profile(msg.from_id)
    if profile.last_energy_end and profile.last_energy_end > datetime.datetime.now():
        return await env.reply(
            f"вы сильно устали.\n⚠ Энергия появляется каждые 30 минут!"
        )
    if profile.energy_days == 1:
        profile.energy_days = 9

        profile.last_energy_end = datetime.datetime.now() + datetime.timedelta(
            seconds=1800
        )
    else:
        profile.energy_days -= 1
    pay = random.randint(1, 15)
    if "железо" in env['args']:
        profile.iron += pay
        text = plural_form(pay, ("железо", "железа", "железа"))
        kb.add_row()
        kb.edit_row(0).add_button("📎 Копать ещё", payload={'command': f'{env.eenv.prefix}эко копать железо'}, color="primary")
    elif "золото" in env['args']:
        if not profile.energy_worked > 500:
            return await env.reply(
                "что бы копать золото нужно больше 500 опыта. Копайте железо и увеличивайте свой опыт!"
            )
        profile.gold += pay
        text = plural_form(pay, ("золото", "золота", "золота"))
        kb.add_row()
        kb.edit_row(0).add_button("💰 Копать ещё", payload={'command': f'{env.eenv.prefix}эко копать золото'}, color="primary")
    elif "алмазы" in env['args']:
        if not profile.energy_worked > 1000:
            return await env.reply(
                "что бы копать алмазы нужно больше 1.000 опыта. Копайте железо/золото и увеличивайте свой опыт!"
            )
        profile.diamond += pay
        text = plural_form(pay, ("алмаз", "алмаза", "алмазов"))
        kb.add_row()
        kb.edit_row(0).add_button("💎 Копать ещё", payload={'command': f'{env.eenv.prefix}эко копать алмазы'}, color="primary")
    else:
        return await env.reply("Мы не очень поняли, что вы хотите копать!")

    profile.energy_worked += 1
    await manager.update(profile)
    vk_message = f"+{text}\n💡 Энергия: {profile.energy_days if not profile.last_energy_end > datetime.datetime.now() else 0}, опыт: {profile.energy_worked}\n"
    return await env.reply(vk_message, keyboard=kb.dump_keyboard())
