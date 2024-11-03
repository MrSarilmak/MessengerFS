import datetime
import os
import re
import time
import traceback
import uuid
from hashlib import sha256

import ffmpeg
import requests_html

from db.db_main import JsonDb

jdb = JsonDb()


def get_timestamp() -> float:
    return time.time()


def get_datetime(timestamp: float) -> str:
    return datetime.datetime \
        .fromtimestamp(timestamp) \
        .strftime("%d-%m-%Y %H:%M:%S")


def get_datetime2(timestamp: float) -> str:
    return datetime.datetime \
        .fromtimestamp(timestamp) \
        .strftime("%Y-%m-%d %H:%M:%S")


def dt_to_timestamp(date_time: str) -> float:
    return time.mktime(datetime.datetime.strptime(date_time, "%d-%m-%Y %H:%M:%S").timetuple())


def dt_to_timestamp2(date_time: str) -> float:
    return time.mktime(datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple())


def split_datetime(datetime_now: str) -> list:
    dt = datetime_now.split(" ")
    date_list = dt[0].split("-")
    time_list = dt[1].split(":")
    return date_list + time_list


def format_datetime_now(date_time: str | float) -> str:
    try:
        if isinstance(date_time, float):
            date_time = get_datetime2(date_time)
        date_time_now = get_datetime2(get_timestamp())
        if date_time_now == date_time:
            return "now"
        # print(split_datetime(date_time))
        # print(split_datetime(date_time_now))
        res = []
        dt_list = split_datetime(date_time)
        dtn_list = split_datetime(date_time_now)
        # if int(dtn_list[2]) - int(dt_list[2]) == 1:
        #     return "last day"
        # if int(dtn_list[2]) - int(dt_list[2]) == 7:
        #     return "last week"
        # if int(dtn_list[1]) - int(dt_list[1]) == 1:
        #     return "last month"
        # if int(dtn_list[0]) - int(dt_list[0]) == 1:
        #     return "last year"
        for i, j in zip(dt_list, dtn_list):
            if i != j:
                res.append(i)
        if len(res) == 6:
            return f"{res[2]}.{res[1]}.{res[0]}"
        elif len(res) == 5:
            return f"{res[1]}.{res[0]}"
        elif len(res) == 4:
            return f"{res[0]}.{dtn_list[1]}"
        elif len(res) == 3:
            return f"{res[0]}:{res[1]}"
        elif len(res) == 2:
            return f"{dtn_list[3]}:{res[0]}"
            # return "hour later"
        elif len(res) == 1:
            return f"{dtn_list[3]}:{dtn_list[4]}"
            # return "minute later"
    except:
        return date_time


def is_number(stroka: str) -> bool:
    if stroka.isdigit():
        return True
    else:
        try:
            float(stroka)
            return True
        except ValueError:
            return False


def gen_hash(psw: str) -> str | None:
    try:
        return sha256(psw.encode()).hexdigest()
    except:
        print(traceback.format_exc())
        return None


def gen_password_hash_string(string: str) -> str:
    salt_p1 = "".join(str(uuid.uuid4()).split("-"))
    salt_p2 = "".join(str(uuid.uuid4()).split("-"))
    salt = salt_p1 + salt_p2
    psw_string = string + ":" + salt
    return gen_hash(psw_string) + ":" + salt


def validate_psw(password: str, password_hash_str: str) -> bool:
    psw_hash = password_hash_str.split(":")[0]
    salt = password_hash_str.split(":")[1]
    psw_string = password + ":" + salt
    return gen_hash(psw_string) == psw_hash


def register(user_login: str, psw: str, psw2: str) -> tuple[bool, dict | str]:
    try:
        if not user_login:
            return False, "fill all fields"
        if not psw:
            return False, "fill all fields"
        if not psw2:
            return False, "fill all fields"
        if psw != psw2:
            return False, "passwords don't match"
        new_user = {
            "login": user_login,
            "name": "",
            "status": "User",
            "password": gen_password_hash_string(psw),
            "notifications": [],
            "settings": {
                "theme": "white"
            },
            "chats": []
        }
        jdb.add_user(new_user)
        return True, new_user
    except Exception:
        print(traceback.format_exc())
        return False, "something went wrong"


