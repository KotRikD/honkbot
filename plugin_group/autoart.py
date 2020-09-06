from kutana import Plugin
from lxml import html
from apscheduler.schedulers.background import BackgroundScheduler
from kutana.controller_vk.vkwrappers import make_upload_photo
from kutana.tools.functions import load_configuration
from utils import schedule_task, VKKeyboard, priviligeshelper
from utils.schedule_api_task import RawRequest
from database import *
from PIL import Image
import io
import random, json
import requests, aiohttp
import asyncio
import secrets
import time

plugin = Plugin(name="Autoart")

chat_id = 2000009996
chat_id_debug = 2000000011
group_id = 154288883


pics = 10
per_site = 2
sources = [['https://yande.re/post', 'ul#post-list-posts>li>a.directlink'], 
           ['https://danbooru.donmai.us/posts', 'div#posts-container>article'], 
           ['https://konachan.net/post', 'ul#post-list-posts>li>a.directlink'],
           ['https://safebooru.org/', 'div#post-list > div.content div > span a', 'img#image'],
           ['https://gelbooru.com/', 'div.contain-push > div.thumbnail-preview > span a', 'img#image']]

tags = '''watanabe_you|Watanabe You
kousaka_honoka|Kousaka Honoka
love_live!|Общий план персонажей LoveLive!
kousaka_honoka|Kousaka Honoka
love_live!_sunshine!!|Общий план персонажей LoveLive! Sunshine!!
kousaka_honoka|Kousaka Honoka
nishikino_maki|Nishikino Maki
matsuura_kanan|Matsuura Kanan
kousaka_honoka|Kousaka Honoka
tsushima_yoshiko|Tsushima Yoshiko
ayase_eli|Ayase Eli
kousaka_honoka|Kousaka Honoka
toujou_nozomi|Toujou Nozomi
minami_kotori|Minami Kotori
sonoda_umi|Sonoda Umi
kousaka_honoka|Kousaka Honoka
hoshizora_rin|Hoshizora Rin
koizumi_hanayo|Koizumi Hanayo
kousaka_honoka|Kousaka Honoka
kurosawa_dia|Kurosawa Dia
kunikida_hanamaru|Kunikida Hanamaru
kousaka_honoka|Kousaka Honoka
ohara_mari|Ohara Mari
takami_chika|Takami Chika
kousaka_honoka|Kousaka Honoka
sakurauchi_riko|Sakurauchi Riko'''.split("\n")

ruris_token = "<ruri_token hehe boi>"


async def parseImages(tag_info):
    name = tag_info[0]
    person = tag_info[1]
    headers = "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko"

    sess = requests.Session()
    sess.headers['user-agent'] = headers
    sess.cookies.set("country", "RU")
    sess.cookies.set("vote", "1")

    urls_of_images = []
    selector = 0
    while len(urls_of_images) < pics:
        if selector >= len(sources):
            if len(urls_of_images) < pics:
                selector = 0
                continue
            break
        
        config_selector = sources[selector]

        limited = 0        
        if len(config_selector) > 2: # for gelbooru sources
            params = {
                'page': 'post',
                's': 'list',
                'tags': f"{name} rating:safe",
                'pid': random.randint(1, 19)*40
            }
            fs_paged = sess.get(config_selector[0]+"index.php", params=params)
            fs_paged_res = html.fromstring(fs_paged.text)

            post_links = fs_paged_res.cssselect(config_selector[1])
            images = []
            for x in post_links:
                if x.attrib.get('href', '').startswith("//"): # gelbooru pattern
                    link = f"https:{x.attrib.get('href', '')}"
                else: # safebooru
                    link = f"{config_selector[0]}{x.attrib.get('href', '')}"
                page_post = sess.get(link)
                page_post_res = html.fromstring(page_post.text)

                if limited == per_site:
                    break

                image = page_post_res.cssselect(config_selector[2])
                if not image:
                    continue
                
                pic_link = image[0].attrib.get("src", "")
                urls_of_images.append(pic_link)
                limited+=1
        else:
            params = dict(
                tags=name+" rating:safe",
                page=random.randint(1, 19),
                commit="Search"
            )
            fs_paged = sess.get(config_selector[0], params=params)
            fs_paged_res = html.fromstring(fs_paged.text)

            images = fs_paged_res.cssselect(config_selector[1])

            if not images:
                selector+=1
                continue
        
            for x in images:
                if limited == per_site:
                    break

                if 'danbooru' in config_selector[0]:
                    # Да, для данбору нужен другой алгоритм ;d
                    if x.attrib.get('data-large-file-url', False):
                        if x.attrib['data-large-file-url'] in urls_of_images: continue
                        urls_of_images.append(x.attrib['data-large-file-url'])
                    else:
                        continue
                else:
                    if x.attrib["href"] in urls_of_images: continue
                    urls_of_images.append(x.attrib["href"])

                limited+=1
        
        selector+=1

    return urls_of_images

