from kutana import Plugin
from database import *
from utils import xputils, edict, priviligeshelper, clear_prefix, VKKeyboard
from utils import levels as levelarr

plugin = Plugin(name="Да тут тип XPSystem",
                cmds=[{'command': 'rank беседы', 'desc': 'узнать статистику о топ-пользователях беседы'},
                      {'command': 'setprefix <префикс>', 'desc': 'устанаваливает префикс от 6 лвла. Випы могут установить когда захотят!'}])

def humanize(value):
    return "{:,}".format(round(value)).replace(",", ".")

@plugin.on_startswith_text("setprefix")
async def on_message(message, attachments, env):
    usera = await get_or_none(PxUser, iduser=str(message.from_id))
    if usera:
        if await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
            pass
        elif usera.rank < len(levelarr):
            await env.reply(f"Этой командой могут пользоваться пользователи от {len(levelarr)} уровня.")
            return "DONE"

        if not env['args']:
            await env.reply('А какой префикс тебе ставить?')
            return "DONE"

        prefix = message.text.replace(f"setprefix ", "")
        if len(prefix) >= 40:
            await env.reply("Слишком длинный префикс, мур")
            return "DONE"

        cleared_prefix = await clear_prefix(prefix)
        if not cleared_prefix:
            return await env.reply("В вашем префиксе найдено упоминание или доменная зона")

        usera.personal = cleared_prefix
        await manager.update(usera)
        await env.eenv.dbredis.set(f"honoka:cached_prefix:{message.from_id}", prefix+", ")
        await env.reply("Префикс был установлен.")
        return "DONE"


@plugin.on_startswith_text("rank беседы")
async def on_message(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")
        return "DONE"

    l = []
    for x in env.eenv.meta_data.users:
        l.append(x['id'])
    usersinconf = l

    users15 = await manager.execute(
        PxUser.select().where(PxUser.iduser << usersinconf).order_by(PxUser.xpcount.desc()).limit(15))
    top = 1
    tops = "Топ 15 в этой беседе:\n\n"
    usr = []
    for x in users15:
        usr += [x.iduser]

    users = await env.request('users.get', user_ids=','.join(usr))
    for x in users.response:
        xpcoun = await manager.execute(PxUser.select().where(PxUser.iduser == x['id']))
        tops += f"{str(top)}. [id{x['id']}|{x['first_name']} {x['last_name']}] - {xpcoun[0].xpcount}xp\n"
        top += 1

    await env.reply(tops)
    return "DONE"


@plugin.on_startswith_text("rank хелп")
async def on_message(message, attachments, env):
    await env.reply(f"Рассказываю как всё устроенно!\n"
                    f"Смотри например ты новенький вводишь !rank - тебя регистрируют в базу и ты получаешь звание новичок\n"
                    f"Каждый уровень - название ранга\n"
                    f"Раз в десять секунд за одно любое сообщение ты получаешь от 1-10xp если ты обычный смертный\n"
                    f"Т.к. я очень люблю тех кто поддержал моего бота\n"
                    f"Випы получают от 11-25xp за сообщение\n"
                    f"Ну, а админы вообще хитрожопые - 250xp за сообщение\n"
                    f"\n\nПосле 5 лвла вам будет писаться !setprefix <prefix>\n"
                    f"Вы просто пишите !setprefix и какой вам префикс будет угодно\n")
    return "DONE"


@plugin.on_startswith_text("rank")
async def on_message(message, attachments, env):
    usera = await get_or_none(PxUser, iduser=str(message.from_id))
    if usera:
        users = await manager.execute(PxUser.select().order_by(PxUser.xpcount.desc()).limit(1000).dicts())
        position = next((index for (index, d) in enumerate(users) if d["iduser"] == usera.iduser), None)
        if position == 0:
            position += 1
        elif position:
            pass
        else:
            position = "1000+"
        # all_users = PxUser.select().order_by(PxUser.xpcount.desc()).dicts()
        #       print(list(all_users.keys()))

        kb = VKKeyboard()
        kb.set_inline(True)
        kb.add_row()
        kb.edit_row(0).add_button("✨ Ваш профиль экономики", payload={'command': f'{env.eenv.prefix}профиль'}, color="primary")
        if env.eenv.is_multichat:
            kb.add_row()
            kb.edit_row(1).add_button("👥 Топ беседы", payload={'command': f'{env.eenv.prefix}rank беседы'}, color="primary")
        
        player_xp = usera.xpcount
        player_lvl = await xputils.getLevel(player_xp)
        next_lvl_reqs = int(await xputils.getRequiredScoreForLevel(player_lvl+1))
        remaining_xp = int(next_lvl_reqs-player_xp)

        if usera.rank != player_lvl:
            usera.rank = player_lvl

        df = f'👨Статистика для [id{int(usera.iduser)}|чертя]:\n\n'
        user_privs = await priviligeshelper.getUserPriviliges(env, usera.iduser)
        if user_privs & priviligeshelper.USER_ADMIN > 0:
            df += "⭐| Администратор ✳\n"
        elif user_privs & priviligeshelper.USER_MODERATOR > 0:
            df += "⭐| Модератор 🅾\n"
        elif user_privs & priviligeshelper.USER_VIP > 0:
            df += "⭐| Вип Ⓜ\n"
        else:
            df += "⭐| Юзер 🆖\n"
        df += f'📢| Уровень: {player_lvl}\n'
        if usera.rank > len(levelarr) - 1:
            df += f"🔑| Префикс: {usera.personal if usera.personal != '' else 'Установите свой префикс!'}\n"
        else:
            df += f"🔑| Звание: {levelarr[player_lvl]}\n"

        df += f'✉| Количество сообщений: {humanize(usera.messcount)}\n'
        df += f'⛏| Количество опыта: {humanize(player_xp)}/{humanize(next_lvl_reqs)}xp (осталось {humanize(remaining_xp)}xp)\n'
        df += f'💻| Позиция в топе: #{position}\n'
        await env.reply(df, keyboard=kb.dump_keyboard())
        await manager.update(usera)
        return "DONE"
    else:
        await manager.get_or_create(PxUser, iduser=str(message.from_id), xpcount=0, messcount=0, rank=0, personal="")
        return "DONE"
