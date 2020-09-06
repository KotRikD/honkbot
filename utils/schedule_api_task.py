import asyncio

from kutana.tools.functions import load_configuration
import aiohttp

class RawRequest:

    def __init__(self, token):
        self.session = None
        self.api_url = "https://api.vk.com/method/{{}}?access_token={}&v={}".format(token, "5.80")

    async def schedule_raw_request(self, method, **kwargs):
        """Perform api request to vk.com"""
        self.session = aiohttp.ClientSession()
        url = self.api_url.format(method)

        data = {}

        for k, v in kwargs.items():
            if v is not None:
                data[k] = v

        try:
            async with self.session.post(url, data=data) as response:
                raw_respose = await response.json()
        except Exception as e:
            return None

        if raw_respose.get("error"):
            return raw_respose.get("error", "")
        await self.session.close()
        
        return raw_respose["response"]

async def schedule_api_task(task):
    a = RawRequest(load_configuration("vk_token", "configuration.json"))
    asyncio.ensure_future(task(a.schedule_raw_request))
    return "GOON"

def schedule_task(task, **kwargs):
    asyncio.ensure_future(task(kwargs))
    return "GOON"
