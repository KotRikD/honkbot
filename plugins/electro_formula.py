from lxml import html
from kutana import Plugin
import aiohttp

endpoint = 'http://www.sciencedebate2008.com/elektronnyye-formuly-atomov/'

plugin = Plugin(name="Электронные форумлы", cmds=[{'command': 'formula <число>', 'desc': 'просчитать число электронов'}])

def pluralRusVariant(x):
    lastTwoDigits = x % 100
    tens = lastTwoDigits / 10
    if tens == 1:
        return 2
    ones = lastTwoDigits % 10
    if ones == 1:
        return 0
    if ones >= 2 and ones <= 4:
        return 1
    return 2

@plugin.on_startswith_text("formula")
async def on_message(message, attachments, env):
    if not env['args']:
        return await env.reply('Извините, но вы не указали число электронов')
    if not env['args'][0].isdigit():
        return await env.reply('Укажите число электронов')
    if int(env['args'][0]) <= 0 or int(env['args'][0]) > 118:
        return await env.reply('Число электронов должно варьироваться от 1 до 118.')

    async with aiohttp.ClientSession() as sess:
        async with sess.post(endpoint, data=None) as resp:
            response = await resp.text()
            tree = html.fromstring(response)
            formula = tree.xpath('//td[@align="left"]')
            suffix = ["электроном", "электронами", "электронами"][pluralRusVariant(int(env['args'][0]))]
            vk_message = f'Электронная формула элемента с {int(env["args"][0])} {suffix}:\n'
            vk_message += str(formula[int(env['args'][0]) - 1].text_content())
            return await env.reply(vk_message)