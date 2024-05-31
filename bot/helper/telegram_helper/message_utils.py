from asyncio import sleep
from pyrogram.errors import FloodWait
from pyrogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from re import match as re_match
from time import time
from typing import Any, Optional, Union

from bot import config_dict, LOGGER, status_dict, task_dict_lock, Intervals, bot, user
from bot.helper.ext_utils.bot_utils import setInterval
from bot.helper.ext_utils.exceptions import TgLinkException
from bot.helper.ext_utils.status_utils import get_readable_message


async def sendMessage(message, text, buttons=None, block=True):
    try:
        return await message.reply(
            text=text,
            quote=True,
            disable_web_page_preview=True,
            disable_notification=True,
            reply_markup=buttons,
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        if block:
            await sleep(f.value * 1.2)
            return await sendMessage(message, text, buttons)
        return str(f)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)


async def editMessage(message, text, buttons=None, block=True):
    try:
        await message.edit(
            text=text, disable_web_page_preview=True, reply_markup=buttons
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        if block:
            await sleep(f.value * 1.2)
            return await editMessage(message, text, buttons)
        return str(f)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)
   

async def copyMessage(chat_id:int, from_chat_id:int, message_id=int, message_thread_id=None, reply_to_message_id=None, is_media_group=False):
    try:
        if is_media_group:
            return await bot.copy_media_group(
                chat_id=chat_id, 
                from_chat_id=from_chat_id, 
                message_id=message_id, 
                message_thread_id=message_thread_id,
                reply_to_message_id=reply_to_message_id
            )
        else:
            return await bot.copy_message(
                chat_id=chat_id, 
                from_chat_id=from_chat_id, 
                message_id=message_id, 
                message_thread_id=message_thread_id,
                reply_to_message_id=reply_to_message_id
            )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await copyMessage(chat_id, from_chat_id, message_id, message_thread_id, is_media_group)
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)


async def forwardMessage(chat_id:int, from_chat_id:int, message_id=int, message_thread_id=None, unquote=True):
    try:
        return await bot.forward_messages(
                chat_id=chat_id, 
                from_chat_id=from_chat_id, 
                message_id=message_id, 
                message_thread_id=message_thread_id,
                drop_author=unquote
            )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await forwardMessage(chat_id, from_chat_id, message_id, message_thread_id, unquote)
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)


async def sendFile(message, file, caption=""):
    try:
        return await message.reply_document(
            document=file, 
            quote=True, 
            caption=caption, 
            disable_notification=True
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await sendFile(message, file, caption)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)


async def sendPhoto(message, photo, caption=""):
    try:
        return await message.reply_photo(
            photo=photo, 
            quote=True, 
            caption=caption, 
            disable_notification=True
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await sendFile(message, photo, caption)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)


async def sendRss(text):
    try:
        app = user or bot
        return await app.send_message(
            chat_id=config_dict["RSS_CHAT"],
            text=text,
            disable_web_page_preview=True,
            disable_notification=True,
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await sendRss(text)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)


async def deleteMessage(message):
    try:
        await message.delete()
    except Exception as e:
        LOGGER.error(str(e))


async def auto_delete_message(cmd_message=None, bot_message=None):
    await sleep(60)
    if cmd_message is not None:
        await deleteMessage(cmd_message)
    if bot_message is not None:
        await deleteMessage(bot_message)


async def delete_status():
    async with task_dict_lock:
        for key, data in list(status_dict.items()):
            try:
                await deleteMessage(data["message"])
                del status_dict[key]
            except Exception as e:
                LOGGER.error(str(e))


async def get_tg_link_message(link):
    message = None
    links = []
    if link.startswith("https://t.me/"):
        private = False
        msg = re_match(
            r"https:\/\/t\.me\/(?:c\/)?([^\/]+)(?:\/[^\/]+)?\/([0-9-]+)", link
        )
    else:
        private = True
        msg = re_match(
            r"tg:\/\/openmessage\?user_id=([0-9]+)&message_id=([0-9-]+)", link
        )
        if not user:
            raise TgLinkException("USER_SESSION_STRING diperlukan untuk link private!")

    chat = msg[1]
    msg_id = msg[2]
    if "-" in msg_id:
        start_id, end_id = msg_id.split("-")
        msg_id = start_id = int(start_id)
        end_id = int(end_id)
        btw = end_id - start_id
        if private:
            link = link.split("&message_id=")[0]
            links.append(f"{link}&message_id={start_id}")
            for _ in range(btw):
                start_id += 1
                links.append(f"{link}&message_id={start_id}")
        else:
            link = link.rsplit("/", 1)[0]
            links.append(f"{link}/{start_id}")
            for _ in range(btw):
                start_id += 1
                links.append(f"{link}/{start_id}")
    else:
        msg_id = int(msg_id)

    if chat.isdigit():
        chat = int(chat) if private else int(f"-100{chat}")

    if not private:
        try:
            message = await bot.get_messages(chat_id=chat, message_ids=msg_id)
            if message.empty:
                private = True
        except Exception as e:
            private = True
            if not user:
                raise e

    if not private:
        return (links, "bot") if links else (message, "bot")
    elif user:
        try:
            user_message = await user.get_messages(chat_id=chat, message_ids=msg_id)
        except Exception as e:
            raise TgLinkException(
                f"You don't have access to this chat!. ERROR: {e}"
            ) from e
        if not user_message.empty:
            return (links, "user") if links else (user_message, "user")
    else:
        raise TgLinkException("Link private!")


