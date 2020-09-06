from kutana import Plugin
import random

plugin = Plugin(name="Попытаемся сделать музочку?", cmds=[{'command': 'randomsong <N>', 'desc': 'Получает <N> количество рандомных песен'}])


def get_n_songs(count):
    audios = []
    i = 0
    while(i<count):
        server_id = random.randint(1, 291461)
        audio_id = random.randint(456239017, 456239700)
        audios.append(f"audio2000{server_id}_{audio_id},")
        i+=1

    return ''.join(audios)

@plugin.on_startswith_text("randomsong")
async def random_song(message, attachments, env):
    if not env['args']:
        return await env.reply("<N> количество - от 1 до 10")

    if not env['args'][0].isdigit() or int(env['args'][0]) > 10:
        return await env.reply("<N> количество - от 1 до 10")

    att_songs = get_n_songs(int(env['args'][0]))

    return await env.reply("Вот, что я нашла!\nАпи может не предоставлять точнее количество аудиозаписей!", attachment=att_songs)


