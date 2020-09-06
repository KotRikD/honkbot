from kutana import Plugin
import random
plugin = Plugin(name="Плагин для IQ", cmds=[{'command': 'iq', 'desc': 'узнать iq'}])


@plugin.on_startswith_text("iq")
async def on_message(message, attachments, env):
    iq = random.randint(0, 100)
    await env.reply(f'Я думаю твой IQ составляет примерно, {str(iq)} баллов.')