async def notificator(*args):
    while True:
        timedb2 = await get_or_none(DynamicSettings, key="LAST_AUTOPOST_TIME")
        if not timedb2:
            await manager.create_or_get(DynamicSettings, key="LAST_AUTOPOST_TIME", value=str(int(time.time())))
            timedb = int(time.time())
        else:
            timedb = int(timedb2.value)

        remaining_time = (timedb+1800)-int(time.time())
        if remaining_time > 0:
            await asyncio.sleep(remaining_time)

        plugin.votes = {}
        plugin.positive_votes = 0
        plugin.cancel_votes = 0
        upload_photo = make_upload_photo(args[0]['kutana']['kutana'].controllers[0], chat_id)
        request = RawRequest(load_configuration("vk_token", "configuration.json")).schedule_raw_request
        ruris_request = RawRequest(ruris_token).schedule_raw_request
        
        tag_splitted = random.choice(tags).split("|")
        tag = tag_splitted[0]
        person = tag_splitted[1]
        images = await parseImages(tag_splitted)

        plugin.hash = secrets.token_hex(16)

        attach_ids = []
        for link in images:
            attach = None
            async with aiohttp.ClientSession() as sess:
                async with sess.get(link) as resp:
                    attach = await upload_photo(io.BytesIO(await resp.read()))
            
            if attach:
                attach_ids.append(f'{attach.type}{attach.owner_id}_{attach.id}')

        kb = VKKeyboard()
        x = 1
        buttons = []
        for _ in images:
            buttons.append({'text': f'{x}', 'payload': {'command': f'!пикчуресхуюреснахуйловлайвлизэйшнблять {x} {plugin.hash}'}, 'color': 'positive'})
            x+=1

        buttons.append({'text': 'Отмена', 'payload': {'command': f'!пикчуресхуюреснахуйловлайвлизэйшнблять cancel {plugin.hash}'}, 'color': 'negative'})
        kb.lazy_buttons({
            'one_time': False,
            'buttons': buttons
        })
        text = f'''
    Привет, я тут захотела выложить пару фоточек, не поможешь мне выбрать какая подходит для паблика?

Обратите внимание!!!! Нужен именно персонаж/общий план:
{person}

На голосование есть 10 минут!
#{tag}@honkbot'''

        await request("messages.send", 
                    peer_id=chat_id, 
                    message=text,
                    attachment=','.join(attach_ids),
                    keyboard=kb.dump_keyboard())
        
        await asyncio.sleep(10*60)
        timedb2.value = str(int(time.time()))
        await manager.update(timedb2)

        plugin.over_cancel = False
        if plugin.positive_votes+plugin.cancel_votes < 2:
            plugin.votes = {}
            plugin.positive_votes = 0
            plugin.cancel_votes = 0
            plugin.hash = "-1-1-1-1-1-1-1-1-1-1--11-1-1-1-1-1-1-1-1"
            
            await request("messages.send", 
                    peer_id=chat_id, 
                    message="К сожалению не достаточно голосов, может тогда опубликуем что-нибудь через часик?",
                    keyboard='{"buttons": []}')
            continue

        if plugin.cancel_votes > plugin.positive_votes:
            plugin.votes = {}
            plugin.positive_votes = 0
            plugin.cancel_votes = 0
            plugin.hash = "-1-1-1-1-1-1-1-1-1-1--11-1-1-1-1-1-1-1-1"
            await request("messages.send", 
                    peer_id=chat_id, 
                    message="Я походу выбрала не очень да? Может тогда опубликуем что-нибудь через часик?",
                    keyboard='{"buttons": []}')
            continue

        results = {}
        for (_, v) in plugin.votes.items():
            if v not in results:
                results[v] = 1
                continue
            results[v]+=1
        final_results = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]

        kb = VKKeyboard()
        kb.lazy_buttons({
            'one_time': False,
            'buttons': [
                {'text': 'ACHTUNG! WRONG PICTURE(nsfw and etc..)', 'payload': {'command': f'!пикчуресхуюреснахуйловлайвлизэйшнблять отмени_пост {plugin.hash}'}, 'color': 'negative'}
            ]
        })

        await request("messages.send", 
                    peer_id=chat_id, 
                    message=f"Ура! Победила картинка №{final_results[0][0]} с {final_results[0][1]} голосами!",
                    attachment=attach_ids[final_results[0][0]-1],
                    keyboard=kb.dump_keyboard())
        
        await asyncio.sleep(15)
        plugin.votes = {}
        plugin.positive_votes = 0
        plugin.cancel_votes = 0
        plugin.hash = "-1-1-1-1-1-1-1-1-1-1--11-1-1-1-1-1-1-1-1"
        if plugin.over_cancel:
            await request("messages.send", 
                    peer_id=chat_id, 
                    message="Админ сказал что пикча не оч, отменяемс",
                    keyboard='{"buttons": []}')
            continue
        
        params = {
            'group_id': group_id,
            'caption': f"Источник: {images[final_results[0][0]-1]}",
        }

        # Start uploading
        result = await ruris_request("photos.getWallUploadServer", **params)
        upload_url = result['upload_url']
        
        data = aiohttp.FormData()
        async with aiohttp.ClientSession() as sess:
            async with sess.get(images[final_results[0][0]-1]) as resp:
                #lets convert image
                image = Image.open(io.BytesIO(await resp.read()))
                
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                
                data.add_field("photo", buffer, filename="img.jpg")

        upload_result = None
        async with aiohttp.ClientSession() as sess:
            async with sess.post(upload_url, data=data) as resp:
                upload_result = json.loads(await resp.read())

                if "error" in upload_result:
                    await request("messages.send", 
                                    peer_id=chat_id, 
                                    message="Не удалось загрузить пикчу на сервера ВК!",
                                    keyboard='{"buttons": []}')
                    continue
                    
                params.update(upload_result)

        image_for_post = await ruris_request("photos.saveWallPhoto", **params)

        if len(image_for_post) < 1:
            await request("messages.send", 
                            peer_id=chat_id, 
                            message="Не удалось загрузить пикчу на сервера ВК!",
                            keyboard='{"buttons": []}')
            continue

        image_for_post = f"photo{image_for_post[0]['owner_id']}_{image_for_post[0]['id']}"

        await ruris_request("wall.post", owner_id=f"-{group_id}", message=f"{person} #{tag} #lovelive", attachments=image_for_post, from_group=1)
        await request("messages.send", 
                        peer_id=chat_id, 
                        message="Пост был опубликован!",
                        keyboard='{"buttons": []}')