def login(user_login, password) -> tuple[bool, dict | str]:
    if not user_login:
        return False, "fill all fields"
    if not password:
        return False, "fill all fields"
    if user := jdb.get_user_by_login(user_login):
        if validate_psw(password, user.get("password", ":")):
            new_session = {
                "session_key": str(uuid.uuid4()),
                "session_login": user_login
            }
            if jdb.add_session(new_session):
                return True, new_session
            else:
                print("session save error")
                return False, "incorrect login or password"
        else:
            print("incorrect password")
            return False, "incorrect login or password"
    else:
        print("user not found")
        return False, "incorrect login or password"


def logout(session_key: str) -> bool:
    try:
        session = jdb.get_session_by_key(session_key)
        jdb.remove_session(session)
        return True
    except:
        return False


def login_required(session_key: str) -> bool:
    if jdb.get_session_by_key(session_key):
        return True
    return False


def api_login_required(token: str) -> bool:
    if token in jdb.get_all_tokens():
        return True
    return False


def api_login_required2(token: str) -> bool:
    return jdb.exist_token2(token)


def api_login_required3(token: str) -> bool:
    tokens = jdb.get_all_tokens2()
    if tokens:
        if tokens.get(token):
            return True
    return False


def api_login_required4(token: str) -> bool:
    _ = token
    raise NotImplementedError


def send_message(from_mail: str, to_mail: str, theme: str, message: str) -> bool:
    new_message = {
        "new": True,
        "sender": from_mail,
        "receiver": to_mail,
        "theme": theme,
        "message": message,
        "datetime": str(datetime.datetime.now())
    }
    return jdb.add_mail(new_message)


def create_token() -> tuple[bool, str]:
    try:
        new_token = str(uuid.uuid4()).replace("-", "")
        add_token_res = jdb.add_token(new_token)
        if add_token_res:
            return True, new_token
        return False, "something went wrong"
    except:
        return False, "something went wrong"


def create_token2():
    ...


def remove_message(mail_ind: int) -> bool:
    mail = jdb.get_mail_by_index(mail_ind)
    if mail:
        if mail.get("category") == "trash":
            return jdb.remove_mail(mail)
        else:
            return jdb.replace_email_category(mail, "trash")
    return False


# #


def add_review(user_login, review):
    new_review = {
        "review": review,
        "login": user_login
    }
    if jdb.add_review(new_review):
        return True
    return False


def parse_links(text: str) -> str:
    text = text.replace("&", "&amp;") \
        .replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace('"', "&quot;") \
        .replace("'", "&#39;") \
        .replace("`", "&#x60;")
    return re.sub(r"(?P<url>https?://\S+)",
                  r'<a href="\g<url>" target="_blank">\g<url></a>', text)


def exist_links(text: str) -> bool:
    return bool(re.search(r"(?P<url>https?://\S+)", text))


def first_link(message_text) -> str:
    return re.findall(r"(?P<url>https?://\S+)", message_text)[0]


def send_message(user_login, chat_id, message_text="", message_type="text",
                 file=None) -> tuple[bool, dict]:
    if message_text or file:
        datetime_str = get_timestamp()
        if chat_id:
            new_message = {
                "id": str(uuid.uuid4()),
                "sender": user_login,
                "message": message_text,
                "type": message_type,
                "time": datetime_str,
                "read": False
            }
            if file:
                new_message["file"] = file
            if user_in_chat(user_login, chat_id):
                return jdb.add_message(chat_id, new_message), new_message
            else:
                print("not in chat")
        else:
            print("no chat id")
    else:
        print("empty message")
    return False, dict()


def get_all_messages(group_id=None, chat_id=None) -> list | None:
    if group_id:
        return jdb.get_all_messages_from_group(group_id)
    if chat_id:
        return jdb.get_all_messages_from_chat(chat_id)
    return None


