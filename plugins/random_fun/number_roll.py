from kutana import Plugin

import random

plugin = Plugin(name="Рандом", cmds=[{'command': 'рандом <от> <до>', 'desc': 'случайное число в диапазоне ОТ ДО'}])

@plugin.on_startswith_text("рандом")
async def on_message(message, attachments, env):
    try:
        args = [int(arg) for arg in env['args']]
    except ValueError:
        return await env.reply("Один из аргументов - не число")

    # Если у нас два аргумента - это диапазон
    if len(args) == 2:
        start, end = args
        # Конечное значение больше начального
        if abs(end - start) > 0:
            num = random.randint(start, end)
        # Конечное число меньше начального
        else:
            num = random.randint(end, start)

    # Если один аргумент, то диапазон будет - (1, число)
    elif len(args) == 1:
        num = random.randint(1, args[0])
    # Если нет аргументов, то диапазон, как в игральном кубике
    else:
        num = random.randint(1, 6)
    await env.reply("Моё число - " + str(num))
