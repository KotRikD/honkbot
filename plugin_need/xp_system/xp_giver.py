from kutana import Plugin
from database import *
from random import randint as rnd
from utils import xputils, edict, ddict, priviligeshelper
import peewee_async

plugin = Plugin(name="Добавка к XPSystem, ввиде опыта выдавателя", priority=620)

async def give_xp(user_id, env):
    usera = await get_or_none(PxUser, iduser=str(user_id))
    if not usera:
        await manager.get_or_create(PxUser, iduser=str(user_id), personal="")
        return "GOON"

    if usera.xpcount == 0:
        await xputils.getRequiredScoreForLevel(0)
        usera.messcount += 1
        usera.xpcount += 1
        usera.rank = 1
        return await manager.update(usera)
    else:
        level = await xputils.getLevel(usera.xpcount)
        tempuserstats = await ddict(await env.eenv.dbredis.get(f"honoka:cached_money:{user_id}"))
        if not tempuserstats:
            tempuserstats = dict(
                messages=0,
                money=0
            )

        usera.messcount += 1
        if usera.rank != level:
#                    await msg.answer(f"Вы повысили свой уровень! Ваш уровень: {level}")
            usera.rank = level
        tempuserstats['messages'] += 1
        priviliges = await priviligeshelper.getUserPriviliges(env, user_id)
        if priviliges&priviligeshelper.USER_ADMIN>0:
            usera.xpcount += rnd(100, 150)
            tempuserstats['money']+=rnd(3500, 7000)

        elif priviliges&priviligeshelper.USER_MODERATOR>0:
            usera.xpcount += rnd(50, 100)
            tempuserstats['money'] += rnd(2400, 3000)
        elif priviliges&priviligeshelper.USER_VIP>0:
            usera.xpcount += rnd(25, 50)
            tempuserstats['money'] += rnd(1200, 2400)
        else:
            usera.xpcount += rnd(11, 25)
            tempuserstats['money'] += rnd(500, 1000)

        await env.eenv.dbredis.set(f"honoka:cached_money:{user_id}", await edict(tempuserstats))
        return await manager.update(usera)


async def disassembly_message(env, message, attachments):
    test = 0
    r = await ddict(await env.eenv.dbredis.get(f"honoka:chat_stats:{message.peer_id}"))
    if not r:
        chat_base = dict(
            chat_id=message.peer_id,
            messages=0,
            clear_messages=0,
            clear_symbols=0,
            symbols=0,
            voice_messages=0,
            resend_messages=0,
            photos=0,
            videos=0,
            audios=0,
            docs=0,
            posts=0,
            stickers=0,
            mentios=0,
            links=0,
            leaved=0,
            messages_with_sw=0,
            last_user_id=0
        )
        await env.eenv.dbredis.set(f"honoka:chat_stats:{message.peer_id}", await edict(chat_base))
        r = chat_base

    r['messages'] += 1
    r['last_user_id'] = message.from_id
    r['symbols'] += len(message.text)

    def check(ats, test):
        for at in ats:
            if at.type == 'photo':
                r['photos'] += 1
                test += 1
            if at.type == 'video':
                r['videos'] += 1
                test += 1
            if at.type == 'audio':
                r['audios'] += 1
                test += 1
            if at.type == 'doc':
                if at.raw_attachment['doc']['ext'] == 'ogg':
                    r['voice_messages'] += 1
                    test += 1
                else:
                    test += 1
                    r['docs'] += 1
            if at.type == 'wall':
                test += 1
                r['posts'] += 1
            if at.type == 'sticker':
                test += 1
                r['stickers'] += 1
            return test

    if attachments and env.eenv.is_multichat:
        data = check(attachments, test)
        test += data if data else 0

    if message.text.startswith('[id'):
        r['mentios'] += 1
        test += 1

    links_check = ['.com', '.ru', '.net', '.tg', '.pl', '.xyz', '.pw', 'https', 'http', '.cl', '.ml', '.io', '.gl',
                   '.bet', '.pe', '.tk', '.ly']
    for x in links_check:
        if message.text.find(x) != -1:
            r['links'] += 1
            test += 1
            break

    sw = ['бля', 'сука', 'suka', 'пиздец', 'пздц', 'ска', 'ля', 'blya', 'pidor', 'пидор', 'нах', 'еба', 'хуй',
          'пизда', 'pizda', 'соси', 'уеб', 'ганд', 'хуес', 'шлюх']
    for z in sw:
        if message.text.find(z) != -1:
            r['messages_with_sw'] += 1
            test += 1
            break
    if test == 0:
        r['clear_messages'] += 1
        r['clear_symbols'] += len(message.text)

    await env.eenv.dbredis.set(f"honoka:chat_stats:{message.peer_id}", await edict(r))
    return "GOON"

async def get_or_create_profile(user_id):
    try:
        shopcenters = shopcenter.select()
        job = jobs.select()
        profiles = Profile.select().where(Profile.user_id == user_id)

        profile = list(await manager.prefetch(profiles, shopcenters, job))[0]
    except IndexError:
        profile = await peewee_async.create_object(Profile, user_id=user_id)
    return profile


@plugin.on_has_text()
async def on_has_text(message, attachments, env):
    await give_xp(message.from_id, env)
    if env.eenv.is_multichat and env.eenv.meta_data:
        data_users = await ddict(await env.eenv.dbredis.get(f"honoka:active_users_multichat:{message.peer_id}"))
        if not data_users:
            data_users = dict(
                users=dict()
            )
            await env.eenv.dbredis.set(f"honoka:active_users_multichat:{message.peer_id}", await edict(data_users))

        user_id = str(message.from_id)
        if not message.from_id in data_users['users']:
            if message.from_id<0:
                pass
            else:
                data_users['users'][user_id] = int(time.time())

        if message.raw_update['object'].get('action', 0) != 0:
            if message.raw_update['object']['action']['type'] == 'chat_invite_user':
                if int(message.from_id)<0:
                    pass
                else:
                    data_users['users'][message.from_id] = int(time.time())
            elif message.raw_update['object']['action']['type'] == 'chat_kick_user':
                user_id = str(message.raw_update['object']['action']['member_id'])
                if user_id in data_users['users']:
                    del(data_users['users'][user_id])

        await env.eenv.dbredis.set(f"honoka:active_users_multichat:{message.peer_id}", await edict(data_users))
    return "GOON"


@plugin.on_has_text()
async def on_has_text(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return "GOON"

    await disassembly_message(env, message, attachments)
    return "GOON"