def get_message(message_id=None, group_id=None, chat_id=None) -> dict | None:
    if message_id:
        if group_id:
            return jdb.get_message_by_group_id_and_message_id(group_id, message_id)
        if chat_id:
            return jdb.get_message_by_chat_id_and_message_id(chat_id, message_id)
    return None


def remove_message(group_id=None, chat_id=None, message_id=None) -> bool:
    if group_id:
        return jdb.remove_message_by_group_id_and_message(group_id, message_id)
    if chat_id:
        return jdb.remove_message_by_chat_id_and_message(chat_id, message_id)
    return False


def user_in_chat(user_login, chat_id):
    return jdb.user_in_chat(user_login, chat_id)


def read_message(group_id=None, chat_id=None, message_id=None):
    if group_id:
        return jdb.read_message_by_group_id_and_message_id(group_id, message_id)
    if chat_id:
        return jdb.read_message_by_chat_id_and_message_id(chat_id, message_id)
    return False


def get_chat(chat_id=None):
    if chat_id:
        if chat_id == "all":
            chat = jdb.get_chat_by_id(chat_id)
            chat["messages"] = [{
                "id": str(uuid.uuid4()),
                "sender": "MrSarilmak",
                "message": f"message {i}",
                "type": "text",
                "time": get_datetime(get_timestamp()),
                "read": False
            } for i in range(1, 101)]
        return jdb.get_chat_by_id(chat_id)
    return None


def get_file_size(file_path: str):
    if os.path.exists(file_path[1:]):
        file_size_bytes = os.path.getsize(file_path[1:])
        i = -1
        byte_units = ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        file_size_bytes /= 1024
        i += 1
        while file_size_bytes > 1024:
            file_size_bytes /= 1024
            i += 1
        return f"{round(max(file_size_bytes, 0.1), 2)} {byte_units[i]}"
    print(f"file not found {file_path[1:]}")
    return ""


def get_meta_tags(url: str, user_agent: str = None, description_max_length: int = 149) -> dict | None:
    session = requests_html.HTMLSession()
    session.max_redirects = 3
    user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
    session.headers.update({"User-Agent": user_agent})
    try:
        request = session.get(url, allow_redirects=True)
    except:
        print(traceback.format_exc())
        session.close()
        return None
    result = {
        "og:site_name": None,
        "og:title": None,
        "og:description": None,
        "og:image": None
    }
    res = 0
    for el in request.html.find("meta"):
        name = el.attrs.get("property")
        content = el.attrs.get("content")
        if name == "og:site_name":
            result["og:site_name"] = content
            res += 1
        elif name == "og:title":
            result["og:title"] = content
            res += 1
        elif name == "og:description":
            result["og:description"] = content[:description_max_length]
            res += 1
        elif name == "og:image":
            result["og:image"] = content
            res += 1
        if res == 4:
            break
    request.close()
    session.close()
    if res == 4:
        return result
    else:
        return None


