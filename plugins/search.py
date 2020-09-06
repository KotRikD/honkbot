import random
from kutana import Plugin
from database import *
from utils import priviligeshelper
import utils.logs as Logs

plugin = Plugin(name="Поиск в документах", cmds=[{'command': 'search <name>', 'desc': 'искать в документах ВК', 'cheat': True}])

@plugin.on_startswith_text("search")
async def on_message(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_ADMIN > 0):
        return await env.reply("ti ne admin.")

    if not env['args']:
        return await env.reply("А искать что?")

    serach_offset = random.randint(1, 100)

    docs = await env.request('docs.search', q=' '.join(env['args']), count=10, offset=serach_offset)
    result = []

    for x in docs.response['items']:
        if x['type'] == 4 or x['type'] == 3:
            result.append(f"doc{x['owner_id']}_{x['id']}")
    
    await Logs.create_log(env, message.from_id, 0, 100, f"Искал в документах ВК: {' '.join(env['args'])}")
    return await env.reply("Вот, что я нашла!", attachment=','.join(result))
