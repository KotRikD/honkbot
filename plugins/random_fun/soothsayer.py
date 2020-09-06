# -*- coding: utf-8 -*-
from kutana import Plugin

import random

plugin = Plugin(name="Шар предсказаний", cmds=[{'command': 'шар [строка]', 'desc': 'правдиво или нет'}])

answers = '''Абсолютно точно!
Да.
Нет.
Скорее да, чем нет.
Не уверен...
Однозначно нет!
Если ты не фанат аниме, у тебя все получится!
Если ты фанат аниме, у тебя все получится!
Можешь быть уверен в этом.
Перспективы не очень хорошие.
А как же иначе?.
Да, но если только ты не смотришь аниме.
Знаки говорят — «да».
Не знаю.
Мой ответ — «нет».
Весьма сомнительно.
Не могу дать точный ответ.
'''.splitlines()

@plugin.on_startswith_text("шар")
async def on_message(message, attachments, env):
    await env.reply("🔮" + random.choice(answers))