def chat_html(messages: list[dict], view_user_login: str, chat_id: str) -> str:
    if messages:
        messages_html_list = []
        user_login_to_name = {}
        for i, message in enumerate(messages):
            message_i = i + 1
            user_name = message.get("sender")
            if user_login_to_name.get(user_name):
                user_name = user_login_to_name.get(user_name)
            else:
                user_sender = jdb.get_user_by_login(user_name)
                if user_sender:
                    user_name = user_sender.get("name") if user_sender.get("name") else user_name
                user_login_to_name[user_name] = user_name
            message_text = message.get("message")
            message_time = message.get("time")
            if message_time:
                message_time = format_datetime_now(message_time)
            if message.get("sender") == view_user_login:
                message_pos = "right"
            else:
                message_pos = "left"
            message_type = message.get("type")
            if message_type == "text":
                if exist_links(message_text):
                    meta_tags = get_meta_tags(first_link(message_text))
                    message_text = parse_links(message_text)
                    if meta_tags:
                        site_name = meta_tags.get("og:site_name")
                        title = meta_tags.get("og:title")
                        description = meta_tags.get("og:description")
                        image = meta_tags.get("og:image")
                        message_html_str = f"""
                        <div class="message {message_pos}">
                            <div class="massage_data">
                                <p class="user_and_answer">
                                    <span class="user_name">{user_name}</span>
                                    <a onclick="open_message({message_i})" сlass="answer_link">ответить</a>
                                </p>
                                <div class="message_text">{message_text}</div>
                                <div class="web_page" style="padding: 5px;border-left: 3px solid #3cb4d9;border-radius: 5px">
                                    <h1 style="color: #3cb4d9;font-size: 16px">{site_name}</h1>
                                    <h1 style="font-size: 16px">{title}</h1>
                                    <p style="font-size: 14px">{description}</p>
                                    <img src="{image}" style="width: 100%;border-radius: 5px"
                                        onerror="this.remove()">
                                </div>
                                <p class="msg_and_time">
                                    <span class="pass"></span>
                                    <span class="message_time">{message_time}</span>
                                </p>
                            </div>
                        </div>"""
                    else:
                        message_html_str = f"""
                        <div class="message {message_pos}">
                            <div class="massage_data">
                                <p class="user_and_answer">
                                    <span class="user_name">{user_name}</span>
                                    <a onclick="open_message({message_i})" сlass="answer_link">ответить</a>
                                </p>
                                <p class="msg_and_time">
                                    <span class="message_text">{message_text}</span>
                                    <span class="message_time">{message_time}</span>
                                </p>
                            </div>
                        </div>"""
                else:
                    message_html_str = f"""
                    <div class="message {message_pos}">
                        <div class="massage_data">
                            <p class="user_and_answer">
                                <span class="user_name">{user_name}</span>
                                <a onclick="open_message({message_i})" сlass="answer_link">ответить</a>
                            </p>
                            <p class="msg_and_time">
                                <span class="message_text">{message_text}</span>
                                <span class="message_time">{message_time}</span>
                            </p>
                        </div>
                    </div>"""
            elif message_type == "reply":
                reply_to_msg_id = message.get("reply_to")
                if reply_to_msg := jdb.get_message_by_id(chat_id, reply_to_msg_id):
                    reply_to_user_name = reply_to_msg.get("sender")
                    if user_login_to_name.get(reply_to_user_name):
                        reply_to_user_name = user_login_to_name.get(reply_to_user_name)
                    if reply_to_user_name and reply_to_msg.get("message"):
                        message_html_str = f"""
                        <div class="message {message_pos}">
                            <div class="massage_data">
                                <p class="user_and_answer">
                                    <span class="user_name">{user_name}</span>
                                    <a onclick="open_message({message_i})" сlass="answer_link">ответить</a>
                                </p>
                                <div class="reply" style="padding: 5px;border-left: 3px solid #3cb4d9;border-radius: 5px">
                                    <h1 style="color: #3cb4d9;font-size: 16px">{reply_to_user_name}</h1>
                                    <p style="font-size: 14px">{reply_to_msg.get("message")}</p>
                                </div>
                                <p class="msg_and_time">
                                    <span class="message_text">{message_text}</span>
                                    <span class="message_time">{message_time}</span>
                                </p>
                            </div>
                        </div>"""
                    else:
                        print(f"reply_to_user_name = {reply_to_user_name}")
                        print(f"reply_to_msg = {reply_to_msg}")
                        message_html_str = f"""
                        <div class="message {message_pos}">
                            <div class="massage_data">
                                <p class="user_and_answer">
                                    <span class="user_name">{user_name}</span>
                                    <a onclick="open_message({message_i})" сlass="answer_link">ответить</a>
                                </p>
                                <p class="msg_and_time">
                                    <span class="message_text">{message_text}</span>
                                    <span class="message_time">{message_time}</span>
                                </p>
                            </div>
                        </div>"""
                else:
                    print(f"reply_to_msg = {reply_to_msg}")
                    message_html_str = f"""
                    <div class="message {message_pos}">
                        <div class="massage_data">
                            <p class="user_and_answer">
                                <span class="user_name">{user_name}</span>
                                <a onclick="open_message({message_i})" сlass="answer_link">ответить</a>
                            </p>
                            <p class="msg_and_time">
                                <span class="message_text">{message_text}</span>
                                <span class="message_time">{message_time}</span>
                            </p>
                        </div>
                    </div>"""
            elif message_type == "image":
                image_name = message.get("file") if message.get(
                    "file") else f"/static/image/placeholder.jpg"
                message_html_str = f"""<div class="message {message_pos}"><div class="massage_data"><p class="user_and_answer"><span class="user_name">{user_name}</span><a onclick="open_message({message_i})" сlass="answer_link">ответить</a></p><img src="{image_name}" onerror="this.onerror=null;this.remove();" class="message_img"><p class="msg_and_time"><span class="message_text">{message_text}</span><span class="message_time">{message_time}</span></p></div></div>"""
            elif message_type == "video":
                video_name = message.get("file") if message.get(
                    "file") else "/static/video/Minecraft_ 1.19.2 - Одиночная игра 2023-02-23 15-15-00.mp4"
                message_html_str = f"""<div class="message {message_pos}"><div class="massage_data"><p class="user_and_answer"><span class="user_name">{user_name}</span><a onclick="open_message({message_i})" сlass="answer_link">ответить</a></p><video src="{video_name}" controls class="message_video"></video><p class="msg_and_time"><span class="message_text">{message_text}</span><span class="message_time">{message_time}</span></p></div></div>"""
            elif message_type == "video_circle":
                video_name = message.get("file") if message.get(
                    "file") else "/static/video/Minecraft_ 1.19.2 - Одиночная игра 2023-02-23 15-15-00.mp4"
                message_html_str = f"""
                <div class="message {message_pos}">
                    <div class="massage_data circle">
                        <p class="user_and_answer"><span class="user_name">{user_name}</span></p>
                        <div class="progress">
                            <svg class="progress-circle">
                                <circle id="vc{message_i}2" class="progress-circle-prog" cx="131" cy="131" r="120"></circle>
                            </svg>
                        </div>
                        <video id="vc{message_i}" src="{video_name}" class="message_video" style="border-radius: 50%"></video>
                        <p class="msg_and_time">
                            <span class="message_text">{message_text}</span>
                            <span class="message_time">{message_time}</span>
                        </p>
                    </div>
                </div>"""
            elif message_type == "audio":
                if message_pos == "left":
                    audio_pos_class = "message_audio"
                else:
                    audio_pos_class = "right_message_audio"
                audio_name = message.get("file") if message.get("file") else "Alan Walker - On My Way (Piano Cover).m4a"
                message_html_str = f"""<div class="message {message_pos}"><div class="massage_data"><p class="user_and_answer"><span class="user_name">{user_name}</span><a onclick="open_message({message_i})" сlass="answer_link">ответить</a></p><audio src="{audio_name}" controls class="{audio_pos_class}"></audio><p class="msg_and_time"><span class="message_text"> </span><span class="message_time">{message_time}</span></p></div></div>"""
            else:
                file_name = message.get("file").split("/")[-1]
                file_size = get_file_size(message.get("file"))
                message_html_str = f"""<div class="message {message_pos}"><div class="massage_data"><p class="user_and_answer"><span class="user_name">{user_name}</span></p><div style="display: flex;"><div class="blue-circle"><a href="{message.get('file')}" download><img src="/static/image/icons/white-arrow-down.svg" class="icon"></a></div><div><h4 class="bold">{file_name}</h4><span>{file_size}</span></div></div><p class="msg_and_time"><span class="message_text"></span><span class="message_time">{message_time}</span></p></div></div>"""
            messages_html_list.append(message_html_str)
        return "\n".join(messages_html_list)
    else:
        return '<div id="zero-messages" class="message">Нет сообщений</div>'


