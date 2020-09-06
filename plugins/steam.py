from kutana import Plugin
import steamapi
import time

plugin = Plugin(name="Steam", cmds=[{'command': 'steam <url>', 'desc': 'просмотр steam профиля'}])

steamapi.core.APIConnection(api_key="<steam key>", validate_key=True)

@plugin.on_startswith_text("steam")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply("Нету url")

    try:
        if env['args'][0].isdigit():
            user = steamapi.user.SteamUser(int(env['args'][0]))
        else:
            user = steamapi.user.SteamUser(userurl=env['args'][0])
    except:
        return await env.reply("Произошла ошыыыыбка, такого профиля не существует.")

    result = f"Информация о профиле {user.name}\n"
    result += f"⭐|Уровень: {user.level}\n"
    result += f"👓|Steamid64: {user.steamid}\n"
    result += f"📊|Количество опыта: {user.xp}xp\n"
    if user.state == 0:
        result += f'🌍|Онлайн? Нет.\n 🌍|Последний вход: {user.last_logoff.strftime("%Y-%m-%d %H:%M:%S")}\n'
    else:
        result += f"🌍|Онлайн? Да\n"
    result += f'📈|Дата регистрации: {user.time_created.strftime("%Y-%m-%d %H:%M:%S")}\n'
    result += "\n\n🎲|Последние игры:\n"
    try:
        for x in user.recently_played:
            result+= f"🎧|{x.name} {time.strftime('%H hours %M minute', time.gmtime(x.playtime_forever*60))} в игре\n"
    except:
        pass

    return await env.reply(result)
