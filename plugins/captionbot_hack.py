from kutana import Plugin
from captionbot import CaptionBot
from yandex.Translater import Translater
from database import *
from utils.static_text import need_vip
from utils import priviligeshelper

plugin = Plugin(name="Разъебу и узнаю, что на фото", cmds=[{'desc': 'узнаю, что на фотке находится', 'command': 'что на фото <вложение>', 'vip': True}])

c = CaptionBot()
tr = Translater()
tr.set_key('<yandex key>') # Api key found on https://translate.yandex.com/developers/keys
tr.set_from_lang('en')
tr.set_to_lang('ru')

@plugin.on_startswith_text("что на фото")
async def what_on_photo(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_VIP > 0):
        return await env.reply(need_vip)

    if not attachments or attachments[0].type != "photo":
        return await env.reply("Хорошо, а изображение где?")

    image = attachments[0]
    link = image.link

    result = c.url_caption(link)
    if not result:
        return await env.reply("Я не знаю, что на фото.")
    else:
        try:
            tr.set_text(result)
            s = tr.translate()

            return await env.reply(s)
        except:
            return await env.reply("Я не знаю, что на фото.")

