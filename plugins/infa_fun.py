
import random
from kutana import Plugin

plugin = Plugin(name="Инфа/вероятность", cmds=[{'command': 'инфа <что-то>', 'desc': 'шанс правды'},
                                               {'command': 'вероятность <что-то>', 'desc': 'вероятность'}])


@plugin.on_startswith_text("инфа")
async def on_message(message, attachments, env):
    text = ' '.join(env['args'])
    if not text:
        return await env.reply("Шанс чего?")

    num = random.randint(0, 100)
    await env.reply(f"{text}\nЯ думаю, что {num}% у этой инфы.")
    return "DONE"


@plugin.on_startswith_text("вероятность")
async def on_message_vero(message, attachments, env):
    text = ''.join(env['args'])
    if not text:
        return await env.reply("Шанс чего?")

    num = random.randint(0, 100)
    return await env.reply(f"🎲 Вероятность этого, {num}%")