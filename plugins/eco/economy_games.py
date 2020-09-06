from kutana import Plugin
from database import *
import random
from random import random as rd
from utils import ddict, edict, priviligeshelper
from utils.static_text import need_vip
from utils import VKKeyboard
import utils.logs as Logs

plugin = Plugin(name="Economy-Games", cmds=[
                                            {'command': 'double [r|g|b] [ставка]', 'desc': 'ну тип рулетка'},
                                            {'command': 'казино [ставка]', 'desc': 'сыграем?'},
                                            {'command': 'бин [вверх/вниз] [ставка]', 'desc': 'бинарные опционы'},
                                            {'command': 'ловушка [ставка]', 'desc': 'попробуй достать сокровища!'},
                                            {'command': 'эко бонус', 'desc': 'получитс бонус от бота', 'vip': True},
                                            {'command': 'игра [ставка]', 'desc': 'просто игрулька)'},
                                            {'command': 'дснять', 'desc': 'снять мани, за то что писал!'}])


# 31give
# 32cazino
# 33double
def humanize(value):
    return "{:,}".format(round(value)).replace(",", ".")

async def get_or_create_profile(user_id):
    try:
        shopcenters = shopcenter.select()
        job = jobs.select()
        profiles = Profile.select().where(Profile.user_id == user_id)

        profile = list(await manager.prefetch(profiles, shopcenters, job))[0]
    except IndexError:
        profile = await peewee_async.create_object(Profile, user_id=user_id)
    return profile


temp_data = []

@plugin.on_text("эко бонус")
async def bonus(msg, ats, env):
    if env.eenv.is_multichat:
        return await env.reply("используйте данную команду в личных сообщениях группы")

    if not await priviligeshelper.getUserPriviliges(env, msg.from_id)&priviligeshelper.USER_VIP>0:
        return await env.reply("Ты не вип!")

    if msg.from_id in temp_data:
        return await env.reply("Вы уже получали свой бонус!")

    temp_data.append(msg.from_id)

    profile = await get_or_create_profile(msg.from_id)
    bonus = random.randint(1, 3)
    if bonus == 1:
        money = random.randint(1000, 1_000_000)
        text = f"вы выиграли {humanize(money)}$"
        profile.money += Decimal(money)
    if bonus == 2:
        bitcoin = random.randint(1, 25)
        text = f"вы выиграли {bitcoin}Ƀ"
        profile.btc += int(bitcoin)
    if bonus == 3:
        shopcenters = list(
            await manager.execute(
                shopcenter.select()
                .where(shopcenter.slot != "other", shopcenter.price < 1_000_000)
                .order_by(shopcenter.price)
            )
        )
        random.shuffle(shopcenters)
        prize = random.choice(shopcenters)
        text = f"вы выиграли {prize.name}"
        if prize.slot == "car":
            if profile.car:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.car = prize
        elif prize.slot == "airplane":
            if profile.airplane:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.airplane = prize
        elif prize.slot == "helicopter":
            if profile.helicopter:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.helicopter = prize
        elif prize.slot == "house":
            if profile.house:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.house = prize
        elif prize.slot == "apartment":
            if profile.apartment:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.apartment = prize
        elif prize.slot == "mobile":
            if profile.mobile:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.mobile = prize
        elif prize.slot == "yacht":
            if profile.yacht:
                profile.money += prize.price
                text += f"\nУ вас есть уже это имущество, на ваш счет зачислено {humanize(prize.price)}$"
            else:
                profile.yacht = prize
    await manager.update(profile)
    return await env.reply(text)


