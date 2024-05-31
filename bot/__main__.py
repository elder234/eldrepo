from aiofiles import open as aiopen
from aiofiles.os import path as aiopath, remove
from asyncio import gather, create_subprocess_exec
from datetime import datetime
from os import execl as osexecl, getpid
from psutil import (
    boot_time, 
    cpu_count, 
    cpu_freq,
    cpu_percent, 
    disk_usage, 
    net_io_counters, 
    Process,
    virtual_memory, 
)
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from pytz import timezone
from signal import signal, SIGINT
from sys import executable
from time import time
from bot import (
    bot_name,
    bot,
    botStartTime,
    config_dict,
    DATABASE_URL,
    INCOMPLETE_TASK_NOTIFIER,
    Intervals,
    IS_PREMIUM_USER,
    LOGGER,
    sabnzbd_client,
    scheduler,
    user,
    Version,
)
from .helper.ext_utils.bot_utils import cmd_exec, sync_to_async, create_help_buttons
from .helper.ext_utils.db_handler import DbManager
from .helper.ext_utils.files_utils import clean_all, exit_clean_up
from .helper.ext_utils.jdownloader_booter import jdownloader
from .helper.ext_utils.status_utils import get_progress_bar_string, get_readable_file_size, get_readable_time
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.listeners.aria2_listener import start_aria2_listener
from .helper.mirror_leech_utils.rclone_utils.serve import rclone_serve_booter
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.button_build import ButtonMaker
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile
from .modules import (
    authorize,  # noqa: F401
    bot_settings,  # noqa: F401
    cancel_task,  # noqa: F401
    clone,  # noqa: F401
    exec,  # noqa: F401
    file_selector,  # noqa: F401
    force_start,  # noqa: F401
    gd_count,  # noqa: F401
    gd_delete,  # noqa: F401
    gd_search,  # noqa: F401
    help,  # noqa: F401
    mirror_leech,  # noqa: F401
    rss,  # noqa: F401
    shell,  # noqa: F401
    speedtest,  # noqa: F401
    status,  # noqa: F401
    torrent_search,  # noqa: F401
    users_settings,  # noqa: F401
    ytdlp,  # noqa: F401
)