@plugin.on_startup()
async def on_startup(kutana, update):
    plugin.votes = {}
    plugin.voters = 0

    schedule_task(notificator, kutana=kutana, update=update)

@plugin.on_startswith_text("пикчуресхуюреснахуйловлайвлизэйшнблять")
async def func(msg, attach, env):
    if msg.peer_id != chat_id:
        return "DONE"

    if env.args is None or len(env.args) < 2:
        return await env.reply("Нет аргументов")

    if env.args[1] != plugin.hash:
        return await env.reply("Неверный хэш! Наверное вы попытались выбрать старое голосование")
    
    privs = await priviligeshelper.getUserPriviliges(env, msg.from_id)
    if (privs & priviligeshelper.USER_MODERATOR > 0):
        COUNT_VOTE = 2
    else:
        COUNT_VOTE = 1

    def make_vote(vote_id):
        positive_vote = True if vote_id > 0 else False

        if msg.from_id in plugin.votes:
            is_positive = True if plugin.votes[msg.from_id] > 0 else False

            if positive_vote is False:
                if is_positive is False:
                    return "Ты уже голосовал за отмену поста. Остынь!"
                else:
                    plugin.votes[msg.from_id] = -1
                    plugin.positive_votes -= COUNT_VOTE
                    plugin.cancel_votes += COUNT_VOTE
                    return "Теперь ты за отмену поста!"
            
            if positive_vote:
                if is_positive is False:
                    plugin.votes[msg.from_id] = vote_id
                    plugin.positive_votes += COUNT_VOTE
                    plugin.cancel_votes -= COUNT_VOTE
                    return f"Теперь ты выбрал вариант №{vote_id}"
                else:
                    if plugin.votes[msg.from_id] != vote_id:
                        plugin.votes[msg.from_id] = vote_id
                        return f"Теперь ты выбрал вариант №{vote_id}"
                    else:
                        return "Успокойся, ты уже голосовал"
        
        if positive_vote:
            plugin.votes[msg.from_id] = vote_id
            plugin.positive_votes += COUNT_VOTE
            return f"Ты выбрал вариант №{vote_id}"
        else:
            plugin.votes[msg.from_id] = -1
            plugin.cancel_votes += COUNT_VOTE
            return "Ты за отмену поста!"       

    result = None
    if env.args[0] == "cancel":
        result = make_vote(-1)
    elif env.args[0] == "отмени_пост":
        if not (privs & priviligeshelper.USER_ADMIN > 0):
            return await env.reply("Ты не админ")
        else:
            plugin.over_cancel = True
            result = "Ок, отменяю...отменяю..."
    elif env.args[0].isdigit():
        result = make_vote(int(env.args[0]))
    else:
        result = "Ну вот и чо ты ломаешь? Умный дохуя?"

    return await env.reply(result)
