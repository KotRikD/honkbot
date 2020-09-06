from kutana import Plugin

import json
import aiohttp
import io
import re
import asyncio
import peewee, peewee_async
from database import *
from utils import schedule_api_task, parse_user_id, priviligeshelper
import utils.logs as Logs
from kutana import logger


plugin = Plugin(name="Проверь донат", cmds=[{'command': 'проверь донат', 'desc': 'проверить донат'}])

PATH = "plugins/donatepay/"

async def add_to_list(env, idv):
    previous_user = await get_or_none(Priviliges, user_id=idv)
    if not previous_user:
        new_user = priviligeshelper.addPrivilige(priviligeshelper.USER_NORMAL, priviligeshelper.USER_VIP)
        await manager.create_or_get(Priviliges, user_id=idv, priv=new_user, last_update_reason='Donater!')
    else:
        new_privs = priviligeshelper.addPrivilige(previous_user.priv, priviligeshelper.USER_VIP)
        previous_user.priv = new_privs
        await manager.update(previous_user)

    return await env.reply("Поздравляем! Вы получили вип статус!")

async def one_type_response(request):
    logger.info("Проверяем новые донаты!")

    #Qiwi VER
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://edge.qiwi.com/payment-history/v2/persons/<x>/payments?parameter=value&rows=3&operation=IN",
                            headers={'Accept': 'application/json', 'Authorization': 'Bearer xxx'}) as resp:
            result = await resp.json()
    if not 'data' in result:
        await asyncio.sleep(100)
        return
    for payment in result['data']:
        if not payment['comment']:
            continue

        if await get_or_none(DonateQiwi, txnId=payment['txnId']):
            continue

        loliuo = payment['comment'].split(" ")[0].replace(f'https://', '').replace(f'http://', '')
        id_user = loliuo.split("/")
        if len(id_user) < 2:
            continue
        info = await request('users.get', user_ids=id_user[1])
        if info and len(info) > 0:
            logger.info(f"Обнаружен новый донат! От пользователя id{info[0]['id']}")
            s = await get_or_none(Donate, user_id=info[0]['id'])
            if s:
                if not s.last_trans_id == payment['txnId']:
                    s.amout += int(payment['sum']['amount'])
                    s.last_trans_id = payment['txnId']
                    await request('messages.send', user_id=info[0]['id'],
                                    message=f'寄付いただきありがとうございます「Спасибо за донат」！ Сумма донатов: {s.amout}руб.')
                    await manager.update(s)
            else:
                await peewee_async.create_object(Donate, user_id=info[0]['id'], amout=int(payment['sum']['amount']),
                                                    last_trans_id=payment['txnId'])
                await request('messages.send', user_id=info[0]['id'],
                                message=f'寄付いただきありがとうございます「Спасибо за донат」！')
        await manager.get_or_create(DonateQiwi, txnId=payment['txnId'])

async def check_for_new(request):
    while True:
        await one_type_response(request)
        await asyncio.sleep(100)

@plugin.on_startup()
async def on_startup(a1, a2):
    await schedule_api_task(check_for_new)
    return "GOON"


@plugin.on_startswith_text("проверь донат")
async def on_message(message, attachments, env):
    d = await get_or_none(Donate, user_id=message.from_id)
    if d and d.amout >= 60:
        if await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP <= 0:
            r="Вип: Нет\n"
            await add_to_list(env, message.from_id)
        else:
            r="Вип: Да\n"

        r+=f"Сумма донатов: {d.amout}руб.\n"

        return await env.reply(r)
    else:
        if await priviligeshelper.getUserPriviliges(env, message.from_id) & priviligeshelper.USER_VIP > 0:
            r="Вип: Да\n"
        else:
            r="Вип: Нет\n"

        r+="Сумма донатов: 0 рублей\n"
        return await env.reply(r)


@plugin.on_startswith_text("ручной донат")
async def custom_donate(message, attachments, env):
    privs = await priviligeshelper.getUserPriviliges(env, message.from_id)
    if not (privs & priviligeshelper.USER_ADMIN > 0):
        return await env.reply("У тебя нету таких прав!")

    if not env['args']:
        return await env.reply("Нету аргументов!")
    
    if env['args'][0] == 'qiwi_check':
        await one_type_response(env.request)
    
    # TODO: Сделать полностью ручной донат!
    return await env.reply("Была выполнена qiwi_проверка доната!")
