from .corounitne import schedule_coroutine
from .levels import *
from .plural_form import plural_form
from .schedule_api_task import schedule_api_task, schedule_task
from .debtcalc import DebtCalc
from .redisutil import *
from .vk_keyboard import VKKeyboard
import re
import aiohttp, json, io

async def parse_user_name(env, user_id):
    u = await env.request('users.get', user_ids=user_id)
    if not u.error:
        return f"{u.response[0]['first_name']} {u.response[0]['last_name']}"

    return None

async def check_admin(message, env, peer_id, uid):
    req = await env.eenv.request('messages.getConversationMembers', peer_id=message.peer_id, fields="sex,screen_name,nickname, invited_by")
    if not 'items' in req.response:
        return False

    for x in req.response['items']:
        if x['member_id'] == uid*-1:
            if 'is_admin' in x and x['is_admin']:
                return True

            return False

        if x['member_id'] == uid:
            if 'is_admin' in x and x['is_admin']:
                return True

            return False

    return False


async def parse_user_id(msg, env, can_be_argument=True, argument_ind=-1, custom_text=None):
    result_ids = []
    if msg.raw_update['object']['fwd_messages']:
        m = msg.raw_update['object']['fwd_messages']
        for user in m:
            result_ids.append(user['from_id'])
        return result_ids

    if not can_be_argument:
        return None

    if custom_text is None:
        original_text = msg.text
    else:
        original_text = custom_text

    text = original_text.split(" ")[argument_ind]
    if text.startswith('-'):
        result_ids.append(int(text))
        return result_ids
    if text.isdigit():
        result_ids.append(int(text))
        return result_ids

    if text.startswith("https://vk.com/"):
        text = text[15:]
    elif text.startswith("vk.com/"):
        text = text[7:]
    if text[:3] == "[id":
        puid = text[3:].split("|")[0]

        if puid.isdigit() and "]" in text[3:]:
            result_ids.append(int(puid))
            return result_ids

    if text[:5] == "[club":
        puid = text[5:].split("|")[0]
        if "]" in text[5:]:
            result_ids.append(-int(puid))
            return result_ids

    tuid = await env.request("utils.resolveScreenName", screen_name=text)
    if tuid.response:
        result_ids.append(tuid.response.get("object_id"))
        return result_ids
    if 'meta_data' in env.eenv:
        if argument_ind == -1:
            targets = [original_text.split(" ")[-1].strip().lower()]
        else:
            targets = [i.strip().lower() for i in original_text.split(" ")[argument_ind: argument_ind + 2]]
        max_match, user_id = 0, None
        try:
            for u in env.eenv.meta_data.users:
                if u.get("screen_name") == text:
                    result_ids.append(u['id'])
                matches = 0
                tg = " ".join(targets)
                if tg in u.get("first_name", "").strip().lower():
                    matches += 1
                if tg in u.get("last_name", "").strip().lower():
                    matches += 1
                if tg in u.get("nickname", "").strip().lower():
                    matches += 1
                if tg in u.get("name", "").strip().lower():
                    matches += 1
                if matches >= 0:
                    if matches > max_match:
                        max_match = matches
                        result_ids.append(u["id"])
                    elif matches == max_match:
                        max_match2 = 0
                        if env.eenv.meta_data.groups != 0:
                            for g in env.eenv.meta_data.groups:
                                if g.get("screen_name") == text:
                                    result_ids.append(-g['id'])
                                matches2 = 0
                                tg = " ".join(targets)
                                names = g.get("name", 0).strip().lower()
                                if text.lower() in names:
                                    matches2 += 1
                                if matches2 > 0:
                                    if matches2 > max_match2:
                                        max_match2 = matches2
                                        result_ids.append(g["id"])

                                    elif matches2 == max_match2:
                                        user_id = None
                                        continue
                        else:
                            user_id = None
                            continue
        except:
            return result_ids
        if not result_ids is None:
            return result_ids
    return None