def get_chats(user_login=None) -> list[dict] | None:
    if user_login:
        chats_id = jdb.get_key_value_from_user_by_login(user_login, "chats")
        if chats_id:
            chats = []
            for chat_id in chats_id:
                chat = jdb.get_chat_by_id(chat_id)
                if chat:
                    chats.append(chat)
                else:
                    print(f"user: {user_login} Chat {chat_id} not found")
            return chats
    return None


def chats_html(chats: list[dict], user_login: str, selected: str = None) -> str:
    chats_html_list = []
    if chats:
        for i, chat in enumerate(chats):
            chat_i = i + 1
            chat_title = chat.get("title")
            if chat_title == "{{companion_name}}":
                if chat.get("users")[0] == user_login:
                    companion_login = chat.get("users")[1]
                else:
                    companion_login = chat.get("users")[0]
                if companion_login:
                    companion_user = jdb.get_user_by_login(companion_login)
                    if companion_user.get("name"):
                        chat_title = companion_user.get("name")
                    else:
                        chat_title = companion_login
            if chat_messages := chat.get("messages", [dict()]):
                chat_last_message = chat_messages[-1] if chat_messages else dict()
                if chat_last_message_time := chat_last_message.get("time"):
                    chat_last_message_time = format_datetime_now(get_datetime2(chat_last_message_time))
                else:
                    chat_last_message_time = ""
                if chat_last_message.get("type") == "text":
                    style_cls = ""
                    chat_last_message = chat_last_message.get("message")
                else:
                    style_cls = "blue-text"
                    chat_last_message = chat_last_message.get("type")
            else:
                chat_last_message_time = ""
                chat_last_message = ""
                style_cls = ""
            chat_logo = chat.get("logo")
            if chat_logo == "{{companion_logo}}":
                companion_login = chat.get("users")[0] if chat.get("users") else None
                if companion_login == user_login:
                    companion_login = chat.get("users")[1] if chat.get("users") else None
                if companion_login:
                    companion_user = jdb.get_user_by_login(companion_login)
                    if companion_user.get("logo"):
                        chat_logo = companion_user.get("logo")
                    else:
                        chat_logo = "placeholder.jpg"
            chat_id = chat.get("id")
            style_cls = f" {style_cls}" if style_cls else ''
            chat_html_str = f"""
                            <div class="chat{' selected' if chat_id == selected else ''}" id="{chat_i}" onclick="open_chat('{chat_id}')">
                                <img src="/static/image/{chat_logo}" class="chat_logo"
                                onerror="this.onerror=null;this.remove()">
                                <div class="chat_info">
                                    <h6 class="chat_name">{chat_title}</h6>
                                    <span class="last_message_time">{chat_last_message_time}</span>
                                    <p class="last_message{style_cls}">{chat_last_message}</p>
                                </div>
                            </div>"""
            chats_html_list.append(chat_html_str)
        return "\n".join(chats_html_list)
    return ""


