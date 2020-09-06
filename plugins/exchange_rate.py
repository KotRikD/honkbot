from kutana import Plugin
import aiohttp
import json

plugin = Plugin(name="Курсы валют", cmds=[{'command': 'курс', 'desc': 'узнать курс валют'}])

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

async def get_rate():
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://www.cbr-xml-daily.ru/daily_json.js") as resp:
            try:
                data = await resp.read()
                data = json.loads(data)
                return data['Valute']
            except (KeyError, IndexError):
                raise ValueError('Курса данной валюты не найдено')

@plugin.on_startswith_text("курс", "валюта")
async def on_message(message, attachments, env):
    data = []
    rate = await get_rate()
    for cur in ('USD', 'EUR', 'GBP'):
        data.append(rate[cur]['Value'])
    usd, eur, gbp = data

    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://blockchain.info/ru/ticker") as resp:
            data = await resp.read()
            btc = json.loads(data)
            btc = btc["RUB"]["sell"]

    vk_message = (f"1 Доллар = {toFixed(usd, 2)} руб.\n"
                  f"1 Евро = {toFixed(eur, 2)} руб.\n"
                  f"1 Фунт = {toFixed(gbp, 2)} руб.\n"
                  f"1 Биткойн = {toFixed(btc, 2)} руб.\n")
    await env.reply(vk_message)
    return "DONE"