async def stats(_, message):
    cpu = cpu_freq()
    memory = virtual_memory()
    network = net_io_counters()
    bot_uptime = get_readable_time(time() - botStartTime)
    machine_uptime = get_readable_time(time() - boot_time())
    total, used, free, disk = disk_usage(config_dict['DOWNLOAD_DIR'])
    neofetch, _, _ = await cmd_exec("neofetch --shell_version off --stdout", shell=True)
    
    if await aiopath.exists(".git"):
        commit_time, _, _ = await cmd_exec("git log -1 --pretty=format:'%cr'", shell=True)
        commit_message, _, _ = await cmd_exec("git log -1 --pretty=format:'%s'", shell=True)
    else:
        commit_time = "-"
        commit_message = "-"
    
    DC_ID = {
        1: "US",
        2: "NL",
        3: "US",
        4: "NL",
        5: "SG"
    }
        
    stats = f"""
<pre languange='bash'><code>{neofetch}</code>

<b>CPU</b>
<b>Cores        :</b> <code>{cpu_count(logical=False)}</code>
<b>Logical      :</b> <code>{cpu_count(logical=True)}</code>
<b>Frequency    :</b> <code>{round(cpu.current)}</code>
<code>{get_progress_bar_string(cpu_percent(interval=0.5))} - {cpu_percent(interval=0.5)}%</code>

<b>RAM</b> 
<b>Terpakai     :</b> <code>{get_readable_file_size(memory.used)}</code> [<code>{get_readable_file_size(Process(getpid()).memory_info().rss)}</code>]
<b>Tersedia     :</b> <code>{get_readable_file_size(memory.available)}</code>
<b>Total        :</b> <code>{get_readable_file_size(memory.total)}</code>
<code>{get_progress_bar_string(memory.percent)} - {memory.percent}%</code>

<b>Penyimpanan</b> 
<b>Terpakai     :</b> <code>{get_readable_file_size(used)}</code>
<b>Tersedia     :</b> <code>{get_readable_file_size(free)}</code>
<b>Total        :</b> <code>{get_readable_file_size(total)}</code>
<code>{get_progress_bar_string(disk)} - {disk}%</code>

<b>Jaringan</b>
<b>Total Unduh  :</b> <code>{get_readable_file_size(network.bytes_recv)}</code>
<b>Total Unggah :</b> <code>{get_readable_file_size(network.bytes_sent)}</code>

<b>Versi</b>
<b>Aria2c       :</b> <code>{Version.Aria2}</code>
<b>FFMPEG       :</b> <code>{Version.FFMPEG}</code>
<b>Google       :</b> <code>{Version.GoogleApi}</code>
<b>Java         :</b> <code>{Version.Java}</code>
<b>MegaSDK      :</b> <code>{Version.MegaSDK}</code>
<b>MyJD         :</b> <code>{Version.JDownloader}</code>
<b>P7Zip        :</b> <code>{Version.P7Zip}</code> 
<b>Pyro         :</b> <code>{Version.Pyrogram}</code>
<b>Python       :</b> <code>{Version.Python}</code>
<b>Qbittorrent  :</b> <code>{Version.QBittorrent}</code>
<b>Rclone       :</b> <code>{Version.Rclone}</code>
<b>SABnzbd      :</b> <code>{Version.SABnzbd}</code>
<b>YT-DLP       :</b> <code>{Version.YT_DLP}</code>

<b>Lainnya</b>
<b>Bot DC       :</b> <code>{bot.me.dc_id} ({DC_ID.get(bot.me.dc_id)})</code>
<b>Bot ID       :</b> <code>{bot.me.id}</code>
<b>Bot Name     :</b> <code>{bot.me.first_name} {(bot.me.last_name or '')}</code>
<b>Bot UserName :</b> <code>@{bot_name}</code>
<b>User DC      :</b> <code>{user.me.dc_id if user else '-'} {('(' + DC_ID.get(user.me.dc_id) + ')' if user else '')}</code>
<b>User ID      :</b> <code>{user.me.id if user else '-'}</code>
<b>User Name    :</b> <code>{(user.me.first_name if user else '-')} {((user.me.last_name if user else '') or '')}</code>
<b>User Status  :</b> <code>{'PREMIUM' if IS_PREMIUM_USER else 'FREE'}</code>
<b>Uptime Bot   :</b> <code>{bot_uptime}</code>
<b>Uptime Mesin :</b> <code>{machine_uptime}</code>
<b>Diperbarui   :</b> <code>{commit_time}</code>
<b>Pembaruan    :</b> <code>{commit_message}</code></pre>
"""

    await sendMessage(
        message, 
        stats
    )


async def start(client, message):
    buttons = ButtonMaker()
    buttons.ubutton(
        "Owner", "https://t.me/SaVe_USDT")
    buttons.ubutton("Channel", "https://t.me/arakurumi")
    reply_markup = buttons.build_menu(2)
    if await CustomFilters.authorized(client, message):
        start_string = f"""
<b>Unduh/Unggah dari Tautan Lambat menjadi Tautan Cepat!</b>
Kirim <code>/{BotCommands.HelpCommand[0]}</code> untuk mendapatkan list perintah yang tersedia!

<b>Note :</b>
Selalu backup File setelah Tugas Unduh/Unggah selesai untuk menghindari Cloud terhapus!
"""
    else:
        start_string = """
<b>Tidak ada izin!</b>

<b>Note :</b>
Gabung Grup/Channel untuk menggunakan Bot!
Jika Group ini mengaktifkan Topik, Kirim perintah di Topik yang diizinkan!
"""

    await sendMessage(
        message, 
        start_string, 
        reply_markup
    )


async def restart(_, message):
    Intervals["stopAll"] = True
    restart_message = await sendMessage(
        message, 
        "<b>Restarting...</b>"
    )
    if scheduler.running:
        scheduler.shutdown(wait=False)
    if qb := Intervals["qb"]:
        qb.cancel()
    if jd := Intervals["jd"]:
        jd.cancel()
    if nzb := Intervals["nzb"]:
        nzb.cancel()
    if st := Intervals["status"]:
        for intvl in list(st.values()):
            intvl.cancel()
    await sync_to_async(clean_all)
    if sabnzbd_client.LOGGED_IN:
        await gather(
            sabnzbd_client.pause_all(),
            sabnzbd_client.purge_all(True),
            sabnzbd_client.delete_history("all", delete_files=True),
        )
    proc1 = await create_subprocess_exec(
        "pkill",
        "-9",
        "-f",
        "avaj|c2aira|enolcr|gepmff|gunicorn|sulpdbznbas|xon-tnerrottibq",
    )
    proc2 = await create_subprocess_exec("python3", "update.py")
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(
        message, 
        "<b>Mengetest waktu respon bot...</b>"
    )
    end_time = int(round(time() * 1000))
    await editMessage(
        reply, 
        f"🤖 <b>Respon Bot :</b> <code>{end_time - start_time} ms</code>"
    )


