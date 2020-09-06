from kutana import Plugin
from utils import edict, ddict, priviligeshelper, VKKeyboard
from utils.static_text import need_vip
import utils.logs as Logs
import random
import base64

from database import *

plugin = Plugin(name="Промокды ептя", cmds=[
    {'command': 'промокод б создать', 'desc': 'Создаёт промокод для конкретной беседы (5 штук в день от 5кк до 10кк)',
     'vip': True},
    {'command': 'промокод лист', 'desc': 'Просмотреть список ваших промокодов'},
    {'command': 'промокод активировать <промокод>', 'desc': 'Активировать промокод'},
    {'command': 'промокод создать <кол-во> <сумма за активацию>', 'desc': 'Создаёт промокоды', 'cheat': True},
    {'command': 'промокод удалить <название>', 'desc': 'Удаление промокода', 'cheat': True}
])

def humanize(value):
    return "{:,}".format(round(value)).replace(",", ".")

def secure_promo(text):
    replacement = text[:-7]
    mask = ""
    for x in replacement:
        mask += "*"
    final = text.replace(replacement, mask)
    return final


def generate_random_name(count=20):
    alphabet = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    random.shuffle(alphabet)
    return f"{''.join(random.sample(alphabet, count))}"


async def create_model(env):
    promocode = dict()
    promocode['data'] = {}
    await env.eenv.dbredis.set(f"honoka:promocodes", await edict(promocode))
    return promocode


async def get_or_create_profile(user_id):
    try:
        shopcenters = shopcenter.select()
        job = jobs.select()
        profiles = Profile.select().where(Profile.user_id == user_id)

        profile = list(await manager.prefetch(profiles, shopcenters, job))[0]
    except IndexError:
        profile = await peewee_async.create_object(Profile, user_id=user_id)
    return profile


@plugin.on_startswith_text("промокод лист")
async def promocode_list(message, attachments, env):
    data = await ddict(await env.eenv.dbredis.get(f"honoka:promocodes"))
    if not data:
        data = await create_model(env)

    result = "На данный момент у вас есть вот такие промокоды:\n\n"
    yours = []
    for x in data['data']:
        codennn = x
        x = data['data'][x]
        if int(x['creator']) == message.from_id:
            yours.append(
                f"{codennn if not env.eenv.is_multichat else secure_promo(codennn) } - {humanize(x['summ'])}$ { 'активируемый лишь в беседе' if x.get('conv_promo', None) else 'Чит-промокод' } {x['active_limit']} активации\n")

    if len(yours) < 1:
        return await env.reply("У вас нету промокодов ;(")

    for x in yours:
        result += x

    result += '\nЕсли вы хотите посмотреть коды напишите боту в лс!(сделано для безопасности кодов)' if env.eenv.is_multichat else '\nДля активации промокода дайте один из этих кодов в беседу'
    return await env.reply(result)


limited = {}
@plugin.on_startswith_text("промокод б создать")
async def promocode_gen(message, attachments, env):
    if not env.eenv.is_multichat:
        return await env.reply("эта команда должна быть выполнена в беседе")

    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_VIP > 0):
        return await env.reply(need_vip)

    data = await ddict(await env.eenv.dbredis.get(f"honoka:promocodes"))
    if message.from_id in limited:
        if limited[message.from_id]['used'] >= 1:
            return await env.reply("вы не можете пока, создавать больше")
        limited[message.from_id]['used'] += 1
    else:
        limited[message.from_id] = {}
        limited[message.from_id]['used'] = 1

    if not data:
        ab = await create_model(env)
        data = ab

    code_name = generate_random_name()
    code = generate_random_name(10)
    data['data'][code] = dict(
        name=code_name,
        summ=random.randint(1000000, 2000000),
        conv_promo=True,
        conv=message.peer_id,
        active_limit=5,
        creator=message.from_id,
        activated=[]
    )

    await env.eenv.dbredis.set(f"honoka:promocodes", await edict(data))
    return await env.reply("Промокод на 5 активаций был успешно создан, его можно посмотреть в\n!промокод лист")


