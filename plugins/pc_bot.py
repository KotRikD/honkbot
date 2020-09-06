from kutana import Plugin

import os
import cpuinfo

plugin = Plugin(name="комп бота", cmds=[{
    'command': 'комп бота', 'desc': "Показать пк бота", 'cheat':True
}])


@plugin.on_startswith_text("комп бота")
async def bot_pc(msg, attach, env):
    result = "🖥Информация о системе:\n"
    result+= f"&#12288;💻OC: {os.uname().sysname}\n"
    result+= f"&#12288;💻Arch: {os.uname().machine}\n"
    if os.name == "posix":
        result+= f"&#12288;💻Platform: linux/*nix\n"
    elif os.name == "nt":
        result+= f"&#12288;💻Platform: NT/Windows\n"
    elif os.name == "mac":
        result+= f"&#12288;💻Platform: Mac OS\n"
    result+=f"&#12288;💻Release: {os.uname().release}\n"

    result+= "\n⚙Информация о железе:\n"
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    result+= f"&#12288;🔧RAM: {used_m}MB / {tot_m}MB ({free_m}MB free)\n"
    result+= f"&#12288;🔧CPU: {cpuinfo.get_cpu_info()['brand']}"

    return await env.reply(result)