async def log(_, message):
    await sendFile(message, "log.txt")


async def bot_help(_, message):
    help_string = f"""
<b>Daftar Perintah</b> <code>@{bot_name}</code>
<code>/{BotCommands.StartCommand}</code> : Mulai Bot.
<code>/{BotCommands.HelpCommand[0]}</code> atau <code>/{BotCommands.HelpCommand[1]}</code> : Cek semua perintah Bot.
<code>/{BotCommands.MirrorCommand[0]}</code> atau <code>/{BotCommands.MirrorCommand[1]}</code> : Mirror ke Cloud menggunakan Aria2.
<code>/{BotCommands.QbMirrorCommand[0]}</code> atau <code>/{BotCommands.QbMirrorCommand[1]}</code> : Mirror ke Cloud menggunakan qBittorrent.
<code>/{BotCommands.JdMirrorCommand[0]}</code> atau <code>/{BotCommands.JdMirrorCommand[1]}</code> : Mirror ke Cloud menggunakan JDownloader.
<code>/{BotCommands.NzbMirrorCommand[0]}</code> atau <code>/{BotCommands.NzbMirrorCommand[1]}</code> : Mirror ke Cloud menggunakan SABnzbd.
<code>/{BotCommands.YtdlCommand[0]}</code> atau <code>/{BotCommands.YtdlCommand[1]}</code> : Mirror ke Cloud menggunakan YT-DLP.
<code>/{BotCommands.LeechCommand[0]}</code> atau <code>/{BotCommands.LeechCommand[1]}</code> : Leech ke Telegram menggunakan Aria2.
<code>/{BotCommands.QbLeechCommand[0]}</code> atau <code>/{BotCommands.QbLeechCommand[1]}</code> : Leech ke Telegram menggunakan qBittorrent.
<code>/{BotCommands.JdLeechCommand[0]}</code> atau <code>/{BotCommands.JdLeechCommand[1]}</code> : Leech ke Telegram menggunakan JDownloader.
<code>/{BotCommands.NzbLeechCommand[0]}</code> atau <code>/{BotCommands.NzbLeechCommand[1]}</code> : Leech ke Telegram menggunakan SABnzbd.
<code>/{BotCommands.YtdlLeechCommand[0]}</code> atau <code>/{BotCommands.YtdlLeechCommand[1]}</code> : Leech ke Telegram menggunakan YT-DLP.
<code>/{BotCommands.CloneCommand[0]}</code> atau <code>/{BotCommands.CloneCommand[1]}</code> [gdriveUrl] : Menggandakan file/folder Google Drive.
<code>/{BotCommands.CountCommand[0]}</code> atau <code>/{BotCommands.CountCommand[1]}</code> [gdriveUrl] : Menghitung file/folder Google Drive.
<code>/{BotCommands.DeleteCommand[0]}</code> atau <code>/{BotCommands.DeleteCommand[1]}</code> [gdriveUrl] : Menghapus file/folder Google Drive (Hanya Owner & Sudo).
<code>/{BotCommands.UserSetCommand[0]}</code> atau <code>/{BotCommands.UserSetCommand[1]}</code> : Pengaturan User.
<code>/{BotCommands.BotSetCommand[0]}</code> atau <code>/{BotCommands.BotSetCommand[1]}</code> : Pengaturan Bot (Hanya Owner & Sudo).
<code>/{BotCommands.SelectCommand[0]}</code> atau <code>/{BotCommands.SelectCommand[1]}</code> : Memilih file dari Torrent atau NZB.
<code>/{BotCommands.CancelTaskCommand[0]}</code> atau <code>/{BotCommands.CancelTaskCommand[1]}</code> [GID] : Membatalkan Tugas.
<code>/{BotCommands.ForceStartCommand[0]}</code> atau <code>/{BotCommands.ForceStartCommand[1]}</code> [GID] : Memulai Tugas secara paksa.
<code>/{BotCommands.CancelAllCommand[0]}</code> atau <code>/{BotCommands.CancelAllCommand[1]}</code> : Membatalkan semua Tugas (Hanya Owner & Sudo).
<code>/{BotCommands.ListCommand[0]}</code> atau <code>/{BotCommands.ListCommand[1]}</code> [query] : Mencari file/folder di Google Drive.
<code>/{BotCommands.SearchCommand[0]}</code> atau <code>/{BotCommands.SearchCommand[1]}</code> [query] : Mencari torrent menggunakan API.
<code>/{BotCommands.StatusCommand[0]}</code> atau <code>/{BotCommands.StatusCommand[1]}</code> : Menampilkan status dari semua Tugas yang sedang berjalan.
<code>/{BotCommands.StatsCommand[0]}</code> atau <code>/{BotCommands.StatsCommand[1]}</code> : Menampilan statistik dari mesin Bot.
<code>/{BotCommands.PingCommand[0]}</code> atau <code>/{BotCommands.PingCommand[1]}</code> : Mengetes kecepatan respon Bot.
<code>/{BotCommands.SpeedCommand[0]}</code> atau <code>/{BotCommands.SpeedCommand[1]}</code> : Mengetes kecepatan koneksi Bot (Hanya Owner & Sudo).
<code>/{BotCommands.AuthorizeCommand[0]}</code> atau <code>/{BotCommands.AuthorizeCommand[1]}</code> : Memberikan izin chat atau user untuk menggunakan Bot (Hanya Owner & Sudo).
<code>/{BotCommands.UnAuthorizeCommand[0]}</code> atau <code>/{BotCommands.UnAuthorizeCommand[1]}</code> : Menghapus izin chat atau user untuk menggunakan Bot (Hanya Owner & Sudo).
<code>/{BotCommands.UsersCommand[0]}</code> atau <code>/{BotCommands.UsersCommand[1]}</code> : Menampilan pengaturan User (Hanya Owner & Sudo).
<code>/{BotCommands.AddSudoCommand[0]}</code> atau <code>/{BotCommands.AddSudoCommand[1]}</code> : Menambahkan User Sudo (Hanya Owner).
<code>/{BotCommands.RmSudoCommand[0]}</code> atau <code>/{BotCommands.RmSudoCommand[1]}</code> : Menghapus User Sudo (Hanya Owner).
<code>/{BotCommands.RestartCommand[0]}</code> atau <code>/{BotCommands.RestartCommand[1]}</code> : Memulai ulang dan memperbarui Bot (Hanya Owner & Sudo).
<code>/{BotCommands.LogCommand[0]}</code> atau <code>/{BotCommands.LogCommand[1]}</code> : Mengambil log file dari Bot (Hanya Owner & Sudo).
<code>/{BotCommands.ShellCommand[0]}</code> atau <code>/{BotCommands.ShellCommand[1]}</code> : Menjalankan perintah Shell (Hanya Owner).
<code>/{BotCommands.ExecCommand[0]}</code> atau <code>/{BotCommands.ExecCommand[1]}</code> : Menjalankan fungsi Sync Exec (Hanya Owner).
<code>/{BotCommands.AExecCommand[0]}</code> atau <code>/{BotCommands.AExecCommand[1]}</code> : Menjalankan fungsi Async Exec (Hanya Owner).
<code>/{BotCommands.ClearLocalsCommand[0]}</code> atau <code>/{BotCommands.ClearLocalsCommand[1]}</code> : Menghapus lokal Sync Exec atau Async Exec (Hanya Owner).
<code>/{BotCommands.RssCommand}</code> : Menu RSS.

<b>NOTE :</b> Kirim perintah tanpa argument untuk melihat perintah secara detail!
"""
    await sendMessage(
        message, 
        help_string
    )


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0
    
    # Get thread_id from AUTHORIZED_CHATS
    if chat_id == 0:
        chat_id = None
        thread_id = None
        if authorized_chat_id := config_dict.get("AUTHORIZED_CHATS"):
            if not isinstance(authorized_chat_id, int):
                if ":" in authorized_chat_id:
                    chat_id = authorized_chat_id.split(":")[0]
                    thread_id = authorized_chat_id.split(":")[1]

            if (
                chat_id is not None
                and not isinstance(chat_id, int)
                and chat_id.isdigit()
            ):
                chat_id = int(chat_id)

            if (
                thread_id is not None
                and not isinstance(thread_id, int)
                and thread_id.isdigit()
            ):
                thread_id = int(thread_id)

    async def send_incompelete_task_message(cid, msg):
        try:
            if msg.startswith("<b>Bot berhasil dimulai ulang!</b>"):
                await bot.edit_message_text(
                    chat_id=chat_id, 
                    message_id=msg_id, 
                    text=msg
                )
                await remove(".restartmsg")

            else:
                await bot.send_message(
                    chat_id=cid, 
                    text=msg, 
                    disable_web_page_preview=True,
                    disable_notification=True,
                    message_thread_id=thread_id,
                )

        except Exception as error:
            LOGGER.error(error)

    now = datetime.now(timezone("Asia/Jakarta"))
    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := await DbManager().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                msg = (
                    "<b>Bot berhasil dimulai ulang!</b>"
                    if cid == chat_id
                    else "<b>Bot dimulai ulang!</b>"
                )
                msg += f"\n<pre languange='bash'><b>Jam     :</b> <code>{now.strftime('%H:%M:%S WIB')}</code>"
                msg += f"\n<b>Hari    :</b> <code>{now.strftime('%A')}</code>"
                msg += f"\n<b>Tanggal :</b> <code>{now.strftime('%d %B %Y')}</code></pre>"

                if data.items():
                    msg += "<b>Tugas yang belum selesai :</b>"

                for tag, links in data.items():
                    msg += f"\n{tag} :"
                    for index, link in enumerate(links, start=1):
                        msg += f"\n <a href='{link}'>Tugas ke {index}</a>"
                        if len(msg.encode()) > 4000:
                            await send_incompelete_task_message(cid, msg)
                            msg = ""

                if msg:
                    await send_incompelete_task_message(cid, msg)

    if await aiopath.isfile(".restartmsg"):
        try:
            msg = "<b>Bot berhasil dimulai ulang!</b>"
            msg += f"\n<pre languange='bash'><b>Jam     :</b> <code>{now.strftime('%H:%M:%S WIB')}</code>"
            msg += f"\n<b>Hari    :</b> <code>{now.strftime('%A')}</code>"
            msg += f"\n<b>Tanggal :</b> <code>{now.strftime('%d %B %Y')}</code></pre>"
            
            await bot.edit_message_text(
                chat_id=chat_id, 
                message_id=msg_id, 
                text=msg
            )

        except Exception as error:
            LOGGER.error(error)

        await remove(".restartmsg")