@plugin.on_startswith_text("промокод активировать")
async def activate_promo(message, attachments, env):
    if not env['args']:
        return await env.reply("пожалуйста, введите промокод!")

    data = await ddict(await env.eenv.dbredis.get(f"honoka:promocodes"))
    if not data:
        data = await create_model(env)

    if not env['args'][0] in data['data']:
        return await env.reply("Промокод не найден!")

    promo_data = data['data'][env['args'][0]]

    if promo_data.get("conv_promo", False):
        if not promo_data['conv'] == message.peer_id:
            return await env.reply(
                f"Этот промокод создан для определённой беседы!\nО этой беседе можно спросить у [id{promo_data['creator']}|создателя промокода]")

    if message.from_id in promo_data['activated']:
        return await env.reply("Ты уже активировал этот промокод!")
    else:
        promo_data['activated'].append(message.from_id)

    profile = await get_or_create_profile(message.from_id)
    promo_data['active_limit'] -= 1
    if promo_data['active_limit'] < 1:
        del(data['data'][env['args'][0]])
    else:
        data['data'][env['args'][0]] = promo_data

    profile.money += promo_data['summ']
    await manager.update(profile)
    await env.eenv.dbredis.set(f"honoka:promocodes", await edict(data))
    return await env.reply("Поздравляем вы активировали промокод:\n"
                           f"\nНазвание: {promo_data['name']}"
                           f"\nСумма промокода: {humanize(promo_data['summ'])}$\n"
                           f"\nКоличество активаций: осталось {promo_data['active_limit']} раз")


@plugin.on_startswith_text("промокод создать")
async def admin_create(message, attachments, env):
    if not await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN>0:
        return await env.reply("Я тебя не знаю! Бака еро!")

    if not env['args'] or len(env['args']) < 2 or not env['args'][0].isdigit() or not env['args'][1].isdigit():
        return await env.reply("Вы забыли ввести какой-то аргумент")

    data = await ddict(await env.eenv.dbredis.get(f"honoka:promocodes"))
    if not data:
        data = await create_model(env)

    if int(env['args'][1]) >= 10_000_000_000 or int(env['args'][0]) >= 2000:
        return await env.reply("Слишком большая сумма!") if int(env['args'][1]) >= 10_000_000_000 else await env.reply("Слишком много активаций!")

    code_name = generate_random_name()
    code = generate_random_name(10)
    data['data'][code] = dict(
        name=code_name,
        summ=int(env['args'][1]),
        active_limit=int(env['args'][0]),
        creator=message.from_id,
        activated=[]
    )
    
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {
                'text': 'Написать промокод',
                'payload': {
                    'command': f'{env.eenv.prefix}промокод ласткопи'
                },
                'color': 'positive'
            }
        ]
        
    })
    
    await Logs.create_log(env, message.from_id, 0, 11, f"Создал чит-промокод на сумму {humanize(int(env['args'][1]))}$")

    await env.eenv.dbredis.set(f"honoka:promocodes", await edict(data))
    return await env.reply(
        f"Промокод на {env['args'][0]} активаций был успешно создан, его можно посмотреть в\n!промокод лист",
        keyboard=kb.dump_keyboard())

@plugin.on_startswith_text("промокод ласткопи")
async def copy_code(message, attachments, env):
    data = await ddict(await env.eenv.dbredis.get(f"honoka:promocodes"))
    if not data:
        data = await create_model(env)

    result = "На данный момент у вас есть вот такие промокоды:\n\n"
    yours = []
    for x in data['data']:
        code = x
        x = data['data'][x]
        if int(x['creator']) == message.from_id:
            yours.append(code)
    
    if not yours:
        return await env.reply("У вас нет промокодов")
    
    await env.request('messages.send', message=yours[-1], peer_id=message.peer_id, random_id=0)
    return "DONE"

@plugin.on_startswith_text("промокод удалить")
async def del_promo(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if privs & priviligeshelper.USER_ADMIN > 0 or privs & priviligeshelper.USER_MODERATOR > 0:
        pass
    else:
        return await env.reply("Я тебя не знаю! Бака еро!")

    if not env['args']:
        return env.reply("Промокод не был введён!")

    data = await ddict(await env.eenv.dbredis.get(f"honoka:promocodes"))
    if not data:
        data = await create_model(env)

    if not env['args'][0] in data['data']:
        return await env.reply("Промокод не найден!")

    await Logs.create_log(env, message.from_id, 0, 12, f"Удалил промокод {env['args'][0]}")
    del(data['data'][env['args'][0]])
    await env.eenv.dbredis.set(f"honoka:promocodes", await edict(data))
    return await env.reply("Промокод был удалён!")