def convert_to_mp4(mkv_file):
    name, ext = os.path.splitext(mkv_file)
    out_name = name + ".mp4"
    # ffmpeg.input(mkv_file).output(out_name).run()
    ffmpeg.input(mkv_file).output(out_name, vcodec="h264", acodec="aac").run()
    print(f"Finished converting {mkv_file}")


def create_group_chat(creator_login: str, logo: str, name: str, users: list[str]) -> \
        tuple[str, str] | tuple[None, None]:
    try:
        if not creator_login:
            return None, "login is required"
        if not logo:
            return None, "logo is required"
        if not name:
            return None, "name is required"
        if not users:
            return None, "users are required"
        group_id = str(uuid.uuid4())
        new_group = {
            "id": group_id,
            "title": name,
            "logo": logo,
            "creator": creator_login,
            "users": users,
            "messages": []
        }
        jdb.add_chat(new_group)
        return group_id, "success"
    except:
        print(traceback.format_exc())
        return None


def create_private_chat(users: list[str]) -> tuple[str, str] | tuple[None, None]:
    try:
        if not users:
            return None, "users are required"
        chat_id = str(uuid.uuid4())
        new_chat = {
            "id": chat_id,
            "title": "{{companion_name}}",
            "logo": "{{companion_logo}}",
            "creator": "MrSarilmak",
            "users": users,
            "messages": []
        }
        jdb.add_chat(new_chat)
        return chat_id
    except:
        print(traceback.format_exc())
        return None