@plugin.on_startswith_text("double")
async def on_message(message, attachments, env):
    profile = await get_or_create_profile(message.from_id)
    if not env['args'] or len(env['args']) < 2:
        return await env.reply("Вы что-то напутали")

    if not env['args'][1].isdigit():
        return await env.reply("Ставка должна быть числовой")

    color = env['args'][0]
    if not color.lower() in ("r", "g", "b"):
        return await env.reply("Аргументы: [r|g|b] [ставка]")

    balance = profile.money

    rate = int(env['args'][1])
    color = color.lower()

    if rate < 1000:
        return await env.reply("Мин. ставка 1000$")

    if color == "r" and balance < rate * 2 or \
                            color == "b" and balance < rate * 2:
        return await env.reply(
            f"Подожди подожди полегче у тебя баланса меньше чем при умножении {rate} на 2 = {rate*2}$.")

    if color == "g" and balance < rate * 4:
        return await env.reply(
            f"Подожди подожди полегче у тебя баланса меньше чем при умножении {rate} на 4 = {rate*4}$.")

    if balance <= 0:
        return await env.reply("Не хватает денег!")

    keyboard = VKKeyboard()
    keyboard.set_inline(True)
    keyboard.add_row()
    keyboard.edit_row(0).add_button('Таже сумма на 🔴', payload={'command': f'{env.eenv.prefix}double r {rate}'}, color="negative")
    keyboard.add_row()
    keyboard.edit_row(1).add_button('Таже сумма на ⚫', payload={'command': f'{env.eenv.prefix}double b {rate}'}, color="primary")
    keyboard.add_row()
    keyboard.edit_row(2).add_button('Таже сумма на ✅', payload={'command': f'{env.eenv.prefix}double g {rate}'}, color="positive")

    rInt = random.randint(1, 11)

    if rInt == 1 and color == "r" or \
                            rInt == 3 and color == "r" or \
                            rInt == 5 and color == "r" or \
                            rInt == 7 and color == "r" or \
                            rInt == 10 and color == "r":

        profile.money += rate * 2
        await manager.update(profile)
        return await env.reply(f"🔴 Красный!\n🏆 Вы выиграли {rate*2}$.\n💰 Ваш баланс: {balance+rate*2}$.", keyboard=keyboard.dump_keyboard())
    elif rInt == 2 and color == "b" or \
                            rInt == 4 and color == "b" or \
                            rInt == 6 and color == "b" or \
                            rInt == 8 and color == "b" or \
                            rInt == 11 and color == "b":

        profile.money += rate * 2
        await manager.update(profile)
        return await env.reply(f"⚫ Черный!\n🏆 Вы выиграли {rate*2}$.\n💰 Ваш баланс: {balance+rate*2}$.", keyboard=keyboard.dump_keyboard())
    elif rInt == 9 and color == "g":
        profile.money += rate * 4
        await manager.update(profile)
        return await env.reply(f"✅ Зеленый!\n🏆 Вы выиграли {rate*4}$.\n💰 Ваш баланс: {balance+rate*4}$.", keyboard=keyboard.dump_keyboard())
    else:
        if rInt == 1 or rInt == 3 or rInt == 5 or rInt == 7 or rInt == 10:
            if profile.money - rate * 2 <= 0:
                profile.money = 0
                balance = 0
            else:
                profile.money -= rate * 2
                balance -= rate * 2
            await env.reply(f"🔴 Красный!\n😭 Вы проиграли {rate*2}$.\n💰 Ваш баланс: {balance}$.", keyboard=keyboard.dump_keyboard())
        elif rInt == 2 or rInt == 4 or rInt == 6 or rInt == 8 or rInt == 11:
            if profile.money - rate * 2 <= 0:
                profile.money = 0
                balance = 0
            else:
                profile.money -= rate * 2
                balance -= rate * 2
            await env.reply(f"⚫ Черный!\n😭 Вы проиграли {rate*2}$.\n💰 Ваш баланс: {balance}$.", keyboard=keyboard.dump_keyboard())
        elif rInt == 9:
            if profile.money - rate * 4 <= 0:
                profile.money = 0
                balance = 0
            else:
                profile.money -= rate * 4
                balance -= rate * 4
            await env.reply(f"✅ Зеленый!\n😭 Вы проиграли {rate*4}$.\n💰 Ваш баланс: {balance}$.", keyboard=keyboard.dump_keyboard())

        await manager.update(profile)
        return "DONE"


@plugin.on_startswith_text("казино")
async def on_message(message, attachments, env):
    if not env['args'] or not env['args'][0].isdigit():
        return await env.reply("Что-то напутал")

    profile = await get_or_create_profile(message.from_id)
    amount = int(env['args'][0])
    keyboard = VKKeyboard()
    keyboard.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': 'Крутануть ещё раз', 'payload': {'command': f'{env.eenv.prefix}казино {amount}' }, 'color': 'primary'}
        ]
    })

    if amount == 777:
        return await env.reply("Ты слил бабло, вухахахахахах.", attachment="video-99505016_456242816", keyboard=keyboard.dump_keyboard())

    if amount < 100:
        return await env.reply("Сумма ставки должна быть равна хотябы 100$")

    if profile.money < int(amount):
        return await env.reply("Сумма превышает ваш баланс!")

    r1 = random.randint(0, 2)
    r2 = random.randint(0, 2)
    r3 = random.randint(0, 2)
    emodjis = ["🍌", "🍓", "🍒"]
    if not r1 == r2 == r3:
        profile.money -= int(amount)
        await manager.update(profile)
        await env.reply(f"🐉 Казино \"Анатолич, крути барабан\" 🐉\n"
                        f"🎰 Вы потеряли: {int(amount)} руб.\n\n"
                        f"🎲 Ваша комбинация: {emodjis[r1]} | {emodjis[r2]} | {emodjis[r3]}\n"
                        f"💳 Ваш баланс: {profile.money} руб.", keyboard=keyboard.dump_keyboard())
    else:
        koef = 0
        if r1 == 0:
            profile.money += int(int(amount) * 1.5)
            koef = 1.5
        elif r1 == 1:
            profile.money += int(int(amount) * 2)
            koef = 2
        elif r1 == 2:
            profile.money += int(int(amount) * 2.5)
            koef = 2.5

        await env.reply(f"🐉| Казино \"Анатолич, крути барабан\" 🐉\n"
                        f"🎰| Вы получили: {int(amount)*koef} руб.\n\n"
                        f"🎲| Ваша комбинация: {emodjis[r1]} | {emodjis[r2]} | {emodjis[r3]}\n"
                        f"💳| Ваш баланс: {profile.money} руб.", keyboard=keyboard.dump_keyboard())
        await manager.update(profile)