async def update_status_message(sid, force=False):
    if Intervals["stopAll"]:
        return
    async with task_dict_lock:
        if not status_dict.get(sid):
            if obj := Intervals["status"].get(sid):
                obj.cancel()
                del Intervals["status"][sid]
            return
        if not force and time() - status_dict[sid]["time"] < 3:
            return
        status_dict[sid]["time"] = time()
        page_no = status_dict[sid]["page_no"]
        status = status_dict[sid]["status"]
        is_user = status_dict[sid]["is_user"]
        page_step = status_dict[sid]["page_step"]
        text, buttons = await get_readable_message(
            sid, is_user, page_no, status, page_step
        )
        if text is None:
            del status_dict[sid]
            if obj := Intervals["status"].get(sid):
                obj.cancel()
                del Intervals["status"][sid]
            return
        if text != status_dict[sid]["message"].text:
            message = await editMessage(
                status_dict[sid]["message"], text, buttons, block=False
            )
            if isinstance(message, str):
                if message.startswith("Telegram says: [400"):
                    del status_dict[sid]
                    if obj := Intervals["status"].get(sid):
                        obj.cancel()
                        del Intervals["status"][sid]
                else:
                    LOGGER.error(
                        f"Status with id: {sid} haven't been updated. Error: {message}"
                    )
                return
            status_dict[sid]["message"].text = text
            status_dict[sid]["time"] = time()


async def sendStatusMessage(msg, user_id=0):
    if Intervals["stopAll"]:
        return
    async with task_dict_lock:
        sid = user_id or msg.chat.id
        is_user = bool(user_id)
        if sid in list(status_dict.keys()):
            page_no = status_dict[sid]["page_no"]
            status = status_dict[sid]["status"]
            page_step = status_dict[sid]["page_step"]
            text, buttons = await get_readable_message(
                sid, is_user, page_no, status, page_step
            )
            if text is None:
                del status_dict[sid]
                if obj := Intervals["status"].get(sid):
                    obj.cancel()
                    del Intervals["status"][sid]
                return
            message = status_dict[sid]["message"]
            await deleteMessage(message)
            message = await sendMessage(msg, text, buttons, block=False)
            if isinstance(message, str):
                LOGGER.error(
                    f"Status with id: {sid} haven't been sent. Error: {message}"
                )
                return
            message.text = text
            status_dict[sid].update({"message": message, "time": time()})
        else:
            text, buttons = await get_readable_message(sid, is_user)
            if text is None:
                return
            message = await sendMessage(msg, text, buttons, block=False)
            if isinstance(message, str):
                LOGGER.error(
                    f"Status with id: {sid} haven't been sent. Error: {message}"
                )
                return
            message.text = text
            status_dict[sid] = {
                "message": message,
                "time": time(),
                "page_no": 1,
                "page_step": 1,
                "status": "All",
                "is_user": is_user,
            }
    if not Intervals["status"].get(sid) and not is_user:
        Intervals["status"][sid] = setInterval(
            config_dict["STATUS_UPDATE_INTERVAL"], update_status_message, sid
        )


# NOTE: Custom by Me, if You dont need it, just ignore or delete from this line ^^
async def customSendMessage(
    client: Any,
    chat_id: int,
    text: str,
    message_thread_id: Optional[int] = None,
    reply_markup: Optional[Union[ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None,
) -> Message:
    try:
        return await client.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
            disable_notification=True,
            message_thread_id=message_thread_id,
            reply_markup=reply_markup,
        )
    
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await customSendMessage(
            client=client,
            chat_id=chat_id,
            text=text,
            message_thread_id=message_thread_id,
            reply_markup=reply_markup,
        )
    
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)


