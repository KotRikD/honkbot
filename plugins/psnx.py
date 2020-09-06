from kutana import Plugin
from database import *
from utils import parse_user_name
from utils import priviligeshelper
import utils.logs as Logs

plugin = Plugin(name="пшнх", cmds=[{'command': 'пшнх', 'desc': 'послать нахуй', 'cheat': True}])


@plugin.on_startswith_text("пшнх")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_ADMIN > 0):
        return await env.reply("Ты не админ")

    await Logs.create_log(env, message.from_id, 0, 8, 'Выпустил нахуй легушку на пользователя!')
    user = await parse_user_name(env, message.from_id)
    return await env.reply(f"{user} посылает вас нахуй!")