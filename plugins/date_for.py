from kutana import Plugin
import random as rnd

plugin = Plugin(name="Узнай дату события", cmds=[{'command': 'дата <чего именно>', 'desc': 'дата события'}])

@plugin.on_startswith_text("дата")
async def on_message(message, attachments, env):
    if not env['args']:
        await env.reply("Дату чего?")
        return "DONE"

    datewhat = ' '.join(env['args'])
    month = rnd.randint(1, 12)
    day = rnd.randint(1, 28)
    year = str(rnd.randint(2014, 2030))

    if not month > 9:
        month = "0"+str(month)
    else:
        month = str(month)

    if not day > 9:
        day = "0"+str(day)
    else:
        day = str(day)

    await env.reply(f"(・∀・) {day}.{month}.{year}")
    return "DONE"

