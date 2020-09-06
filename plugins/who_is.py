from kutana import Plugin
import random
from random import sample
from database import *
from utils import priviligeshelper

plugin = Plugin(name="Кто? Кто в кого влюблён", cmds=[{'command': 'кто <определение>', 'desc': 'кто в конференции является обладателем определения.'},
                                                      {'command': 'кто кого', 'desc': 'кто кого же любит в беседе? Хмммммм'},
                                                      {'command': 'ктогей', 'desc': 'поиск петушков'}])


@plugin.on_startswith_text("кто кого", "ктокого")
async def on_message(message, attachments, env):
    if env.eenv.is_multichat and env.eenv.meta_data:
        love1, love2 = sample(env.eenv.meta_data.users, 2)
        await env.reply(f"[id{love1['id']}|{love1['first_name']} {love1['last_name']}] - ❤ Любит ❤ - [id{love2['id']}|{love2['first_name']} {love2['last_name']}]")
    else:
        await env.reply("Эту команду можно использовать только в беседе, и при условии что у бота есть права администратора.")


@plugin.on_startswith_text("ктогей", "ктопидор")
async def on_message(message, attachments, env):

    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Команда должна запускаться в беседе, где бот является администратором")

    gay = random.choice(env.eenv.meta_data.users)#рандомно выбираем гея из списка
    if await priviligeshelper.getUserPriviliges(env, gay['id'])&priviligeshelper.USER_ADMIN>0:
        await env.reply("К сожалению это админ. Если скажу такое он мне отрубит розетку.")
    else:
        await env.reply("[id"+ str(gay['id'])+f"|{gay['first_name']} {gay['last_name']}] - вот ваш петушок")

@plugin.on_startswith_text("кто")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply(f"Используйте !кто <текст>\n(без `<` или `>`)")

    if not env.eenv.is_multichat or not env.eenv.meta_data:
        return await env.reply("Эту команду надо использовать в беседе и бот должен быть администратором!")
    else:
        user = random.choice(env.eenv.meta_data.users)

        return await env.reply(f"Кто {' '.join(env['args'])}? Я думаю, это {user['first_name']} {user['last_name']} 🙈")

