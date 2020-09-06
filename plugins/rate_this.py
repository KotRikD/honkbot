import random
from kutana import Plugin

plugin = Plugin(name="Оцени", cmds=[{'command': 'оцени <текст>', 'desc': 'оценить что-либо'}])

numbers = ['0', '0', '0', '1', '1', '2', '3', '4', '5', '5', '5', '6', '7', '8', '8', '8', '8', '9', '9', '9', '10', '10', '12', '12']

@plugin.on_startswith_text("оцени")
async def on_message(message, attachments, env):
    text = ' '.join(env['args'])
    if not text:
        return await env.reply("Оценивать что именно.")

    return await env.reply(f"Ну я думаю {random.choice(numbers)}/10")