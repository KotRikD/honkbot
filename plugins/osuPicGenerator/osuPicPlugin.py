from kutana import Plugin
from utils.osuPicGenerator import osuPicGenerator
from database import OsuProfile, get_or_none, manager

plugin = Plugin(name="генератор карточек osu V2", cmds=[
    {'command': 'osu![ofc/kurikku/gatari/akatsuki/ripple] [nickname] [mode(желательно(std, mania, taiko, ctb))]', 'desc': 'генерирует карточку с статистикой для игры osu! на разных серверах'},
    {'command': 'sn!osu [server(ofc/kurikku/gatari/akatsuki/ripple)] [nick] [mode]', 'desc': 'Установка никнейма для генератора карточек osu! на разных серверах'}
])

@plugin.on_startswith_text("osu")
async def on_message(msg, attach, env):
    server = "ofc"
    nickname = ""
    mode = ""
    
    lowered_args = [] 
    for arg in env.args:
        lowered_args.append(arg.lower())
    
    env.args = lowered_args 
    if len(env.args) == 3:
        #full complect
        if env.args[0][1:] not in ['ofc', 'kurikku', 'gatari', 'akatsuki', 'ripple']:
            return await env.reply("укажи сервер, где хочешь посмотреть стату!\nНапример: !osu!ofc KotRik std")
        
        if env.args[2] not in ['std', 'mania', 'ctb', 'taiko', 'ripple']:
            return await env.reply("укажи игровой режим, где хочешь посмотреть стату!\nНапример: !osu!ofc KotRik std")
        
        server = env.args[0][1:]
        nickname = env.args[1]
        mode = env.args[2]
    elif len(env.args) == 2:
        if env.args[0][1:] in ['ofc', 'kurikku', 'gatari', 'akatsuki', 'ripple']:
            server = env.args[0][1:]
            nickname = env.args[1]
            mode = "std"
        elif env.args[1] in ['std', 'mania', 'ctb', 'taiko', 'ripple']:
            nickname = env.args[0]
            mode = env.args[1]
        else:
            return await env.reply("не смогла разобрать аргументы, проверь пожалуйста, что ты набрал похожее:\n!osu!ofc KotRik\n!osu KotRik std")
    elif len(env.args) == 1:
        user_config = await get_or_none(OsuProfile, vk_id=msg.from_id)
        if env.args[0][1:] in ['ofc', 'kurikku', 'gatari', 'akatsuki', 'ripple']:
            # Инфа из бд, с ником из бд(vk_id) и сервером env.args[0]
            if not user_config:
                return await env.reply("ничего не можем сказать, ты не установил никнейм!")

            if env.args[0][1:] == "kurikku":
                if not user_config.kurikku_name or not user_config.kurikku_mode:
                    return await env.reply("для этого id, нет информации о настройках для сервера kurikku")
                
                server = "kurikku"
                nickname = user_config.kurikku_name
                mode = user_config.kurikku_mode
            elif env.args[0][1:] == "gatari":
                if not user_config.gatari_name or not user_config.gatari_mode:
                    return await env.reply("для этого id, нет информации о настройках для сервера ofgataric")

                server = "gatari"
                nickname = user_config.gatari_name
                mode = user_config.gatari_mode
            elif env.args[0][1:] == "akatsuki":
                if not user_config.akatsuki_name or not user_config.akatsuki_mode:
                    return await env.reply("для этого id, нет информации о настройках для сервера akatsuki")

                server = "akatsuki"
                nickname = user_config.akatsuki_name
                mode = user_config.akatsuki_mode
            elif env.args[0][1:] == "ripple":
                if not user_config.ripple_name or not user_config.ripple_mode:
                    return await env.reply("для этого id, нет информации о настройках для сервера akatsuki")

                server = "ripple"
                nickname = user_config.ripple_name
                mode = user_config.ripple_mode
        else:
            mode = "std"
            nickname = env.args[0]
    else:
        user_config = await get_or_none(OsuProfile, vk_id=msg.from_id)
        # Инфа из бд, с ником из бд(vk_id) и сервером env.args[0]
        if not user_config:
            return await env.reply("ничего не можем сказать, ты не установил никнейм!")

        if not user_config.osu_name or not user_config.osu_mode:
            return await env.reply("для этого id, нет информации о настройках для сервера ofc")

        server = "ofc"
        nickname = user_config.osu_name
        mode = user_config.osu_mode
    
    picture = osuPicGenerator(server.lower(), nickname.lower(), msg.from_id, mode.lower())
    try:
        await picture.getStats()
        await picture.generate()
    except:
        return await env.reply("не нашла такого игрока")
    
    result = await env.upload_photo(picture.generatedPic)
    return await env.reply('держи', attachment=result)
    
    
@plugin.on_startswith_text("sn!osu")
async def on_message(msg, attach, env):
    if len(env.args) < 3:
        return await env.reply("неверное количество аргументов")
    
    if env.args[0] not in ['ofc', 'kurikku', 'gatari', 'akatsuki', 'ripple']:
        return await env.reply("неправильно указан сервер!\nПравильный пример: !sn!osu ofc KotRik std")
    
    if env.args[2] not in ['std', 'mania', 'ctb', 'taiko', 'ripple']:
        return await env.reply("неправильно указан режим!\nПравильный пример: !sn!osu ofc KotRik std")
    
    user_confs = await get_or_none(OsuProfile, vk_id=msg.from_id)
    if not user_confs:
        user_confs = await manager.create_or_get(OsuProfile, vk_id=msg.from_id)
        user_confs = user_confs[0]

    if env.args[0] == "ofc":
        user_confs.osu_name = env.args[1]
        user_confs.osu_mode = env.args[2]
    elif env.args[0] == "kurikku":
        user_confs.kurikku_name = env.args[1]
        user_confs.kurikku_mode = env.args[2]
    elif env.args[0] == "akatsuki":
        user_confs.akatsuki_name = env.args[1]
        user_confs.akatsuki_mode = env.args[2]
    elif env.args[0] == "gatari":
        user_confs.gatari_name = env.args[1]
        user_confs.gatari_mode = env.args[2]
    elif env.args[0] == "ripple":
        user_confs.ripple_name = env.args[1]
        user_confs.ripple_mode = env.args[2]
    
    await manager.update(user_confs)
    return await env.reply("информация обновлена!")
