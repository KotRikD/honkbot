import datetime
import random
import re
import string

from peewee import fn

from database import *
from kutana import Plugin
from utils import *

plugin = Plugin(name="ClanSystem", cmds=[
    {'command': 'клан создать', 'desc': 'Создание клана, стоимость 1 млрд$'},
    {'command': 'клан топ', 'desc': 'Показывает топ кланов'},
    {'command': 'клан переименовать', 'desc': 'Позволяет переименовать клан'},
    {'command': 'клан участники', 'desc': 'Просмотреть список клана'},
    {'command': 'клан пригласить', 'desc': 'Пригласить человека в клан'},
    {'command': 'клан приглашения', 'desc': 'Просмотреть кто приглашал вас в свой клан'},
    {'command': 'клан отклонить', 'desc': 'Отклонить приглашение в клан'},
    {'command': 'клан принять', 'desc': 'Принять приглашение в клан'},
    {'command': 'клан вложить', 'desc': 'Вложить деньги в клан'},
    {'command': 'клан снять', 'desc': 'Снять мани из казны'},
    {'command': 'клан пэйклан', 'desc': 'Выплатить з/п участникам'},
    {'command': 'клан выгнать', 'desc': 'Выгнать человека из клана'},
    {'command': 'клан повысить', 'desc': 'Повысить должность участника клана'},
    {'command': 'клан понизить', 'desc': 'Понизить должность участника клана'},
    {'command': 'клан выйти', 'desc': 'Покинуть клан'},
    {'command': 'клан', 'desc': 'Просмотреть информацию о клане!'}
])


def toFixed(f: float, n=0):
    a, b = str(f).split('.')
    return '{}{}{}'.format(a, b[:n], '0' * (n - len(b)))


def humanize(value):
    return "{:,}".format(round(value)).replace(",", ".")


def text_to_value(value, text):
    value2 = 1000
    if text == 'к' or text == 'k':
        return int(value) * int(value2)
    if text == 'кк' or text == 'kk':
        return int(value) * (int(value2) ** 2)
    if text == 'ккк' or text == 'kkk':
        return int(value) * (int(value2) ** 3)
    if text == 'кккк' or text == 'kkkk':
        return int(value) * (int(value2) ** 4)
    if text == 'ккккк' or text == 'kkkkk':
        return int(value) * (int(value2) ** 5)
    if text == 'кккккк' or text == 'kkkkkk':
        return int(value) * (int(value2) ** 6)
    if text == 'ккккккк' or text == 'kkkkkkk':
        return int(value) * (int(value2) ** 7)
    if text == 'кккккккк' or text == 'kkkkkkkk':
        return int(value) * (int(value2) ** 8)
    return int(value)


def textify_value(value):
    avalue = abs(value)
    if avalue > 1000000000000000000000000000000000000000000000000000000000000000:
        return "Too many Money!"
    if avalue >= 1000000000000000000000000000000000:
        return str(round(value / 1000000000000000000000000000000000, 2)) + " дец."
    if avalue >= 1000000000000000000000000000000:
        return str(round(value / 1000000000000000000000000000000, 2)) + " нон."
    if avalue >= 1000000000000000000000000000:
        return str(round(value / 1000000000000000000000000000, 2)) + " окт."
    if avalue >= 1000000000000000000000000:
        return str(round(value / 1000000000000000000000000, 2)) + " сптл."
    if avalue >= 1000000000000000000000:
        return str(round(value / 1000000000000000000000, 2)) + " скст."
    if avalue >= 1000000000000000000:
        return str(round(value / 1000000000000000000, 2)) + " квнт."
    if avalue >= 1000000000000000:
        return str(round(value / 1000000000000000, 2)) + " квдр."
    if avalue >= 1000000000000:
        return str(round(value / 1000000000000, 2)) + " трлн."
    if avalue >= 1000000000:
        return str(round(value / 1000000000, 2)) + " млрд."
    if avalue >= 1000000:
        return str(round(value / 1000000, 2)) + " млн."
    if avalue >= 100000:
        return str(round(value / 100000)) + "00 тыс."
    if avalue >= 1000:
        return str(round(value / 1000)) + " тыс."
    return str(value)

