
import time

from kutana import Plugin

from utils import edict, ddict

plugin = Plugin(name="Игнор пидоров", priority=630)

@plugin.on_has_text()
async def on_has_text(message, attachments, env):
    ct = time.time()

    banned = False
    u = await ddict(await env.eenv.dbredis.get(f"honoka:banned_users:{message.from_id}"))
    lockedchat = await ddict(await env.eenv.dbredis.get(f"honoka:banned_chats:{message.peer_id}"))

    if u:
        banned = True

    muted = await ddict(await env.eenv.dbredis.get(f"honoka:muted_users:{message.from_id}"))

    if not banned and message.text.lower().startswith(env.eenv.prefix+"включить бота") or \
       not banned and message.text.lower().startswith(env.eenv.prefix+"разбанить беседу"):
        return "GOON"
    elif muted:
        return "DONE"
    elif banned or lockedchat:
        return "DONE"

    return False