domain_names = ['.fun', '.academy', '.accountant', '.accountants', '.active', '.actor', '.adult', '.aero', '.agency', '.airforce', '.apartments', '.app', '.archi', '.army', '.associates', '.asia', '.attorney', '.auction', '.audio', '.autos', '.biz', '.cat', '.com', '.coop', '.dance', '.edu', '.eus', '.gov', '.info', '.int', '.jobs', '.mil', '.mobi', '.museum', '.name', '.net', '.one', '.ong', '.onl', '.online', '.ooo', '.org', '.organic', '.partners', '.parts', '.party', '.pharmacy', '.photo', '.photography', '.photos', '.physio', '.pics', '.pictures', '.feedback', '.pink', '.pizza', '.place', '.plumbing', '.plus', '.poker', '.porn', '.post', '.press', '.pro', '.productions', '.prof', '.properties', '.property', '.qpon', '.racing', '.recipes', '.red', '.rehab', '.ren', '.rent', '.rentals', '.repair', '.report', '.republican', '.rest', '.review', '.reviews', '.rich', '.site', '.tel', '.travel', '.xxx', '.xyz', '.yoga', '.zone', '.ninja', '.art', '.moe', '.yandex', '.dev', '.ac', '.ad', '.ae', '.af', '.ag', '.ai', '.al', '.am', '.an', '.ao', '.aq', '.ar', '.as', '.at', '.au', '.aw', '.ax', '.az', '.ba', '.bb', '.bd', '.be', '.bf', '.bg', '.bh', '.bi', '.bj', '.bm', '.bn', '.bo', '.br', '.bs', '.bt', '.bv', '.bw', '.by ', '.бел', '.bz', '.ca', '.cc', '.cd', '.cf', '.cg', '.ch', '.ci', '.ck', '.cl', '.cm', '.cn', '.co', '.cr', '.cu', '.cv', '.cx', '.cy', '.cz', '.dd', '.de', '.dj', '.dk', '.dm', '.do', '.dz', '.ec', '.ee', '.eg', '.er', '.es', '.et', '.eu', '.fi', '.fj', '.fk', '.fm', '.fo', '.fr', '.ga', '.gb', '.gd', '.ge', '.gf', '.gg', '.gh', '.gi', '.gl', '.gm', '.gn', '.gp', '.gq', '.gr', '.gs', '.gt', '.gu', '.gw', '.gy', '.hk', '.hm', '.hn', '.hr', '.ht', '.hu', '.id', '.ie', '.il', '.im', '.in', '.io', '.iq', '.ir', '.is', '.it', '.je', '.jm', '.jo', '.jp', '.ke', '.kg', '.kh', '.ki', '.km', '.kn', '.kp', '.kr', '.kd', '.kw', '.ky', '.kz', '.la', '.lb', '.lc', '.li', '.lk', '.lr', '.ls', '.lt', '.lu', '.lv', '.ly', '.ma', '.mc', '.md', '.me', '.mg', '.mh', '.mk', '.ml', '.mm', '.mn', '.мон', '.mo', '.mp', '.mq', '.mr', '.ms', '.mt', '.mu', '.mv', '.mw', '.mx', '.my', '.mz', '.na', '.nc', '.ne', '.nf', '.ng', '.ni', '.nl', '.no', '.np', '.nr', '.nu', '.nz', '.om', '.pa', '.pe', '.pf', '.pg', '.ph', '.pk', '.pl', '.pm', '.pn', '.pr', '.ps', '.pt', '.pw', '.py', '.qa', '.re', '.ro', '.rs', '.срб', '.ru', '.рф', '.rw', '.sa', '.sb', '.sc', '.sd', '.se', '.sg', '.sh', '.si', '.sj', '.sk', '.sl', '.sm', '.sn', '.so', '.sr', '.st', '.su', '.sv', '.sy', '.sz', '.tc', '.td', '.tf', '.tg', '.th', '.tj', '.tk', '.tl', '.tm', '.tn', '.to', '.tp', '.tr', '.tt', '.tv', '.tw', '.tz', '.ua', '.укр', '.ug', '.uk', '.us', '.uy', '.uz', '.va', '.vc', '.ve', '.vg', '.vi', '.vn', '.vu', '.wf', '.ws', '.ye', '.yt', '.yu', '.za', '.zm', '.zw', '.xn--lgbbat1ad8j', '.xn--90ais', '.xn--fiqs8s', '.xn--fiqz9s', '.xn--wgbh1c', '.xn--j6w193g', '.xn--h2brj9c', '.xn--mgbbh1a71e', '.xn--fpcrj9c3d', '.xn--gecrj9c', '.xn--s9brj9c', '.xn--xkc2dl3a5ee0h', '.xn--45brj9c', '.xn--mgba3a4f16a', '.xn--mgbayh7gpa', '.xn--mgbc0a9azcg', '.xn--ygbi2ammx', '.xn--wgbl6a', '.xn--p1ai', '.xn--mgberp4a5d4ar', '.xn--90a3ac', '.xn--yfro4i67o', '.xn--clchc0ea0b2g2a9gcd', '.xn--3e0b707e', '.xn--fzc2c9e2c', '.xn--xkc2al3hye2a', '.xn--ogbpf8fl', '.xn--kprw13d', '.xn--kpry57d', '.xn--o3cw4h', '.xn--pgbs0dh', '.xn--j1amh', '.xn--mgbaam7a8h', '.xn--54b7fta0cc', '.xn--90ae', '.xn--node', '.xn--4dbrk0ce', '.xn--mgb9awbf', '.xn--mgbai9azgqp6j', '.xn--mgb2ddes', '.xn--kgbechtv', '.xn--hgbk6aj7f53bba', '.xn--0zwm56d', '.xn--g6w251d', '.xn--80akhbyknj4f', '.xn--11b5bs3a9aj6g', '.xn--jxalpdlp', '.xn--9t4b11yi5a', '.xn--deba0ad', '.xn--zckzah', '.xn--hlcj6aya9esc7a']
async def clear_prefix(prefix):
    clearRegex = r"\*(.*)\s\((.*)\)|\[(.*)\|(.+?)\]"

    tryToFind = re.findall(clearRegex, prefix)
    if len(tryToFind) < 1:
        if any(prefix.find(domain) != -1 for domain in domain_names):
            return None
        return prefix
    else:
        return None

async def get_nekos_attach(env, query):
    if query == "random_hentai_gif":
        query = "Random_hentai_gif"

    async with aiohttp.ClientSession() as sess:
        async with sess.get(f'https://nekos.life/api/v2/img/{query}') as resp:
            response = json.loads(await resp.read())

            if not response.get("url", None):
                return None

    attach = None
    async with aiohttp.ClientSession() as sess:
        async with sess.get(response['url']) as resp:
            if response['url'].endswith(".gif"):
                attach = await env.upload_doc(io.BytesIO(await resp.read()))
            else:
                attach = await env.upload_photo(io.BytesIO(await resp.read()))

    return attach