def digits_recursive(nonneg):
    digits = []
    while nonneg:
        digits += [nonneg % 10]
        nonneg //= 10
    return digits[::-1] or [0]


def num_to_smile(num):
    if num <= 10:
        numbers = {0: '0⃣', 1: '1⃣', 2: '2⃣', 3: '3⃣', 4: '4⃣', 5: '5⃣', 6: '6⃣', 7: '7⃣', 8: '8⃣', 9: '9⃣', 10: '🔟'}
        return numbers[num]
    numbers = {0: '0⃣.', 1: '1⃣', 2: '2⃣', 3: '3⃣', 4: '4⃣', 5: '5⃣', 6: '6⃣', 7: '7⃣', 8: '8⃣', 9: '9⃣', 10: '🔟'}
    digits = digits_recursive(num)
    result = ""
    for i in digits:
        result += numbers[i]
    return result


def parse_rank_name(rank):
    if rank == 1:
        return 'рядовой'
    if rank == 2:
        return 'офицер'
    if rank == 3:
        return 'заместитель'
    if rank == 4:
        return 'основатель'


async def get_or_create_profile(user_id):
    try:
        shopcenters = shopcenter.select()
        job = jobs.select()
        profiles = Profile.select().where(Profile.user_id == user_id)

        profile = list(await manager.prefetch(profiles, shopcenters, job))[0]
    except IndexError:
        profile = await peewee_async.create_object(Profile, user_id=user_id)
    return profile


def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


async def get_clan_info(identify):
    test = Profile.select(fn.SUM(Profile.rg).alias('total'), Profile.user_id).group_by(Profile.rg,
                                                                                       Profile.user_id).where(
        Profile.clan == identify).order_by(fn.SUM(Profile.rg).desc())
    query_result = await manager.execute(test)
    raitings = 0
    members = 0
    for u in query_result:
        raitings += round(int(u.total))
        members += 1
    return raitings, members


async def get_info_for_top(tag):
    test = clan_members.select().where(clan_members.clan_tag == tag, clan_members.is_accepted == 1)
    query_result = await manager.execute(test)
    raitings = 0
    members = 0
    for u in query_result:
        data = await get_or_none(Profile, user_id=u.user_id)
        raitings += round(int(data.rg))
        members += 1
    return raitings, members


@plugin.on_startswith_text('клан создать')
async def create_clan(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if a.clan:
        return await env.reply('вы уже состоите в клане, чтобы покинуть его, введите "клан выйти"')
    if a.money < 1_000_000_000:
        return await env.reply('стоимость создания клана - 1.000.000.000$')
    args = env.body.split()
    if not args or len(args) < 2:
        return await env.reply('использование: <<клан создать [аббревиатура] [название]>>')
    if len(args[0]) < 2 or len(args[0]) > 10:
        return await env.reply('Максимальное значение длины аббревиатуры варьируется от 2 до 10')
    name = ''.join(args[1:])
    if await get_or_none(clans, shortname=args[0]):
        return await env.reply('клан с такой аббревиатурой уже создан.')
    if await get_or_none(clans, name=name):
        return await env.reply('клан с таким названием уже создан.')
    a.money -= 1_000_000_000
    tag = id_generator()
    cm, cr = await manager.get_or_create(clan_members, user_id=msg.from_id, join_date=datetime.datetime.today(), rank=4,
                                         clan_tag=tag)
    await manager.update(cm)
    cl, created = await manager.get_or_create(clans, header_id=msg.from_id, name=name, shortname=args[0], treasury=0,
                                              clan_type=1, tag=tag)
    await manager.update(cl)
    a.clan = cl.id
    await manager.update(a)

    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': 'Статистика клана', 'payload': {'command': f'{env.eenv.prefix}клан'}, 'color': 'primary'},
        ]
    })
    return await env.reply(
        f'клан с аббревиатурой [{args[0]}] и названием "{name}" создан.\nЧтобы узнать всю информацию о клане, введите "клан"', keyboard=kb.dump_keyboard())


