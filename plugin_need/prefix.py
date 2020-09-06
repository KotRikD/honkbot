from kutana import Plugin, Message

plugin = Plugin(name="Система префиксов!", priority=500)


@plugin.on_has_text()
async def on_has_text(message, attachments, env):
    if not message.text.startswith(env.eenv.prefix):
        return "DONE"  # "GOON" if you want to just keep message

    env.eenv['prefixes'] = env.eenv.prefix

    env.eenv._cached_message = Message(
        message.text[len(env.eenv.prefix):],
        message.attachments,
        message.from_id,
        message.peer_id,
        message.raw_update
    )

    return "GOON"
