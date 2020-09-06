from kutana.controller_vk.converter import convert_to_attachment
from kutana.tools.functions import load_configuration
from kutana.logger import logger
import aiohttp
import json
from database import *
from utils import levels

async def upload_file_to_vk(ctrl, upload_url, data):
    upload_result_resp = await ctrl.session.post(
        upload_url, data=data
    )

    if not upload_result_resp:
        return None

    upload_result_text = await upload_result_resp.text()

    if not upload_result_text:
        return None

    try:
        upload_result = json.loads(upload_result_text)

        if "error" in upload_result:
            raise Exception

    except Exception:
        return None

    return upload_result


def make_reply(ctrl, peer_id, from_id, redisstore):
    """Creates replying coroutine for controller and peer_id."""

    async def reply(message, attachment=None, sticker_id=None,
            payload=None, keyboard=None):
        #print(f"I want SAY A TEXT!!! {from_id}")
        prefix = await redisstore.get(f"honoka:cached_prefix:{from_id}")
        if not prefix:
            try:
                usera = await manager.execute(PxUser.select().where(PxUser.iduser == str(from_id)))
                if not usera:
                    prefix = ""
                    raise NameError('User not found!')

                usera = usera[0]
                if usera.rank > len(levels)-1:
                    prefix = f"{usera.personal if usera.personal != '' else 'Установите свой префикс командой !setprefix'}, "
                    await redisstore.set(f"honoka:cached_prefix:{from_id}", f"{usera.personal if usera.personal != '' else 'Установите свой префикс командой !setprefix'}, ")
                else:
                    prefix = f"{levels[usera.rank]}, "
            except Exception as e:
                #            print(e)
                pass

        await ctrl.send_message(
            prefix+message,
            peer_id,
            attachment,
            sticker_id,
            payload,
            keyboard
        )
        return "DONE"

    return reply


def make_upload_docs(ctrl, ori_peer_id):
    """Creates uploading docs coroutine for controller and peer_id."""

    async def upload_doc(file, peer_id=None, group_id=None,
            doctype="doc", filename=None):
        """Pass peer_id=False to upload with docs.getWallUploadServer."""

        if filename is None:
            filename = "file.png"

        if peer_id is None:
            peer_id = ori_peer_id

        if isinstance(file, str):
            with open(file, "rb") as o:
                file = o.read()

        if peer_id:
            upload_data = await ctrl.request(
                "docs.getMessagesUploadServer", peer_id=peer_id, type=doctype
            )

        else:
            upload_data = await ctrl.request(
                "docs.getWallUploadServer",
                group_id=group_id or ctrl.group_id
            )

        if "upload_url" not in upload_data.response:
            return None

        upload_url = upload_data.response["upload_url"]

        data = aiohttp.FormData()
        data.add_field("file", file, filename=filename)

        upload_result = await upload_file_to_vk(ctrl, upload_url, data)

        if not upload_result:
            return None

        attachments = await ctrl.request(
            "docs.save", **upload_result
        )

        if not attachments.response:
            return None

        return convert_to_attachment(
            attachments.response[0], "doc"
        )

    return upload_doc


def make_upload_photo(ctrl, ori_peer_id):
    """Creates uploading photo coroutine for controller and peer_id"""

    async def upload_photo(file, peer_id=None):
        if peer_id is None:
            peer_id = ori_peer_id

        if isinstance(file, str):
            with open(file, "rb") as o:
                file = o.read()

        upload_data = await ctrl.request(
            "photos.getMessagesUploadServer", peer_id=peer_id
        )

        if "upload_url" not in upload_data.response:
            return None

        if upload_data.response['user_id'] == 0: # group chat
            upload_data = await ctrl.request(
                "photos.getMessagesUploadServer", peer_id=load_configuration("group_chat_pseudo_photo", "configuration.json")
            )

        upload_url = upload_data.response["upload_url"]

        data = aiohttp.FormData()
        data.add_field("photo", file, filename="image.png")

        upload_result = await upload_file_to_vk(ctrl, upload_url, data)

        if not upload_result:
            return None

        attachments = await ctrl.request(
            "photos.saveMessagesPhoto", **upload_result
        )

        if not attachments.response:
            return None

        return convert_to_attachment(
            attachments.response[0], "photo"
        )

    return upload_photo