@plugin.on_text('клан топ')
async def top_clans(msg, ats, env):
    top = list(await manager.execute(clans.select().where(clans.treasury >= 0).order_by((clans.treasury).desc())))
    data = [{"id": u.header_id, "money": u.treasury, "tag": u.tag, 'name': u.name, 'shortname': u.shortname} for u in
            top]
    mesto = list(z['tag'] for z in data)
    text = "топ-10 кланов по богатству:\n"
    for i in enumerate(data[:10], start=1):
        num = num_to_smile(i[0])
        raitings, members = await get_info_for_top(i[1]['tag'])
        text += f"{num}. @id{i[1]['id']} ({i[1]['name']}) [{i[1]['shortname']}]\nТэг: {i[1]['tag']} | Рейтинг: {textify_value(raitings)}👑 | Участников: {int(members)}/200\n"
    return await env.reply(text)


@plugin.on_startswith_text('клан переименовать')
async def rename_clan(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank >= 3):
        return await env.reply('данная функция доступна со звания заместитель и выше.')
    args = env.body.split()
    if not args or len(args) < 2:
        return await env.reply('использование: "клан переименовать [аббревиатура] [название]"')
    if len(args[0]) < 2 or len(args[0]) > 5:
        return await env.reply('Максимальное значение длины аббревиатуры варьируется от 2 до 5')
    name = ''.join(args[1:])
    if await get_or_none(clans, shortname=args[0]):
        return await env.reply('клан с такой аббревиатурой уже создан.')
    if await get_or_none(clans, name=name):
        return await env.reply('клан с таким названием уже создан.')
    cl, created = await manager.get_or_create(clans, name=clan.name, tag=clan.tag)
    cl.name = name
    cl.shortname = args[0]
    await manager.update(cl)
    await env.request('messages.send', user_id=cl.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) изменил название клана на \"{name} [{args[0]}]\".")
    return await env.reply(f'название вашего клана изменено на "{name} [{args[0]}]"')


