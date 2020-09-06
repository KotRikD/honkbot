from kutana import Plugin
import romajitable
import transliterate

plugin = Plugin(name="Кана", cmds=[{'command': 'jp <текст>', 'desc': 'переводит текст на япу(фан)'}])

@plugin.on_startswith_text("jp")
async def on_message(message, attachments, env):

    if not env['args']:
        return await env.reply("Введите текст пожалуйста")

    text = ' '.join(env['args'])
    try:
        text = transliterate.translit(text, reversed=True)
    except Exception:
        pass

    rt = romajitable.to_kana(text)
    return await env.reply("А вот и результат подъехал\n\n"
                            f"🔑🇯🇵|Хирагана: {rt.hiragana}\n"
                            f"🔑🇯🇵|Катакана: {rt.katakana}")