from database import manager, Priviliges, get_or_none
from utils import ddict

USER_BANNED = 0
USER_NORMAL = 2
USER_VIP = 128
USER_MODERATOR = 1024
USER_ADMIN = 2048
#3202 - MAX PRIVILIGES

def getPriviliges(priv):
    priviliges = [USER_VIP, USER_MODERATOR, USER_ADMIN]
    have_priviliges = 0
    for x in priviliges:
        if (priv & x) > 0:
            have_priviliges+=x
            priv-=x

    if (USER_ADMIN&have_priviliges)>0:
        have_priviliges = USER_NORMAL+USER_VIP+USER_MODERATOR+USER_ADMIN
    return have_priviliges

def strpriv(priv):
    user_privs = []

    if (priv & USER_BANNED) > 0:
        user_privs.append("USER_BANNED")
    if (priv & USER_NORMAL) > 0:
        user_privs.append("USER_NORMAL")
    if (priv & USER_VIP) > 0:
        user_privs.append("USER_VIP")
    if (priv & USER_MODERATOR) > 0:
        user_privs.append("USER_MODERATOR")
    if (priv & USER_ADMIN) > 0:
        user_privs.append("USER_ADMIN")

    return user_privs

def intpriv(priv):
    user_privs = []

    if (priv & USER_NORMA) > 0:
        user_privs.append(USER_NORMAL)
    if (priv & USER_VIP) > 0:
        user_privs.append(USER_VIP)
    if (priv & USER_MODERATOR) > 0:
        user_privs.append(USER_MODERATOR)
    if (priv & USER_ADMIN) > 0:
        user_privs.append(USER_ADMIN)

    return user_privs

def addPrivilige(priv_old, priv_new):
    priv_old = getPriviliges(priv_old)
    privs_old = intpriv(priv_old)
    privs_new = intpriv(priv_old+priv_new)
    if len(privs_new)==len(privs_old):
        return priv_old

    if (priv_old & priv_new) > 0:
        return priv_old

    priv_news=priv_old+priv_new
    return priv_news

def removePrivilige(priv, priv_to_delete):
    if (priv&priv_to_delete)>0:
        return priv-priv_to_delete
    else:
        return priv

async def canTouch(user_priv, user_id_who_touchs):
    user1 = await get_or_none(Priviliges, user_id=user_id_who_touchs)
    if not user1:
        user_1 = USER_NORMAL
    else:
        user_1 = user1.priv

    if user_priv==user_1:
        return False
    if user_priv>user_1:
        return True
    else:
        return False

async def getUserPriviliges(env, user_id, need_to_check=False, need_user_id=None):
    '''

    :param env: Параметра enviroment из сообщения, крч там где есть redis хранилище
    :param user_id:
    :param need_to_check: Параметр отвечающий за нужно ли проверять может ли пользователь трогать вышшего по званию
    :return:
    '''
    u = await ddict(await env.eenv.dbredis.get(f"honoka:banned_users:{user_id}"))
    if u:
        return USER_BANNED if not need_to_check else False

    user = await get_or_none(Priviliges, user_id=user_id)
    if not user:
        return USER_NORMAL if not need_to_check else False

    user_priviliges = getPriviliges(user.priv)
    user_needd = None
    can_user = False
    if need_to_check:
        if not need_user_id:
            return None if not need_to_check else False

        user_need = await get_or_none(Priviliges, user_id=need_user_id)
        if not user_need:
            return None if not need_to_check else False

        user_needd = getPriviliges(user_need.priv)
        if user_priviliges < user_needd:
            can_user = False
        else:
            can_user = True

    return user_priviliges if not need_to_check else can_user