@plugin.on_text('клан участники')
async def clan_member(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    top = list(await manager.execute(
        clan_members.select().where(clan_members.clan_tag == clan.tag, clan_members.is_accepted == 1).order_by(
            (clan_members.rank).desc())))
    data = [{"id": u.user_id, "rank": u.rank} for u in top]
    text = f"участники клана {clan.name}:\n"
    for i in enumerate(data, start=1):
        name = await parse_user_name(env, i[1]['id'])
        rank = parse_rank_name(i[1]['rank'])
        text += f"{i[0]}. @id{i[1]['id']} ({name}) [{rank}]\n"
    return await env.reply(text)


@plugin.on_startswith_text('клан пригласить')
async def invite_clan(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank >= 2):
        return await env.reply('данная функция доступна со звания офицер и выше.')
    raitings, members = await get_clan_info(a.clan)
    if members >= 200:
        return await env.reply('достигнуто максимальное количество участников.')
    puid = await parse_user_id(msg, env)
    if not puid:
        return await env.reply('использование: "пригласить [id(vk)]" для приглашения в клан.')
    if await get_or_none(clan_members, clan_tag=clan.tag, user_id=puid[0]):
        return await env.reply('пользователь и так состоит в вашем клане')
    if await get_or_none(clan_invites, whom_id=puid[0], clan_tag=clan.tag):
        return await env.reply('вы уже отправляли приглашение данному пользователю.')
    ci, cr = await manager.get_or_create(clan_invites, whom_id=puid[0], clan_tag=clan.tag)
    await manager.update(ci)
    name = await parse_user_name(env, puid[0])
    await env.request('messages.send', user_id=clan.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) пригласил пользователя @id{puid[0]} ({name})")
    await env.request('messages.send', user_id=puid[0],
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) пригласил вас в клан {clan.name} [{clan.shortname}], чтобы принять, просмотрите приглашения\nИспользование: <<приглашения>>")
    return await env.reply(f'приглашение в клан отправлено игроку {name}')


@plugin.on_text('клан приглашения')
async def invites(msg, ats, env):
    if not await get_or_none(clan_invites, whom_id=msg.from_id):
        return await env.reply('список пуст')
    top = list(await manager.execute(clan_invites.select().where(clan_invites.whom_id == msg.from_id)))
    data = [{"clan_tag": u.clan_tag} for u in top]
    text = "\n"
    for i in enumerate(data, start=1):
        clan = await get_or_none(clans, tag=i[1]['clan_tag'])
        if not clan:
            continue
        name = await parse_user_name(env, clan.header_id)
        raitings, members = await get_info_for_top(i[1]['clan_tag'])
        text += f"{i[0]}. @id{clan.header_id} ({clan.name}) [{clan.shortname}]\nРейтинг: {raitings}👑 | Участников: {members}/200 | Тэг: {i[1]['clan_tag']}\n"
    text += '\nДля принятия инвайта, введите "клан принять [тэг клана]"\nДля отклонения инвайта, введите "клан отклонить [тэг клана]"'
    return await env.reply(text)


@plugin.on_startswith_text('клан отклонить')
async def decline_invite(msg, ats, env):
    if not await get_or_none(clan_invites, whom_id=msg.from_id):
        return await env.reply('вам нечего отклонять')
    if not env.body:
        return await env.reply('использование: "клан отклонить [тэг клана]"')
    if not await get_or_none(clan_invites, whom_id=msg.from_id, clan_tag=env.body.upper()):
        return await env.reply('приглашение в клан с таким идентификатором не найдено')
    await manager.execute(
        clan_invites.delete().where(clan_invites.whom_id == msg.from_id, clan_invites.clan_tag == env.body.upper()))
    return await env.reply('заявка успешно отклонена.')


@plugin.on_startswith_text('клан принять')
async def accept_invite(msg, ats, env):
    if not await get_or_none(clan_invites, whom_id=msg.from_id):
        return await env.reply('вам нечего отклонять')
    if not env.body:
        return await env.reply('использование: "клан принять [тэг клана]"')
    if not await get_or_none(clan_invites, whom_id=msg.from_id, clan_tag=env.body.upper()):
        return await env.reply('приглашение в клан с таким идентификатором не найдено')
    a = await get_or_create_profile(msg.from_id)
    cl, created = await manager.get_or_create(clans, tag=env.body.upper())
    raitings, members = await get_clan_info(cl)
    if members >= 200:
        return await env.reply('в данном клане уже достигнуто максимальное количество участников')
    a.clan = cl.id
    await manager.update(a)
    cm, cr = await manager.get_or_create(clan_members, user_id=msg.from_id, join_date=datetime.datetime.today(), rank=1,
                                         clan_tag=env.body.upper())
    await manager.update(cm)
    await manager.execute(
        clan_invites.delete().where(clan_invites.whom_id == msg.from_id, clan_invites.clan_tag == env.body.upper()))
    await env.request('messages.send', user_id=cl.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) вступил в клан.")
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': 'Статистика клана', 'payload': {'command': f'{env.eenv.prefix}клан'}, 'color': 'primary'},
        ]
    })
    return await env.reply(f'вы вступили в клан {cl.name}.\nЧтобы узнать всю информацию о клане, введите "клан"', keyboard=kb.dump_keyboard())


@plugin.on_startswith_text('клан вложить')
async def add_treasury(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not env.body:
        return await env.reply('использование: "клан вложить [сумма]"')
    if env.body.lower() == "всё" or env.body.lower() == "все":
        amount = a.money
        result = env.body.lower()
    else:
        value = re.findall(r'\d+', env.body.lower())
        text = re.sub(r'[^\w\s]+|[\d]+', r'', env.body.lower()).strip()
        result = text_to_value(value[0], text)
        if int(result) < 1:
            return await env.reply('число должно быть больше 0.')
        if int(a.money) < result:
            return await env.reply("на вашем счете недостаточно средств.")

    a.money -= result
    cl, cr = await manager.get_or_create(clans, tag=clan.tag)
    cl.treasury += result
    await manager.update(cl)
    await manager.update(a)
    await env.request('messages.send', user_id=cl.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) внес в казну клана {textify_value(result)}$")
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': 'Вложить столько же', 'payload': {'command': f'{env.eenv.prefix}клан вложить {result}'}, 'color': 'primary'},
        ]
    })
    return await env.reply(f'вы внесли в казну клана +{textify_value(result)} $', keyboard=kb.dump_keyboard())


