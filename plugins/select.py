import random
from kutana import Plugin

plugin = Plugin(name="Выбери", cmds=[{'command': 'выбери <1> или <2> или ...', 'desc': 'выбрать между'}])


@plugin.on_startswith_text("выбери")
async def on_message(message, attachments, env):
    text = ' '.join(env['args'])
    ili = text.split("или")

    if not ili:
        return await env.reply("Почитай справочку о команде)")

    return await env.reply(f"Я выбираю {random.choice(ili)}")