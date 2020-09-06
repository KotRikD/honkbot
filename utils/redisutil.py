import json

async def edict(dict_to_encode):
    '''
    The function to encode dict -> json for redis.set

    :param dict_to_encode:
    :return str:
    '''
    try:
        jdict = json.dumps(dict_to_encode)
        return jdict
    except Exception:
        return None

async def ddict(dict_to_decode):
    '''
    The function to decode str -> dict for redis.get
    :param dict_to_decode:
    :return dict:
    '''

    try:
        edict = json.loads(dict_to_decode)
        return edict
    except Exception:
        return None