from lxml import html
from kutana import Plugin
import aiohttp

plugin = Plugin(name="Что за день сегодня?", cmds=[{ 'command': 'сегодня день чего', 'desc': 'Показывает какой сегодня день.'}])


@plugin.on_startswith_text("сегодня день чего")
async def here_day(message, attachments, env):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"http://kakoysegodnyaprazdnik.ru",
                            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}) as resp:
            fs_paged_res = html.fromstring(await resp.text())

    days = []

    happy_days = fs_paged_res.cssselect("div.listing_wr > div > div.main")
    for x in happy_days:
        days.append(x.text_content().replace("• ", "").replace("\n", "")+"\n")

    return await env.reply(f"Сегодня праздники:\n🌲"+'\n🌲 '.join(days))