async def customSendRss(
    text: str,
    photo: Union[str, bytes],
    caption: Optional[str] = str(),
    has_spoiler: bool = None,
    reply_markup: Optional[Union[ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None,
) -> Message:
    chat_id = None
    message_thread_id = None
    if chat_id := config_dict.get("RSS_CHAT_ID"):
        if not isinstance(chat_id, int):
            if ":" in chat_id:
                message_thread_id = chat_id.split(":")[1]
                chat_id = chat_id.split(":")[0]
        
        if (
            chat_id is not None
            and chat_id.isdigit()   
        ):
            chat_id = int(chat_id)
        
        if (
            message_thread_id is not None
            and message_thread_id.isdigit()
        ):
            message_thread_id = int(message_thread_id)
    else:
        return "RSS_CHAT_ID tidak ditemukan!"
        
    try:
        if photo:
            if len(text) > 1024:
                reply_photo = await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    has_spoiler=has_spoiler,
                    disable_notification=True,
                    message_thread_id=message_thread_id,
                    reply_markup=reply_markup,
                )

                return await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    disable_web_page_preview=True,
                    disable_notification=True,
                    message_thread_id=message_thread_id,
                    reply_to_message_id=reply_photo.id,
                    reply_markup=reply_markup,
                )
            
            else:
                return await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    has_spoiler=has_spoiler,
                    disable_notification=True,
                    message_thread_id=message_thread_id,
                    reply_markup=reply_markup,
                )
            
        else:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True,
                disable_notification=True,
                message_thread_id=message_thread_id,
                reply_markup=reply_markup
            )
        
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await customSendRss(
            text=text,
            photo=photo,
            caption=caption,
            has_spoiler=has_spoiler,
            reply_markup=reply_markup,
        )
    
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)


async def customSendDocument(
    message: Message,
    document: Union[str, bytes],
    thumb: Optional[Union[str, bytes]] = None,
    caption: Optional[str] = str(),
    file_name: Optional[str] = None,
    reply_markup: Optional[Union[ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None,
    progress: Optional[Any] = None,
    progress_args: Optional[tuple] = (),
) -> Message:
    try:
        return await message.reply_document(
            document=document,
            quote=True,
            thumb=thumb,
            caption=caption,
            file_name=file_name,
            force_document=True,
            disable_notification=True,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await customSendDocument(
            message=message,
            document=document,
            thumb=thumb,
            caption=caption,
            file_name=file_name,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)


async def customSendAudio(
    message: Message,
    audio: Union[str, bytes],
    caption: Optional[str] = str(),
    duration: Optional[int] = 0,
    performer: Optional[str] = None,
    title: Optional[str] = None,
    thumb: Optional[Union[str, bytes]] = None,
    reply_markup: Optional[Union[ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None,
    progress: Optional[Any] = None,
    progress_args: Optional[tuple] = (),
) -> Message:
    try:
        return await message.reply_audio(
            audio=audio,
            quote=True,
            caption=caption,
            duration=duration,
            performer=performer,
            title=title,
            thumb=thumb,
            disable_notification=True,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await customSendAudio(
            message=message,
            audio=audio,
            caption=caption,
            duration=duration,
            performer=performer,
            title=title,
            thumb=thumb,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)
    

async def customSendVideo(
    message: Message,
    video: Union[str, bytes],
    caption: Optional[str] = str(),
    duration: Optional[int] = 0,
    width: Optional[int] = None,
    height: Optional[int] = None,
    thumb: Optional[Union[str, bytes]] = None,
    has_spoiler: bool = None,
    reply_markup: Optional[Union[ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None,
    progress: Optional[Any] = None,
    progress_args: Optional[tuple] = (),
) -> Message:
    try:
        return await message.reply_video(
            video=video,
            quote=True,
            caption=caption,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            has_spoiler=has_spoiler,
            supports_streaming=True,
            disable_notification=True,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await customSendVideo(
            message=message,
            video=video,
            caption=caption,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            has_spoiler=has_spoiler,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)


async def customSendPhoto(
    message: Message,
    photo: Union[str, bytes],
    caption: Optional[str] = str(),
    has_spoiler: bool = None,
    reply_markup: Optional[Union[ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None,
    progress: Optional[Any] = None,
    progress_args: Optional[tuple] = (),
) -> Message:
    try:
        return await message.reply_photo(
            photo=photo,
            quote=True,
            caption=caption,
            has_spoiler=has_spoiler,
            disable_notification=True,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await customSendPhoto(
            message=message,
            photo=photo,
            caption=caption,
            has_spoiler=has_spoiler,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )
    
    except Exception as e:
        LOGGER.error(str(e))
        raise Exception(e)