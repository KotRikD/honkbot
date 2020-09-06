import requests
from lxml import html
import io
import random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from kutana import Plugin

plugin = Plugin(name="Генератор слоганов", cmds=[
    {'command': 'слоган [категория] [слоган]', 'desc': 'Генерирует слоган одной из категории(категории можно узнать, простот написав !слоган)'}
])

PATH = "plugins/slogan/"

CATEGORIES = ["Абстракция", "Животные", "Искусство, дизайн", "Бизнес, бухгалтерия, маркетинг", "Благотворительность", "Клининговые услуги", "Строительство, недвижимость", "Образование, наука", "Развлечение", "Дом, семья", "Мода", "Еда и напитки", "Сельское хозяйство", "Отели, отдых", "Производство", "Юриспруденция, банковское дело, страхование", "Медицина", "Музыка", "Фотография", "Спорт", "IT, Технологии", "Туризм, путешествие", "Транспорт"]

TEMPLATES = {
        #bg-color       #font-color
    1: [(229, 215, 90), (0, 0, 0)],
    2: [(125, 12, 24), (255, 255, 255)],
    3: [(119, 151, 146), (255, 255, 255)],
    4: [(84, 69, 64), (255, 255, 255)],
    5: [(243, 224, 182), (84, 69, 64)],
    6: [(244, 141, 36), (84, 69, 64)],
    7: [(158, 205, 173), (125, 12, 24)],
    8: [(233, 227, 227), (84, 69, 64)],
    9: [(137, 119, 86), (255, 255, 255)]
}

SIZES = (700, 400)

async def create_slogan(env, template_id: int, slogan_top: str, slogan_bottom: str):
    colors = TEMPLATES.get(random.randint(1, 9))

    tex = Image.new("RGB", (700, 400), color=colors[0])
    draw = ImageDraw.Draw(tex)

    big_font_size = 64
    small_font_size = 30

    font = ImageFont.truetype(PATH+"ariblk.ttf", big_font_size)
    font2 = ImageFont.truetype(PATH+"arial.ttf", small_font_size)

    w, _ = draw.textsize(slogan_top, font=font)
    w1, _ = draw.textsize(slogan_bottom, font=font2)

    while w+20 > SIZES[0]:
        big_font_size-=1
        font = ImageFont.truetype(PATH+"ariblk.ttf", big_font_size)
        w, _ = draw.textsize(slogan_top, font=font)

    while w1+20 > SIZES[0]:
        small_font_size-=1
        font2 = ImageFont.truetype(PATH+"arial.ttf", small_font_size)
        w1, _ = draw.textsize(slogan_bottom, font=font2)

    draw.text(( (SIZES[0]-w)/2 , 130), slogan_top, fill=colors[1], font=font)
    draw.text(( (SIZES[0]-w1)/2, 210), slogan_bottom, fill=colors[1], font=font2)

    buffer = io.BytesIO()
    tex.save(buffer, format='png')
    buffer.seek(0)

    result = await env.upload_photo(buffer)
    return f'{result.type}{result.owner_id}_{result.id}'

sess = requests.Session()

sess.headers["Accept"] = 'application/json, */*; q=0.01'
sess.headers["Content-Type"] = 'application/x-www-form-urlencoded; charset=UTF-8'
sess.headers["Origin"] = 'https://www.logaster.ru'
sess.headers["Referer"] = 'https://www.logaster.ru/slogan-generator/'
sess.headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 OPR/66.0.3515.72'

@plugin.on_startswith_text("слоган")
async def lebedev(msg, att, env):
    if not env.args or len(env.args) < 2 or not env.args[0].isdigit() or int(env.args[0])-1 > len(CATEGORIES) or int(env.args[0]) <= 0:
        build_str = ""
        iter_str = 0
        for x in CATEGORIES:
            build_str += f"{iter_str+1}. - {x}\n"
            iter_str +=1
        return await env.reply(f"Возможные категории:\n\n{build_str}\n\nВведите команду: 'слоган [номер категории] [слоган]'")

    r1 = sess.get("https://www.logaster.ru/slogan-generator")
    fs_paged_res = html.fromstring(r1.text)

    happy_csrf = fs_paged_res.cssselect('meta[name="csrf-token"]')
    if len(happy_csrf) < 1:
        return await env.reply("попробуйте позже, апи сдохло")

    sess.headers['X-CSRF-TOKEN'] = happy_csrf[0].attrib["content"]
    sess.headers['X-Requested-With'] = "XMLHttpRequest"

    r = sess.post("https://www.logaster.ru/slogan-generator/create-slogan", data={
        'page': str(random.randint(2, 10)),
        'lang_code': 'ru',
        'brand': ' '.join(env.args[1:]),
        'category': int(env.args[0]) 
    })

    slogans = []
    slogans_att = []
    object_need = r.json()["result_data"]["slogans"]

    for x in object_need:
        slogans.append([x['template_id'], x['brand_name'], x['slogan']])

    for x in slogans:
        att_id = await create_slogan(env, x[0], x[1], x[2])
        slogans_att.append(att_id)

    return await env.reply("держи!", attachment=','.join(slogans_att))
