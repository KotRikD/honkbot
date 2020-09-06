from kutana import Plugin
import json
import aiohttp
import mc


plugin = Plugin(name="Выбор Маркова", cmds=[{'command': 'мч [текст]', 'desc': 'коверкает предложения)'}])


def parseRussian(args):
    env_to_lower = []
    preview = ""
    for arg in args:
        if preview == "" and len(arg) <= 3:
            preview = arg.lower()
            continue
        elif len(preview) > 0 and len(arg) <= 3:
            preview += f" {arg.lower()}"
            continue
        elif len(preview) > 0 and len(arg) > 3:
            env_to_lower.append(f"{preview} {arg.lower()}")
            preview = ""
            continue
        else:
            env_to_lower.append(arg.lower())
    return env_to_lower


@plugin.on_startswith_text("мч")
async def on_message(message, attachments, env):
    if not env.args:
        return await env.reply("Пожалуйста введите аргументы)")

    parsed = parseRussian(env.args)

    generator = mc.StringGenerator(
        learning_data=parsed,
        order=1
    )

    return await env.reply(' '.join(generator.generate(count=len(parsed))).lower())