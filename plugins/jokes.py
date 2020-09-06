from kutana import Plugin
import aiohttp, random

plugin = Plugin(name="Шутки", cmds=[{'command': 'пошути', 'desc': 'написать случайный анекдот'}])

answers = '''А вот и шуточки подъехали!!!
Сейчас будет смешно, зуб даю!
Шуточки заказывали?
Петросян в душе прям бушует :)
'''.splitlines()

URL = "http://rzhunemogu.ru/RandJSON.aspx?CType=1"

@plugin.on_startswith_text("пошути")
async def on_message(message, attachments, env):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(URL) as resp:
            text = await resp.text()
            joke = "".join(text.replace('\r\n', '\n').split("\"")[3:-1])
    await env.reply(random.choice(answers) + '\n' + str(joke))