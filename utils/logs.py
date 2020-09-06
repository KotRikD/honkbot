from database import manager, Log, get_or_none
import peewee_async

TYPE_LOGS = {
    0: 'ADDED_PRIVILIGE',
    1: 'REMOVED_PRIVILIGE',
    2: 'ADDED_MONEY',
    3: 'REMOVED_MONEY',
    4: 'USER_BANNED',
    5: 'USER_UNBANNED',
    6: 'USER_MUTED',
    7: 'USER_UNMUTED',
    8: 'FROGGED',
    9: 'CAKED',
    10: 'DONATE_ADD',
    11: 'CREATE_PROMOCODE',
    12: 'DELETED_PROMOCODE',
    13: 'DELETED_ACCOUNT',
    100: 'CUSTOM_NOTIFY',
    128: 'NOTIFY_ME'
}

MINI_VERSIONS = {
    0: '📃 ⬆ {} => {} // group add',
    1: '📃 ⬇ {} => {} // group remove',
    3: '📃 💸 {} => {} // balance clear',
    4: '📃 ⛔ {} => {} // ban',
    5: '📃 ✅ {} => {} // unban',
    6: '📃 🔇 {} => {} // mute',
    7: '📃 🔊 {} => {} // unmute',
    8: '📃 🐸 {} => {} // frog',
    13: '📃 💸 {} => {} // balance clear'
}

async def create_log(env, from_id, to_id, type, addon_message=""):
    if not type in TYPE_LOGS:
        return False

    mini_version = MINI_VERSIONS.get(type, '')+'\n'

    users_notifies = await manager.execute(Log.select().where(Log.type == TYPE_LOGS[128]))
    LogMessage = f'''{mini_version.format(from_id, to_id)}Пришёл новый лог!👩‍⚖️
⬅️: [id{from_id}|{from_id}]
➡️: [id{to_id}|{to_id}]
👁‍🗨: {TYPE_LOGS[type]}
💬: {addon_message}
'''
    for x in users_notifies:
        await env.send_message(LogMessage, x.from_id)

    await manager.get_or_create(Log,
                                type=TYPE_LOGS[type],
                                from_id=from_id,
                                to_id=to_id,
                                body=addon_message)
    return True