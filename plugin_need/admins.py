from kutana import Plugin, Message

plugin = Plugin(name="Вспомогательная дичь!", priority=700)

@plugin.on_has_text()
async def on_has_text(message, attachments, env):
    env.eenv['admins'] = (311572436, 392278257, )
    env.eenv['notify_admins'] = (311572436, 392278257, 487922908, 250235910)
    env.eenv.prefix = "!"
    if message.peer_id == message.from_id:
        env.eenv.is_multichat = False
    else:
        env.eenv.is_multichat = True

    return "GOON"