@plugin.on_startswith_text('клан снять')
async def minus_treasury(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank == 4):
        return await env.reply('данная функция доступна только основателю')
    cl, created = await manager.get_or_create(clans, name=clan.name, tag=clan.tag)
    if not env.body:
        return await env.reply('использование: "клан снять [сумма]"')
    if env.body.lower() == "всё" or env.body.lower() == "все":
        amount = a.money
        result = env.body.lower()
    else:
        value = re.findall(r'\d+', env.body.lower())
        text = re.sub(r'[^\w\s]+|[\d]+', r'', env.body.lower()).strip()
        result = text_to_value(value[0], text)
        if int(result) < 1:
            return await env.reply('число должно быть больше 0.')
        if int(result) > cl.treasury:
            return await env.reply("В клановой казне нету столько!")

    a.money += result
    cl.treasury -= result
    await manager.update(cl)
    await manager.update(a)
    return await env.reply(f'вы сняли с казны клана -{textify_value(result)} $')


@plugin.on_startswith_text('клан пэйклан')
async def pay_clan_members(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank == 4):
        return await env.reply('данная функция доступна только основателю')
    cl, created = await manager.get_or_create(clans, name=clan.name, tag=clan.tag)
    if not env.body:
        return await env.reply('использование: "клан пэйклан [сумма]"')
    if env.body.lower() == "всё" or env.body.lower() == "все":
        amount = a.money
        result = env.body.lower()
    else:
        value = re.findall(r'\d+', env.body.lower())
        text = re.sub(r'[^\w\s]+|[\d]+', r'', env.body.lower()).strip()
        result = text_to_value(value[0], text)
    if int(result) < 1:
        return await env.reply('число должно быть больше 0.')
    raitings, members = await get_info_for_top(clan.tag)
    if int(result) * int(members) > cl.treasury:
        return await env.reply(
            f'в казне клана недостаточно средств (не хватает {textify_value(int(result) * int(members) - cl.treasury)}\nУчтите, что при выплате богатства с казны кланов, деньги выдаются каждому участнику в размере указанной суммы.')
    top = list(await manager.execute(
        clan_members.select().where(clan_members.clan_tag == clan.tag, clan_members.is_accepted == 1).order_by(
            (clan_members.rank).desc())))
    data = [{"id": u.user_id} for u in top]
    text = f"участники клана {clan.name}:\n"
    for i in enumerate(data, start=1):
        profile = await get_or_create_profile(i[1]['id'])
        profile.money += int(result)
        await manager.update(profile)
    cl.treasury -= int(result) * int(members)
    await manager.update(cl)
    text = f'всем участникам клана выплачено {textify_value(int(result))} $'
    return await env.reply(text)


@plugin.on_startswith_text('клан выгнать')
async def kick_member(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank >= 3):
        return await env.reply('данная функция доступна со звания заместитель и выше.')    
    puid = await parse_user_id(msg, env)
    if not puid:
        return await env.reply('использование: "клан выгнать [id(vk)]" для исключения из клана.')
    if not await get_or_none(clan_members, clan_tag=clan.tag, user_id=puid[0]):
        return await env.reply('пользователь не состоит в вашем клане')
    
    kicker = await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id)
    kicked = await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == puid[0])
    if kicked.rank >= kicker.rank:
        return await env.reply("ваши полномочия не позволяют кикнуть этого пользователя ;d")

    user = await get_or_create_profile(puid[0])
    user.clan = None
    await manager.update(user)
    await manager.execute(
        clan_members.delete().where(clan_members.user_id == puid[0], clan_members.clan_tag == clan.tag))
    name = await parse_user_name(env, puid[0])
    await env.request('messages.send', user_id=clan.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) исключил пользователя @id{puid[0]} ({name})")
    return await env.reply(f'игрок {name} исключен с клана.')


@plugin.on_startswith_text('клан повысить')
async def plus_rank(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank >= 3):
        return await env.reply('данная функция доступна со звания заместитель и выше.')
    puid = await parse_user_id(msg, env)
    if not puid:
        return await env.reply('использование: "клан повысить [id(vk)]" для повышения звания.')
    if not await get_or_none(clan_members, clan_tag=clan.tag, user_id=puid[0]):
        return await env.reply('пользователь не состоит в вашем клане')
    cm, cr = await manager.get_or_create(clan_members, user_id=puid[0], clan_tag=clan.tag)
    if cm.rank == 2 and await get_or_none(clan_members, clan_members.clan_tag == clan.tag,
                                          clan_members.user_id == msg.from_id, clan_members.rank == 3):
        return await env.reply('Вы не можете больше повышать ранг.')
    if cm.rank < 3:
        cm.rank += 1
    else:
        return await env.reply('у пользователя максимальный ранг.')
    await manager.update(cm)
    name = await parse_user_name(env, puid[0])
    await env.request('messages.send', user_id=clan.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) повысил пользователя @id{puid[0]} ({name}) до звания [{parse_rank_name(cm.rank)}]")
    return await env.reply(f'Игрок {name} повышен до звания {parse_rank_name(cm.rank)}')


