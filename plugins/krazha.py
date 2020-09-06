import random
from kutana import Plugin
from utils import parse_user_id, parse_user_name

variants = ['Пантсу', 'Деньги', 'Девственность <3', 'Плащ', 'Говно', 'Мозг']

plugin = Plugin(name="Плагин для кражи", cmds=[{'command': 'кража @человек <вещь>', 'desc': 'украсть вещь у @человека'}])


@plugin.on_startswith_text("кража")
async def on_message(message, attachments, env):
    userc = await parse_user_id(message, env, custom_text=env['args'][0] if len(env['args'])>0 else None)
    if not userc:
        return await env.reply("Ты не упомянул человека!")

    user_name = await parse_user_name(env, userc[0])

    if len(env['args']) < 2:
        return await env.reply("А шо пиздить буим?")

    if random.randint(0, 3) == 3:
        return await env.reply(
            f"🔑 [id{message.from_id}|Этот человек спиздил у] [id{userc[0]}|{user_name}]\n🛒 {random.choice(variants)}")
    else:
        return await env.reply(
            f"🔑 [id{message.from_id}|Этот человек спиздил у] [id{userc[0]}|{user_name}]\n🛒 {' '.join(env['args'][1:])}")
