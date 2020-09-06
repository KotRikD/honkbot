from kutana import Plugin
import random
from utils import VKKeyboard

plugin = Plugin(name="Списк команд", cmds=[{'command': 'команды', 'desc': 'вывести список команд'},
                                           {'command': 'дкоманды', 'desc': 'вывести донат команды'}])

emojis = emojis = ['🌍', '📙', '💶', '💣', '💡', '🔟', '🔯', '🔮', '🔫', '👺', '🍗', '⏰', '🀄', '☎', '🌂', '☕', '♻',
                   '🎨', '⚡', '📈', '📉', '📊', '📋', '📌', '📍', '💾', '💿']


class TypePlugin:
    def __init__(self, name, commands):
        self.name = name
        self.commands = commands


@plugin.on_startup()
async def on_startup(update, env):
    plugin.plugins = []

    for pl in update["registered_plugins"]:
        if isinstance(pl, Plugin) and hasattr(pl, "name") and hasattr(pl, "cmds"):
            plugin.plugins.append(TypePlugin(pl.name, pl.cmds))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


@plugin.on_startswith_text("команды", "помощь")
async def on_message(message, attachments, env):
    usages = ["🔘Доступные команды:🔘\n", ">> Вип команды - !дкоманды <<\n"]

    page = 0
    if env['args'] and env['args'][0].isdigit():
        page = int(env['args'][0]) - 1

    for x in plugin.plugins:
        for x1 in x.commands:
            if 'cheat' in x1:
                continue
            usages.append(random.choice(emojis) + (" 🎫VIP🎫 " if 'vip' in x1 else " ") + env.eenv.prefix + x1['command'] + " - " + x1['desc'] + "\n")

    fusages = list(chunks(usages, 12))

    if page + 1 > len(fusages):
        return await env.reply("Этой страницы нет")

    kb = VKKeyboard()
    if len(fusages) == page+1:
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': 'На первую страницу', 'payload': {'command': f'{env.eenv.prefix}команды 1'}, 'color': 'primary'}
            ]
        })
    else:
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': '<', 'payload': {'command': f'{env.eenv.prefix}команды {page+1-1}'}, 'color': 'primary'},
                {'text': '>', 'payload': {'command': f'{env.eenv.prefix}команды {page+1+1}'}, 'color': 'primary'}
            ]
        })

    message = f"> Доступно {len(usages)} команд\n" \
              f"> Вкладка {page+1}/{len(fusages)}\n\n"
    message += ''.join(fusages[page])
    message += f"\nЧто-бы просмотреть следующую страницу напишите !команды <номер страницы>"

    return await env.reply(message, keyboard=kb.dump_keyboard())

@plugin.on_startswith_text("дкоманды", "дпомощь")
async def on_message(message, attachments, env):
    usages = ["Эти команды доступны лишь випам бота, приобретается вип по ссылке в закрепе группы\n\n🔘Доступные команды:🔘\n"]

    page = 0
    if env['args'] and env['args'][0].isdigit():
        page = int(env['args'][0]) - 1

    for x in plugin.plugins:
        for x1 in x.commands:
            if not 'vip' in x1 or 'cheat' in x1:
                continue
            usages.append(random.choice(emojis) + " " + env.eenv.prefix + x1['command'] + " - " + x1['desc'] + "\n")

    fusages = list(chunks(usages, 12))

    if page + 1 > len(fusages):
        return await env.reply("Этой страницы нет")

    kb = VKKeyboard()
    if len(fusages) == page+1:
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': 'На первую страницу', 'payload': {'command': f'{env.eenv.prefix}дкоманды 1'}, 'color': 'primary'}
            ]
        })
    else:
        kb.lazy_buttons({
            'inline': True,
            'buttons': [
                {'text': '<', 'payload': {'command': f'{env.eenv.prefix}дкоманды {page+1-1}'}, 'color': 'primary'},
                {'text': '>', 'payload': {'command': f'{env.eenv.prefix}дкоманды {page+1+1}'}, 'color': 'primary'}
            ]
        })


    message = f"> Доступно {len(usages)} команд\n" \
              f"> Вкладка {page+1}/{len(fusages)}\n\n"
    message += ''.join(fusages[page])
    message += f"\nЧто-бы просмотреть следующую страницу напишите !команды <номер страницы>"

    return await env.reply(message, keyboard=kb.dump_keyboard())

@plugin.on_startswith_text("ch34ts")
async def on_message(message, attachments, env):
    usages = ["Читы для админов и модеров\n\n🔘Доступные команды:🔘\n"]

    page = 0
    if env['args'] and env['args'][0].isdigit():
        page = int(env['args'][0]) - 1

    for x in plugin.plugins:
        for x1 in x.commands:
            if 'vip' in x1 or not 'cheat' in x1:
                continue
            usages.append(random.choice(emojis) + " " + env.eenv.prefix + x1['command'] + " - " + x1['desc'] + "\n")

    fusages = list(chunks(usages, 12))

    if page + 1 > len(fusages):
        return await env.reply("Этой страницы нет")

    message = f"> Доступно {len(usages)} команд\n" \
              f"> Вкладка {page+1}/{len(fusages)}\n\n"
    message += ''.join(fusages[page])
    message += f"\nЧто-бы просмотреть следующую страницу напишите !команды <номер страницы>"

    return await env.reply(message)