@plugin.on_startswith_text("эко выдать")
async def on_message(message, attachments, env):
    if not env['args'] or len(env['args']) < 2 or not env['args'][1].isdigit():
        return await env.reply("Что-то напутал")
    if not await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN>0:
        return await env.reply("Эта команда доступна лишь админам")

    profile = await get_or_create_profile(message.from_id)

    amount = int(env['args'][1])
    if amount>100_000_000_000_000:
        return await env.reply("Слишком много!")

    user_idd = env['args'][0]
    try:
        c, cr = await manager.get_or_create(Profile, id=int(user_idd))
    except:
        return await env.reply("Пользователяя с данным ID не существует")

    await Logs.create_log(env, message.from_id, c.user_id, 2, f"Выдал пользователю {user_idd} сумму в размере {amount}$.")

    c.money += int(amount)
    await manager.update(c)
    return await env.reply("Денюжка была выдана!")


@plugin.on_startswith_text("бин")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply(f'[Подсказка] !бин вверх/вниз ставка')

    if len(env['args']) < 2 or not env['args'][1].isdigit():
        return await env.reply(
            f'🔥 ➣ Вы не указали ставку\n [Подсказка] ➣ бин вверх/вниз ставка');

    if len(env['args']) < 1:
        return await env.reply(
            f'🔥 ➣ Вы не указали вверх/вниз\n [Подсказка] ➣ бин вверх/вниз ставка');

    amount = int(env['args'][1])

    keyboard = VKKeyboard()
    keyboard.set_inline(True)
    keyboard.add_row()
    keyboard.edit_row(0).add_button('🔺 Ещё раз вверх', payload={'command': f'{env.eenv.prefix}бин вверх {amount}'}, color="positive")
    keyboard.add_row()
    keyboard.edit_row(1).add_button('🔻 Ещё раз вниз', payload={'command': f'{env.eenv.prefix}бин вниз {amount}'}, color="negative")

    profile = await get_or_create_profile(message.from_id)
    if amount > profile.money or amount < 1000:
        return await env.reply(
            f'Ставка не может быть меньше 1000 💰' if amount < 1000 else f'Ставка не может превышать баланс')
    if amount > 10000000:
        return await env.reply("Ставка не может быть больше 10000000$")

    a = int(rd()*10)
    if env['args'][0].lower() == 'вверх' and a < 3:
            bin = random.randint(15, 40)
            win = amount*2
            profile.money += win
            await manager.update(profile)
            return await env.reply(f'''
                                    📊 ➣ Binary Option
                                    📈 ➣ Курс акции вырос на — {bin} %
                                    💳 ➣ Вы выиграли: {win}💰.
                                    💰 ➣ Ваш баланс: {profile.money}💰''', keyboard=keyboard.dump_keyboard())

    elif env['args'][0].lower() == 'вниз' and a < 3:
        bin = random.randint(15, 40)
        win = amount*2
        profile.money += win
        await manager.update(profile)
        return await env.reply(f'''
                                📊 ➣ Binary Option
                                📉 ➣ Курс акции упал на — {bin} %
                                💳 ➣ Вы выиграли: {win}💰.
                                💰 ➣ Ваш баланс: {profile.money}💰''', keyboard=keyboard.dump_keyboard())
    else:
        bin = random.randint(15, 40)
        lose = int(amount)
        profile.money -= lose
        await manager.update(profile)
        return await env.reply(f'''
                                📊 ➣ Binary Option
                                📈 ➣ Курс акции { "упал" if env['args'][0].lower() == "вверх" else "вырос" } на — {bin} %
                                💳 ➣ Вы проиграли: {lose}💰.
                                💰 ➣ Ваш баланс: {profile.money}💰''', keyboard=keyboard.dump_keyboard())



