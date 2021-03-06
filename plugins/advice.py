from kutana import Plugin
import random
from utils import VKKeyboard

advices = '''Напиши ня ТЗ!
Удели ня себе время!
Не мешай ня другим работать!
Изучай ня новые технологии!
Рассчитывай ня время!
Никогда ня не оправдывайся!
Не ленись, ня!
Выражайся ня ясно!
Не делай ня чужую работу!
Сделай ня пока помнишь!
Научись ня говорить НЕТ!
Иди ня и сделай!Уберись ня на столе!
Постоянно ня развивайся!
Записывай ня свои мысли!
Не лежи ня после звонка будильника!
Хорош ня откладывать!
Цени ня свой труд!
Уважай ня коллег!
Повышай ня планку!
Экспериментируй, ня!
Признавай ня свои ошибки!
Объясняй ня свои решения!
Поменьше пизди о своих планах!
Не жди ня вдохновения!
Нет работы — иди ня учись!
Делись ня знаниями!
Подумай ня дважды!
Не жалей ня себя!
Приноси ня пользу!
Не жалей ня об упущенном!
Применяй ня новые знания!
Договаривайся ня на берегу!
Не спеши ня!
Не отвечай ня больше чем спрашивают!Делегируй ня второстепенное!
Ставь ня конкретные сроки!
Спрашивай ня обо всём!
Будь ня в курсе событий!
Не экономь ня на важном!
Работай ня честно!
Лён факин инглиш!
Не работай ня с мудаками!
Благодари ня людей!
Будь ня настойчивым!Расставляй ня приоритеты!
Не считай ня чужие деньги!
Перестань ня сравнивать себя с другими!
Сомневаешься — спроси ня!
Не ленись, ня!
Не срывай ня сроки!
Не подписывай на дело полных долбоёбов!
Изучай ня чужие работы!
Сделай ня ещё проще!
Поднимай ня расценки!
Подумай ня дважды!Не суди ня по возрасту!
Переступай ня через себя!
Не спорь ня с дураками!
Составь ня список важных дел!
Начни с себя, ёпта!
Проверь ня ещё раз!
Не работай ня бесплатно!
Не завидуй, ня — работай!
Не срывайся ня на окружающих!
Переноси ня сроки с запасом!
Делай ня поэтапно!
Сначала ня подготовься!'''.splitlines()

plugin = Plugin(name="Дай советик", cmds=[{'command': 'cовет', 'desc': 'бот даст совет!'}])

@plugin.on_startswith_text("совет")
async def on_message(message, attachments, env):
    kb = VKKeyboard()
    kb.lazy_buttons({
        'inline': True,
        'buttons': [
            {'text': '💡 ещё совет', 'payload': {'command': f'{env.eenv.prefix}совет'}, 'color': 'primary'}
        ]
    })
    await env.reply(random.choice(advices), keyboard=kb.dump_keyboard())
    return "DONE"