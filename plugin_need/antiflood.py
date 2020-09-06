import time
from kutana import Plugin

plugin = Plugin(name="Антифлуд", priority=650)

cooldown_n = 4
cooldown_p = 2
cd_users = {}

@plugin.on_has_text()
async def on_has_text(message, attachments, env):
    if env.eenv['is_payload']:
        cooldown = cooldown_p
    else:
        cooldown = cooldown_n
    ts = int(time.time())

    if message.from_id in cd_users:
        if ts - cd_users[message.from_id]['message_date'] <= cooldown:
            cd_users[message.from_id]['message_date'] = ts
            return "DONE"

        cd_users[message.from_id]['message_date'] = ts
    else:
        cd_users[message.from_id] = {}
        cd_users[message.from_id]['message_date'] = ts

    return "GOON"