@plugin.on_startswith_text("ловушка")
async def on_message(message, attachments, env):
    if len(env['args']) < 1 or not env['args'][0].isdigit():
        return await env.reply(f'😈 ➣ Укажите ставку')

    profile = await get_or_create_profile(message.from_id)
    text = int(env['args'][0])
    if text > profile.money or text <= 0:
        return await env.reply(
            f'Ставка не может быть меньше 0 или равна 0' if text <= 0 else f'Ставка не может превышать баланс')

    keyboard = VKKeyboard()
    keyboard.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '👉 Ещё раз 👈', 'payload': {'command': f'{env.eenv.prefix}ловушка {text}'}, 'color': 'positive'}
        ]
    })
    if random.randint(1, 100) > 80:
        win = text * 2
        profile.money += win
        a_some_rare = random.choice(['💶', '💍', '💎', '💰', '🎁', '⚽'])
        await manager.update(profile)
        return await env.reply(
            f'😈 ➣ Вы засунули руку в коробку...\n▪ ➣ Из нее вы достали -> [{a_some_rare}] \n💴 ➣ Вы выиграли:  {win}💰\n💰 ➣ Баланс: {profile.money}', keyboard=keyboard.dump_keyboard())
    else:
        win = text
        profile.money -= win
        somebad = random.choice(['ловушкой', 'мышеловкой', 'капканом'])
        await manager.update(profile)
        return await env.reply(
            f'👉 ➣ Вы засунули руку в коробку...\n💀 ➣ Неудача... Вы повредили руку -> [{somebad}] \n💴 ➣ Вы проиграли:  {win}💰\n💰 ➣ Баланс: {profile.money}', keyboard=keyboard.dump_keyboard())

@plugin.on_startswith_text("игра")
async def game(message, attachments, env):
    if not env['args'] or not env['args'][0].isdigit():
        return await env.reply("На какую сумму хотите сыграть?")

    profile = await get_or_create_profile(message.from_id)
    rate = int(env['args'][0])
    if rate > profile.money:
        return await env.reply("Ставка не может превышать ваш баланс!")

    if rate < 2000:
        return await env.reply("Ставка должна быть минимум 2000$")

    keyboard = VKKeyboard()
    keyboard.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '👉 Ещё раз 👈', 'payload': {'command': f'{env.eenv.prefix}игра {rate}'}, 'color': 'positive'}
        ]
    })
    m = random.randint(1, 100)
    if m < 75:
        profile.money-=rate
        await manager.update(profile)
        return await env.reply(f"Выпало число {m}, ваша ставка сгорела!", keyboard=keyboard.dump_keyboard())

    if m > 75 and m <= 89:
        profile.money+=rate*2
        await manager.update(profile)
        return await env.reply(f"Выпло число {m}, ваша ставка удвоилась!", keyboard=keyboard.dump_keyboard())

    if m >= 90 and m <= 99:
        profile.money+=rate*3
        await manager.update(profile)
        return await env.reply(f"Выпло число {m}, ваша ставка утроилась!", keyboard=keyboard.dump_keyboard())

    if m == 100:
        profile.money+=rate*5
        await manager.update(profile)
        return await env.reply("Выпало число 100, невероятно, но ваша ставка вырасла в 5 раз!", keyboard=keyboard.dump_keyboard())


@plugin.on_startswith_text("дснять")
async def dcheckout(message, attachments, env):
    profile = await get_or_create_profile(message.from_id)
    tempuserstats = await ddict(await env.eenv.dbredis.get(f"honoka:cached_money:{message.from_id}"))

    if not tempuserstats:
        tempuserstats = dict(
            messages=0,
            money=0
        )

    if tempuserstats['money']<=0:
        return await env.reply("В данный момент в ваших накоплениях с сообщений 0$. Попробуйте что-нибудь написать и приходите снова.")

    profile.money+=tempuserstats['money']
    await manager.update(profile)
    await env.reply(
        "Поздравляем!\n"
        f"Вы сняли: {tempuserstats['money']}$\n"
        f"За {tempuserstats['messages']} сообщений"
    )
    tempuserstats['messages']=0
    tempuserstats['money']=0
    await env.eenv.dbredis.set(f"honoka:cached_money:{message.from_id}", await edict(tempuserstats))