@plugin.on_startswith_text('клан понизить')
async def plus_rank(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if not await get_or_none(clan_members, clan_members.clan_tag == clan.tag, clan_members.user_id == msg.from_id,
                             clan_members.rank >= 3):
        return await env.reply('данная функция доступна со звания заместитель и выше.')
    puid = await parse_user_id(msg, env)
    if not puid:
        return await env.reply('использование: "клан понизить [id(vk)]" для понижения звания.')
    if not await get_or_none(clan_members, clan_tag=clan.tag, user_id=puid[0]):
        return await env.reply('пользователь не состоит в вашем клане')
    cm, cr = await manager.get_or_create(clan_members, user_id=puid[0], clan_tag=clan.tag)
    if cm.rank >= 3 and await get_or_none(clan_members, clan_members.clan_tag == clan.tag,
                                          clan_members.user_id == msg.from_id, clan_members.rank == 3):
        return await env.reply('Вы не можете понизить данного пользователя')
    if cm.rank > 1:
        cm.rank -= 1
    else:
        return await env.reply('у пользователя минимальный ранг.')
    await manager.update(cm)
    name = await parse_user_name(env, puid[0])
    await env.request('messages.send', user_id=clan.header_id,
                      message=f"Пользователь @id{msg.from_id} (id{msg.from_id}) понизил пользователя @id{puid[0]} ({name}) до звания [{parse_rank_name(cm.rank)}]")
    return await env.reply(f'Игрок {name} понижен до звания {parse_rank_name(cm.rank)}')


@plugin.on_text('клан выйти')
async def leave_clan(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    if await get_or_none(clan_members, user_id=msg.from_id, rank=4):
        await manager.execute(clan_invites.delete().where(clan_invites.clan_tag == clan.tag))
        await manager.execute(clans.delete().where(clans.header_id == msg.from_id))
        a.clan = None
        await env.reply('Ваш клан был удален, т.к лидер покинул его.')
    else:
        await manager.execute(
            clan_members.delete().where(clan_members.user_id == msg.from_id, clan_members.clan_tag == clan.tag))
        a.clan = None
        await env.reply('вы покинули клан.')
    return await manager.update(a)


@plugin.on_text('клан')
async def clan_info(msg, ats, env):
    a = await get_or_create_profile(msg.from_id)
    if not a.clan:
        return await env.reply(
            'Вступите в какой-нибудь клан, чтобы просмотреть его статистику.\nВступить в клан можно с помощью приглашений')
    clan = await get_or_none(clans, id=a.clan)
    header = await parse_user_name(env, clan.header_id)
    raitings, members = await get_clan_info(clan)
    vk_message = f'информация о клане [{clan.name} ({clan.shortname})]:\n🆔Клан-тэг: {clan.tag}\n👨‍💻️Основатель: @id{clan.header_id} ({header})\n💰Богатство: {textify_value(round(clan.treasury))}\n👑Рейтинг: {humanize(raitings)}\n👔Участников: {members}/200\n💿Дата основания: {clan.register_date}\n'
    kb = VKKeyboard()
    kb.set_inline(True)
    kb.add_row()
    kb.edit_row(0).add_button("🔝 Топ кланов", payload={'command': f'{env.eenv.prefix}клан топ'}, color="primary")
    kb.add_row()
    kb.edit_row(1).add_button("👨‍💻️ Участники клана", payload={'command': f'{env.eenv.prefix}клан участники'}, color="positive")
    #kb.add_row()
    #kb.edit_row(2).add_button("🙎 Выйти из клана", payload={'command': f'{env.eenv.prefix}клан выйти'}, color="negative")
    return await env.reply(vk_message, keyboard=kb.dump_keyboard())
