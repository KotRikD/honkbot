from kutana import Plugin
import feedparser

plugin = Plugin(name="Гороскоп", cmds=[{'command': 'гороскоп <знак зодиака>', 'desc': 'показывает гороскоп на сегодня'}])

ems = {
    'овен': 1,
    'телец': 2,
    'близнецы': 3,
    'рак': 4,
    'лев': 5,
    'дева': 6,
    'весы': 7,
    'скорпион': 8,
    'стрелец': 9,
    'козерог': 10,
    'водолей': 11,
    'рыбы': 12
}

@plugin.on_startswith_text("гороскоп")
async def on_message(message, attachments, env):
    if not env['args']:
        await env.reply(f"Пример: {env.eenv['prefixes']}гороскоп близнецы")
        return "DONE"

    if not env['args'][0] in ems:
        await env.reply(f"Пример: {env.eenv['prefixes']}гороскоп близнецы")
        return "DONE"

    pos = ems[env['args'][0]]

    feed = feedparser.parse('http://www.hyrax.ru/cgi-bin/bn_xml.cgi')

    summary = feed.entries[pos]['summary']
    await env.reply("☀🔥🖤 "+summary)
    return "DONE"