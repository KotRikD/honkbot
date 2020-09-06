from kutana import Plugin
import json
import aiohttp


plugin = Plugin(name="Топ 10", cmds=[{'command': 'топ 10 [онгоингов/хентая]', 'desc': 'топ 10'}])


@plugin.on_startswith_text("топ 10")
async def on_message(message, attachments, env):
    #https://shikimori.org/api/animes?status=ongoing&limit=10 - OnGoing
    #https://shikimori.org/api/animes?rating=rx&limit=10 - Hentai

    if not env['args']:
        await env.reply("Чего топ-то? \nОнгоингов или Хентая?")
        return "DONE"
    elif env['args'][0].lower() == "онгоингов":
        async with aiohttp.ClientSession() as session:
            async with session.get("https://shikimori.org/api/animes?status=ongoing&limit=10") as response:
                response = await response.json()
                x = 0
                final = []
                for res in response:
                    final.append(str(x+1) + f". {res['russian']}")
                    x = x + 1

                await env.reply('\n'.join(final))
                return "DONE"
    elif env['args'][0].lower() == "хентая":
        async with aiohttp.ClientSession() as session:
            async with session.get("https://shikimori.org/api/animes?rating=rx&limit=10") as response:
                response = await response.json()
                x = 0
                final = []
                for res in response:
                    final.append(str(x+1) + f". {res['russian']}")
                    x = x + 1

                await env.reply('\n'.join(final))
                return "DONE"