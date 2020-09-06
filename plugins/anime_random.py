from kutana import Plugin
import aiohttp

plugin = Plugin(name="Рандомное аниме", cmds=[{'command': 'посоветуй аниме', 'desc': 'бот подскажет тебе аниме'}])

@plugin.on_startswith_text("посоветуй аниме")
async def on_message(message, attachments, env):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f'https://api.kotrik.ru/api/recommendAnime') as resp:
            r = await resp.json()
    try:
        if not r:
            return await env.reply("Мне нечего тебе посоветовать!")

        rl = r['response']
        anr = f"\n👍| Название: {rl['name']}\n"

        ff = "💥| Жанры: "
        for x in rl['genres']:
            ff += f"{x} "

        anr += ff+"\n"
        anr += f"💡| Описание: \n{rl['description']}\n"
        anr += f"⚡| Ссылка на просмотр онлайн: {rl['url']}"

        await env.reply(anr)
    except Exception as e:
        print(e)
        await env.reply("пока мне нечего тебе посоветовать.")
    return "DONE"
