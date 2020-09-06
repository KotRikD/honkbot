
from kutana import Plugin
from kutana.structures import objdict
from utils import ddict, edict, parse_user_name
import asyncio
from operator import is_not
from functools import partial

plugin = Plugin(name="Статистика чата", cmds=[{'command': 'chatstats', 'desc': 'отображение статистики текущего чата.'},
                                              {'command': 'raiting', 'desc': 'отображение топа из чатов!'}], order=30)

async def getname(env, user_id):
    users = {}
    for u in env.eenv.meta_data.users:
        if 'name' in u:
            continue
        users[u["id"]] = u['first_name'] + " " + u["last_name"]
    resuser = users.get(user_id)
    if not resuser:
        if user_id < 0:
            return user_id
        us = await env.request('users.get', user_ids=user_id, fields="sex,screen_name,nickname")

        if not us:
            return user_id
        name1 = us.response[0]["first_name"] + " " + us[0]["last_name"]
        return name1
    return resuser

async def getrawname(env, user_id):
    us = await env.request('users.get', user_ids=user_id, fields="sex,screen_name,nickname")
    if not us:
        return user_id
    name1 = us.response[0]["first_name"] + " " + us[0]["last_name"]
    return name1

def textify_value(value):
    avalue = abs(value)

    if avalue >= 1000000000000:
        return str(round(value / 1000000000000, 2)) + "T"

    if avalue >= 1000000000:
        return str(round(value / 1000000000, 2)) + "B"

    if avalue >= 1000000:
        return str(round(value / 1000000, 2)) + "M"

    if avalue >= 100000:
        return str(value // 1000) + "k"

    if avalue >= 1000:
        return str(value)
    return str(value)

async def digits_recursive(nonneg):
    digits = []
    while nonneg:
        digits += [nonneg % 10]
        nonneg //= 10
    return digits[::-1] or [0]


async def disassembly_message(env, message, attachments):
    test = 0
    r = await ddict(env.eenv.dbredis.get(f"honoka:chat_stats:{message.peer_id}"))
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

    async def check(ats, test):
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
        data = await check(attachments, test)
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

@plugin.on_startswith_text("chatstats")
async def on_message(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")

    text = f"статистика чата №{message.peer_id}\n"
    r = await ddict(await env.eenv.dbredis.get(f"honoka:chat_stats:{message.peer_id}"))
    if not r:
        chat_base = objdict(
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

    if r['messages'] > 0:
        text += f"📧 Сообщений: {textify_value(r['messages'])} ({textify_value(r['clear_messages'])} чистых)\n"
    if r['symbols'] > 0:
        text += f"🔣 Символов: {textify_value(r['symbols'])} ({textify_value(r['clear_symbols'])})\n"
    if r['voice_messages'] > 0:
        text += f"🎵 Голосовых: {textify_value(r['voice_messages'])}\n"
    if r['resend_messages'] > 0:
        text += f"📩 Пересланных: {textify_value(r['resend_messages'])}\n"
    if r['photos'] > 0:
        text += f"📷 Фото: {textify_value(r['photos'])}\n"
    if r['videos'] > 0:
        text += f"📹 Видео: {textify_value(r['videos'])}\n"
    if r['audios'] > 0:
        text += f"🎧 Аудио: {textify_value(r['audios'])}\n"
    if r['docs'] > 0:
        text += f"📑 Документов: {textify_value(r['docs'])}\n"
    if r['posts'] > 0:
        text += f"📣 Постов: {textify_value(r['posts'])}\n"
    if r['stickers'] > 0:
        text += f"😜 Стикеров: {textify_value(r['stickers'])}\n"
    if r['mentios'] > 0:
        text += f"💬 Упоминаний: {textify_value(r['mentios'])}\n"
    if r['links'] > 0:
        text += f"📡 Ссылок: {textify_value(r['links'])}\n"
    if r['leaved'] > 0:
        text += f"🚪 Выходов из чата: {textify_value(r['leaved'])}\n"
    if r['messages_with_sw'] > 0:
        text += f"👺 Сообщений с матом: {textify_value(r['messages_with_sw'])}\n"
    if not text:
        await env.reply('ошибка получения данных.')
        return "DONE"

    await env.reply(text)
    return "DONE"

def build_task(env, key):
    async def task():
        value = await env.eenv.dbredis.get(key)
        json = await ddict(value)
        return json
    
    return task

@plugin.on_startswith_text("raiting")
async def on_message(message, attachments, env):
    if not env.eenv.is_multichat or not env.eenv.meta_data:
        await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")
        return "DONE"

    top_raw = await env.eenv.dbredis.scan(match="honoka:chat_stats:*")
    chats = []
    while True:
        item = await top_raw.fetchone()
        if item is None:
            break
        else:
            chats.append(item)
    tasks = []
    for chat in chats:
        tasks.append(build_task(env, chat)())
    
    chats = list(await asyncio.gather(*tasks))
    chats = [chat for chat in chats if chat is not None]

    top = list(sorted(chats, key=lambda k: k['messages'], reverse=True))
    raiting = {}
    cur = 1
    text = "🏆 Наиболее активные чаты:\n"
    for p in top:
        #print(p)
        if int(p['chat_id']) < 0:
            continue
        if p['chat_id'] not in raiting:
            raiting[p['chat_id']] = p['messages']
        else:
            raiting[p['chat_id']] += p['messages']
    for i in list(raiting.keys())[:10]:
        chat = await env.request('messages.getConversationsById', peer_ids=i)
        if chat.error or len(chat.response['items'])<1 or not 'chat_settings' in chat.response['items'][0]:
            continue
        chat = chat.response['items'][0]
        num = cur
        admin_name = await parse_user_name(env, chat['chat_settings']['owner_id'])
        text += f"{num}. {chat['chat_settings']['title']} - @id{chat['chat_settings']['owner_id']} ({admin_name})\n"
        cur += 1
    if not message.peer_id in list(raiting.keys())[:10]:
        num = list(raiting.keys()).index(message.peer_id) + 1
        text += f"...\n{num}. <<Ваша беседа>>"
    return await env.reply(text)