def chekbox_users_html(users: list[dict], user_login: str) -> str:
    users_html_list = []
    if users:
        for user in users:
            if user.get("login") == user_login:
                continue
            user_logo = user.get("logo") if user.get("logo") else "placeholder.jpg"
            user_html = f"""<div class="user">
            <div class="checkbox">
                <input type="checkbox" onclick="ocgsum_toggle('{user.get("login")}')">
            </div>
            <div class="logo">
                <img src="/static/image/{user_logo}">
            </div>
            <div class="data">
                <div class="user-name">{user.get("login")}</div>
            </div>
        </div>"""
            users_html_list.append(user_html)
    return "".join(users_html_list)


def users_html(users: list[dict], user_login: str) -> str:
    users_html_list = []
    if users:
        for user in users:
            if user.get("login") == user_login:
                continue
            user_logo = user.get("logo") if user.get("logo") else "placeholder.jpg"
            user_html = f"""<div class="user">
            <div class="logo">
                <img src="/static/image/{user_logo}">
            </div>
            <div class="data">
                <div class="user-name">{user.get("login")}</div>
            </div>
        </div>"""
            users_html_list.append(user_html)
    return "".join(users_html_list)


def chat_menu_members_html(chat_users: list[str], login_sio_sid: dict[str, str]) -> str:
    members_html_list = []
    for i, user_login in enumerate(chat_users):
        if user := jdb.get_user_by_login(user_login):
            user_logo = user.get("logo") if user.get("logo") else "placeholder.jpg"
            user_name = user.get("name") if user.get("name") else user_login
            user_status = "online" if login_sio_sid.get(user_login) else "offline"
            member_html = f"""<div id="cm1" class="chat-member">
            <img src="/static/image/{user_logo}" class="user_logo"
            onerror="this.onerror=null;this.remove()">
            <div class="user_info">
                <h6 id="un{i + 1}" class="user_name">{user_name}</h6>
                <p id="us{i + 1}" class="user_status">{user_status}</p>
            </div>
        </div>"""
            members_html_list.append(member_html)
    return "".join(members_html_list)


def change_password(user_login: str, old_password: str, new_password: str,
                    new_password2: str) -> tuple[bool, str]:
    if not user_login:
        return False, "login is required"
    if not old_password:
        return False, "old password is required"
    if not new_password:
        return False, "new password is required"
    if not new_password2:
        return False, "new repeat password is required"
    if new_password != new_password2:
        return False, "new passwords do not match"
    if user := jdb.get_user_by_login(user_login):
        if validate_psw(old_password, user.get("password", ":")):
            jdb.set_key_value_to_user_by_login(user_login, "password",
                                               gen_password_hash_string(new_password))
            return True, ""
        else:
            # return False, "wrong password"
            return False, "wrong login or password"
    else:
        # return False, "user not found"
        return False, "wrong login or password"


def request_log(client_ip: str, method: str, uri: str, status_code: int) -> str:
    date_time = datetime.datetime.now()
    date_time = date_time.strftime("%d/%B/%Y %H:%M:%S")
    log_msg = f"{client_ip} - - [{date_time}] \"{method} {uri} HTTP/1.1\" {status_code} -"
    return log_msg


def event_log(client_ip: str, event: str, status: str) -> str:
    date_time = datetime.datetime.now()
    date_time = date_time.strftime("%d/%B/%Y %H:%M:%S")
    log_msg = f"{client_ip} - - [{date_time}] \"{event}\" {status} -"
    return log_msg
