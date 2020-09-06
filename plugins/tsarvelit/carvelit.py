from kutana import Plugin
from database import *

from PIL import Image
import io

from utils import priviligeshelper
import utils.logs as Logs

plugin = Plugin(name="Царь велит или не велит?", cmds=[{'command': 'царь', 'desc': 'проверить, повелит ли?', 'cheat': True}])

PATH="plugins/tsarvelit/"

@plugin.on_startswith_text("царь")
async def on_message(message, attachments, env):
    if not await priviligeshelper.getUserPriviliges(env, message.from_id)&priviligeshelper.USER_ADMIN > 0:
        return await env.reply("Еще чего, я не велю")

    tsarpic = Image.open(PATH+"tsar.jpg")

    buffer = io.BytesIO()
    tsarpic.save(buffer, format='png')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    
    await Logs.create_log(env, message.from_id, 0, 8, f"Выпустил царя-легушку в {'чате' if env.eenv.is_multichat else 'лс'}")
    await env.reply(f"[id{message.from_id}|ЦАРЬ] велитъ😂😂\n\nЕбать васъ в сраку,\nБросить на съеденье ракам\nИ царицу, и приплодъ\nЗдесь печать и подпись. ВотЪ.", attachment=result)
