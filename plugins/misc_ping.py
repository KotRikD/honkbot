import time
import datetime
import asyncio
from kutana import Plugin

plugin = Plugin(name="Просто установка статуса беч")

launch_time = datetime.datetime.now()

@asyncio.coroutine
def ping(target, dump=False):
    create = asyncio.create_subprocess_exec('ping', '-c', '1', target,
                                            stdout=asyncio.subprocess.PIPE)
    proc = yield from create
    lines = []
    while True:
        line = yield from proc.stdout.readline()
        if line == b'':
            break
        l = line.decode('utf8').rstrip()
        if dump:
            print(l)
        lines.append(l)

    transmited, received = [int(a.split(' ')[0]) for a
                            in lines[-2].split(', ')[:2]]
    stats, unit = lines[-1].split(' = ')[-1].split(' ')
    min_, avg, max_, stddev = [float(a) for a in stats.split('/')]
    return avg

@plugin.on_text("п", "пинг", "p", "ping")
async def on_message(message, attachments, env):
    p = await ping('vk.com')
    uptime = (datetime.datetime.now() - launch_time).total_seconds()
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    vk = f"⚡ Pong!\n🅿 Ping: {int(p)} ms.\n⏰ Time: {datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')}.\n♻ Uptime: ({'%02d:%02d:%02d' % (hours, minutes, seconds)})."
    return await env.reply(vk)