async def main():
    if DATABASE_URL:
        await DbManager().db_load()
    jdownloader.initiate()
    await gather(
        sync_to_async(clean_all),
        torrent_search.initiate_search_tools(), 
        restart_notification(),
        telegraph.create_account(),
        rclone_serve_booter(),
        sync_to_async(start_aria2_listener, wait=False),
    )
    create_help_buttons()
    
    bot.add_handler(
        MessageHandler(
            start, 
            filters=command(
                BotCommands.StartCommand
            )
        )
    )
    bot.add_handler(
        MessageHandler(
            log, 
            filters=command(
                BotCommands.LogCommand
            ) & CustomFilters.sudo
        )
    )
    bot.add_handler(
        MessageHandler(
            restart, 
            filters=command(
                BotCommands.RestartCommand
            ) & CustomFilters.sudo
        )
    )
    bot.add_handler(
        MessageHandler(
            ping, 
            filters=command(
                BotCommands.PingCommand
            ) & CustomFilters.authorized
        )
    )
    bot.add_handler(
        MessageHandler(
            bot_help, 
            filters=command(
                BotCommands.HelpCommand
            ) & CustomFilters.authorized
        )
    )
    bot.add_handler(
        MessageHandler(
            stats, 
            filters=command(
                BotCommands.StatsCommand
            ) & CustomFilters.authorized
        )
    )
    LOGGER.info(f"Bot Started! -> @{bot_name}")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
