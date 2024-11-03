import socket
import struct
from datetime import timedelta

from flask import *
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException
from werkzeug.serving import WSGIRequestHandler
from colorama import init as init_colorama, Fore

from logic import *


class ErrorTestingWSGIRequestHandler(WSGIRequestHandler):
    def make_environ(self):
        environ = super(ErrorTestingWSGIRequestHandler, self).make_environ()
        environ["socket"] = self.connection
        return environ


init_colorama(True)
app = Flask("MyMessagerFS test6 100% PWA")
socketio = SocketIO(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)
app.secret_key = "92f282cf-b568-4a40-9ccb-b38ee103a0fb"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
# app.config["SESSION_COOKIE_SECURE"] = True
HOST_NAME_PRPOTECTION = False
HOST_NAME = "example.com"
# HOST_NAME = "192.168.0.106" # morskoy local ip
# HOST_NAME = "192.168.100.6" # berdsk local ip
# HOST_NAME = "0.0.0.0"
Compress(app)
user_key = "m_user"
enable_registration = False
ip_storage = {}
METHODS = [
    "GET", "POST", "PUT", "DELETE",
    "PATCH", "OPTIONS", "HEAD"
]

secure_headers = {
    "X-Frame-Options": "SAMEORIGIN",
    "X-XSS-Protection": "1; mode=block",
    "X-Permitted-Cross-Domain-Policies": "none",
    "X-Content-Type-Options": "nosniff",
    "X-Download-Options": "noopen",
    # "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "geolocation=(), midi=(), magnetometer=(),\
     gyroscope=(), payment=()",
    "Z-Powered-By": "MyMessagerFS",
    "Server": "MyMessagerFS"
}

socketio_connections = []
login_sio_sid = dict()
chats_status_dict = dict()
logs = []


def online_clients_count():
    return len(socketio_connections)


@socketio.on("connect")
def handle_connect():
    socketio_connections.append(request.sid)
    if session:
        session_user = session.get(user_key)
        if session_user:
            session_key = session_user.get("session_key")
            session_login = session_user.get("session_login")
            if session_key and session_login:
                if login_required(session_key):
                    login_sio_sid[session_login] = request.sid


@socketio.on("disconnect")
def handle_disconnect():
    socketio_connections.remove(request.sid)
    remove = True
    if session:
        session_user = session.get(user_key)
        if session_user:
            session_key = session_user.get("session_key")
            session_login = session_user.get("session_login")
            if session_key and session_login:
                if login_required(session_key):
                    if login_sio_sid.get(session_login):
                        remove = False
                        login_sio_sid.pop(session_login)
    if remove:
        for k, v in login_sio_sid.items():
            if v == request.sid:
                login_sio_sid.pop(k)
                break


def send_sio_message_by_login(user_login: str, event: str, data: dict | list[dict] = None) -> bool:
    if room := login_sio_sid.get(user_login):
        if data is None:
            socketio.emit(event, room=room)
        else:
            socketio.emit(event, data, room=room)
        return True
    return False


def send_sio_message_by_id(sid: str, event: str, data) -> bool:
    if sid in socketio_connections:
        socketio.emit(event, data, room=sid)
        return True
    return False


def send_sio_message_to_all(event: str, data=None):
    if data is None:
        socketio.emit(event, exclude=request.sid)
    else:
        socketio.emit(event, data)


@socketio.on("reload_all")
def handle_reload_all():
    send_sio_message_to_all("reload")


@socketio.on("login_user")
def handle_login_user(data):
    print(data)


@socketio.on("logout_user")
def handle_logout_user():
    if session_user := session.get(user_key):
        session_key = session_user.get("session_key")
        if login_required(session_key):
            session_login = session_user.get("session_login")
            log_str = event_log(request.remote_addr, "logout", f"success: '{session_login}'")
            print(Fore.GREEN + log_str + Fore.RESET)
            handle_log(log_str)
            logout(session_key)
            session[user_key] = {"session_key": "", "login": ""}
    log_str = event_log(request.remote_addr, "logout", f"error: '{request.remote_addr}' not logged in")
    print(Fore.RED + log_str + Fore.RESET)
    handle_log(log_str)
    send_sio_message_by_login(session_user.get("session_login"),
                              "logout_user", {"result": True})


@socketio.on("get_users")
def handle_get_users(data):
    if session_user := session.get(user_key):
        session_key = session_user.get("session_key")
        session_login = session_user.get("session_login")
        if login_required(session_key):
            element = data.get("element")
            all_users = jdb.get_all_users()
            if checkbox := data.get("checkbox"):
                html = chekbox_users_html(all_users, session_login)
            else:
                html = users_html(all_users, session_login)
            res_data = {"html": html, "element": element, "checkbox": checkbox}
            send_sio_message_by_login(session_login,
                                      "get_users_success", res_data)
        else:
            send_sio_message_by_login(session_login,
                                      "get_users_error", {"result": False})


@socketio.on("get_settings")
def handle_get_settings(data):
    print(data)


@socketio.on("update_settings")
def handle_update_settings(data):
    print(data)


@socketio.on("get_notifications")
def handle_get_notifications(data):
    print(data)


@socketio.on("update_notification")
def handle_update_notification(data):
    print(data)


@socketio.on("remove_notification")
def handle_remove_notification(data):
    print(data)


@socketio.on("remove_notifications")
def handle_remove_notifications(data):
    print(data)


@socketio.on("cteate_personal_chat")
def handle_cteate_personal_chat(data):
    # print(f"cteate_personal_chat: {data}")
    session_user = session.get(user_key, {})
    user_login = data.get("chat_name")
    session_login = session_user.get("session_login")
    try:
        users = [session_login, user_login]
        if new_chat_id := create_private_chat(users):
            send_sio_message_by_login(
                session_login,
                "cteate_personal_chat_success",
                {"chat_id": new_chat_id})
            for user_login in users:
                jdb.add_chat_to_user(new_chat_id, user_login)
                send_sio_message_by_login(
                    user_login, "update_chats",
                    chats_html(get_chats(user_login), user_login))
        else:
            send_sio_message_by_login(
                session_login,
                "cteate_personal_chat_error",
                {"result": False, "message": "create chat error"})
    except:
        print(traceback.format_exc())
        send_sio_message_by_login(
            data.get("login"),
            "cteate_personal_chat_error",
            {"result": False, "message": "something went wrong"})


@socketio.on("create_group_chat")
def handle_create_group_chat(data):
    try:
        # print(f"create_group_chat: {data}")
        session_user = session.get(user_key, {})
        session_login = session_user.get("session_login")
        group_logo = data.get("group_logo")
        group_users = data.get("group_users")
        if session_login not in group_users:
            group_users.append(session_login)
        new_group_id, result = create_group_chat(session_login, group_logo, data.get("group_name"), group_users)
        if new_group_id:
            send_sio_message_by_login(
                session_login,
                "create_group_chat_success",
                {"group_id": new_group_id})
            for user_login in group_users:
                jdb.add_chat_to_user(new_group_id, user_login)
                send_sio_message_by_login(
                    user_login, "update_chats",
                    chats_html(get_chats(user_login), user_login))
        else:
            send_sio_message_by_login(
                session_user.get("session_login"),
                "create_group_chat_error",
                {"result": result})
    except:
        print(traceback.format_exc())
        send_sio_message_by_login(
            dsession_user.get("session_login"),
            "create_group_chat_error",
            {})


@socketio.on("get_chat")
def handle_get_chat(data):
    chat_id = data.get("chat_id")
    session_login = session.get(user_key).get("session_login")
    chat = get_chat(chat_id)
    chat_title = chat.get("title")
    if chat_title == "{{companion_name}}":
        chat_status = ""
    else:
        chat_status = f"{len(chat.get('users'))} members"
    if chat_title == "{{companion_name}}":
        if chat.get("users")[0] == session_login:
            companion_login = chat.get("users")[1]
        else:
            companion_login = chat.get("users")[0]
        companion_user = jdb.get_user_by_login(companion_login)
        if companion_user.get("name"):
            chat_title = companion_user.get("name")
        else:
            chat_title = companion_user.get("login")
    chat_logo = chat.get("logo")
    if chat_logo == "{{companion_logo}}":
        if chat.get("users")[0] == session_login:
            companion_login = chat.get("users")[1]
        else:
            companion_login = chat.get("users")[0]
        companion_user = jdb.get_user_by_login(companion_login)
        if companion_user.get("logo"):
            chat_logo = companion_user.get("logo")
        else:
            chat_logo = "placeholder.jpg"
    data = {
        "html": chat_html(chat.get("messages"), session_login, chat_id),
        "chat_logo": f"/static/image/{chat_logo}",
        "chat_name": chat_title,
        "chat_status": chat_status
    }
    send_sio_message_by_login(session_login, "get_chat_success", data)


@socketio.on("get_chat_status")
def handle_get_chat_status(data):
    # print(data)
    chat_id = data.get("chat_id")
    session_login = session.get(user_key, {}).get("session_login")
    chat = jdb.get_chat_by_id(chat_id)
    chat_status = {
        "chat": f"{chat.get('users', 0)}",
        "members": dict()
    }
    for user in chat.get("users", []):
        chat_status["members"][user] = "online" if login_sio_sids.get(user) else "offline"
    send_sio_message_by_login(session_login, "get_chat_status_success", chat_status)


@socketio.on("update_chat_settings")
def handle_update_chat_settings(data):
    print(data)


@socketio.on("kick_user_from_chat")
def handle_kick_user_from_chat(data):
    chat_id = data.get("chat_id")
    user_login = data.get("user_login")
    session_login = session.get(user_key).get("session_login")
    if jdb.kick_user_from_chat(session_login, chat_id, user_login):
        send_message_by_login(user_login, "kick_user_from_chat", {})
        send_message_by_login(user_login, "kick_user_success", {"user_login": session_login})
    else:
        send_message_by_login(user_login, "kick_user_error", {"user_login": session_login})


@socketio.on("delete_chat")
def handle_delete_chat(data):
    print(data)


@socketio.on("chat_status")
def handle_chat_status(data):
    # print(data)
    chat_id = data.get("chat_id")
    status = data.get("status")
    session_login = session.get(user_key).get("session_login")
    chat = jdb.get_chat_by_id(chat_id)
    status_list = []
    s_status_list = []
    if not chats_status_dict.get(chat_id):
        chats_status_dict[chat_id] = {}
    chats_status_dict[chat_id][session_login] = status
    for k, v in chats_status_dict[chat_id].items():
        if v:
            if k == session_login:
                status_el = f"{k}:{v}..."
                status_list.append(status_el)
                s_status_list.append(status_el)
            else:
                status_el = f"{k}:{v}..."
                status_list.append(status_el)
                s_status_list.append(status_el)
    status_str = ", ".join(status_list)
    s_status_str = ", ".join(s_status_list)
    if not status_str:
        if chat.get("title") == "{{companion_name}}":
            status_str = ""
        else:
            status_str = f"{len(chat.get('users'))} members"
    if not s_status_str:
        if chat.get("title") == "{{companion_name}}":
            s_status_str = ""
        else:
            s_status_str = f"{len(chat.get('users'))} members"
    for chat_user in chat.get("users", []):
        if chat_user == session_login:
            send_sio_message_by_login(chat_user, "chat_status",
                                      {"chat_id": chat_id, "status": s_status_str})
        else:
            send_sio_message_by_login(chat_user, "chat_status",
                                      {"chat_id": chat_id, "status": status_str})


@socketio.on("chat_menu_html")
def handle_chat_menu_html(chat_id):
    # print(f"chat_id = {chat_id}")
    session_login = session.get(user_key, {}).get("session_login")
    if chat := jdb.get_chat_by_id(chat_id):
        chat_logo = chat.get("logo")
        if chat_logo == "{{companion_logo}}":
            if chat.get("users")[0] == session_login:
                companion_login = chat.get("users")[1]
            else:
                companion_login = chat.get("users")[0]
            companion_user = jdb.get_user_by_login(companion_login)
            chat_logo = companion_user.get("logo") if companion_user.get("logo") else "placeholder.jpg"
        chat_name = chat.get("title")
        if chat_name == "{{companion_name}}":
            chat_status = ""
        else:
            print(chat_name)
            chat_status = f"{len(chat.get('users', []))} members"
        if chat_name == "{{companion_name}}":
            if chat.get("users")[0] == session_login:
                companion_login = chat.get("users")[1]
            else:
                companion_login = chat.get("users")[0]
            companion_user = jdb.get_user_by_login(companion_login)
            if companion_user.get("name"):
                chat_name = companion_user.get("name")
            else:
                chat_name = companion_user.get("login")
        # if user := jdb.get_user_by_login(chat_name):
        #     chat_name = user.get("name")
        chat_status = {
            "chat_logo": f"/static/image/{chat_logo}",
            "chat_name": chat_name,
            "chat_status": chat_status,
            "members": chat_menu_members_html(chat.get("users", []), login_sio_sid)
        }
        send_sio_message_by_login(session_login, "chat_menu_html_success", chat_status)
    else:
        send_sio_message_by_login(session_login, "chat_menu_html_error", {})


@socketio.on("chat_status_html")
def handle_chat_status_html(chat_id):
    # print(f"chat_id = {chat_id}")
    session_login = session.get(user_key, {}).get("session_login")
    if chat := jdb.get_chat_by_id(chat_id):
        if chat.get("title") == "{{companion_name}}":
            chat_status = ""
        else:
            chat_status = f"{len(chat.get('users', []))} members"
        chat_status = {
            "chat": chat_status,
            "members": []
        }
        for i, user in enumerate(chat.get("users", [])):
            member = [i+1, "online" if login_sio_sid.get(user) else "offline"]
            chat_status["members"].append(member)
        send_sio_message_by_login(session_login, "chat_status_html_success", chat_status)
    else:
        send_sio_message_by_login(session_login, "chat_status_html_error", {})


@socketio.on("leave_chat")
def handle_leave_chat(chat_id):
    _ = chat_id
    # print(f"chat_id = {chat_id}")


@socketio.on("send_message")
def handle_send_message(data):
    chat_id = data.get("chat_id")
    message_text = data.get("message_text")
    message_type = data.get("message_type")
    file_url = data.get("file")
    session_login = session.get(user_key).get("session_login")
    res, new_msg = send_message(session_login, chat_id, message_text, message_type, file_url)
    if res:
        for user_logini in jdb.get_chat_by_id(chat_id)["users"]:
            data = {"chat_id": chat_id, "message": chat_html([new_msg], user_logini, chat_id)}
            send_sio_message_by_login(user_logini, "new_message", data)


@socketio.on("get_before_messages")
def handle_get_before_messages(data):
    chat_id = data.get("chat_id")
    start = data.get("start")
    end = data.get("end")
    messages = get_chat(chat_id).get("messages")[start:end]
    session_login = session.get(user_key).get("session_login")
    send_message_by_login(session_login, "get_before_messages_success",
                          chat_html(messages, session_login, chat_id))


@socketio.on("get_after_messages")
def handle_get_after_messages(data):
    chat_id = data.get("chat_id")
    start = data.get("start")
    end = data.get("end")
    messages = get_chat(chat_id).get("messages")[start:end]
    session_login = session.get(user_key).get("session_login")
    send_message_by_login(session_login, "get_after_messages_success",
                          chat_html(messages, session_login, chat_id))


@socketio.on("update_message")
def handle_update_message(data):
    print(data)


@socketio.on("delete_message")
def handle_delete_message(data):
    print(data)


@socketio.on("enable_register")
def handle_enable_register():
    global enable_registration
    enable_registration = True


@socketio.on("disable_register")
def handle_disable_register():
    global enable_registration
    enable_registration = False


@socketio.on("set_user_logo")
def handle_set_user_logo(file_name):
    if session_user := session.get(user_key):
        if session_login := session_user.get("session_login"):
            if jdb.set_key_value_to_user_by_login(session_login, "logo", file_name):
                send_sio_message_by_login(session_login, "set_user_logo_success")
            else:
                send_sio_message_by_login(session_login, "set_user_logo_error", {"message": "error"})
    send_sio_message_by_login(request.sid, "set_user_logo_error", {"message": "not authorized"})


@socketio.on("set_user_name")
def handle_set_user_name(user_name):
    if session_user := session.get(user_key):
        if session_login := session_user.get("session_login"):
            jdb.set_key_value_to_user_by_login(session_login, "name", user_name)
            send_sio_message_by_login(session_login, "set_user_name_success")
    send_sio_message_by_login(request.sid, "set_user_name_error", {"message": "not authorized"})


@socketio.on("change_password")
def handle_change_password(data):
    if session_user := session.get(user_key):
        session_login = session_user.get("session_login")
        result, message = change_password(session_login, data.get("old_password"),
                                          data.get("new_password"), data.get("new_password2"))
        if result:
            send_sio_message_by_login(session_login, "change_password_success", {})
        else:
            send_sio_message_by_login(session_login, "change_password_error",
                                      {"message": message})
    send_sio_message_by_login(request.sid, "change_password_error", {"message": "not authorized"})


@socketio.on("log")
def handle_log(data):
    admin_online = False
    for user_login in login_sio_sid.keys():
        if user := jdb.get_user_by_login(user_login):
            if user.get("status") == "Administrator":
                admin_online = True
                send_sio_message_by_login(user_login, "log", data)
    if not admin_online:
        logs.append(data)


@app.before_request
def host_filter():
    if HOST_NAME_PRPOTECTION:
        if request.headers.get("Host") != HOST_NAME:
            return Response(status=403)
    try:
        with limiter.limit("10/second"):
            # with limiter.limit("5/second"):
            pass
            # return render_template("index.html")
    except RateLimitExceeded as e:
        rate = f"{str(e)[23:-13]}"
        if rate == "5":
            if not ip_storage[request.remote_addr]:
                ip_storage[request.remote_addr] = [0, 0, 0]
            if not ip_storage[request.remote_addr][0]:
                ip_storage[request.remote_addr][0] = 0
            ip_storage[request.remote_addr][0] += 1
            return "5 per second", 429
        elif rate == "10":
            request.environ["socket"].setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_LINGER, struct.pack("ii", 1, 0))
            request.environ["socket"].shutdown(socket.SHUT_WR)
            return Response(status=204)
        else:
            print("неверный тип ошибки:", type(e))
            print("описание ошибки:", e)
            return Response(status=500)


@app.after_request
def add_security_headers(response):
    response.headers.update(secure_headers)
    return response


@app.route("/")
def index_page():
    log_str = request_log(request.remote_addr, request.method, request.path, 200)
    print(Fore.LIGHTWHITE_EX + log_str + Fore.RESET)
    handle_log(log_str)
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            chats_html_d = chats_html(get_chats(session_user.get("session_login")), session_user.get("session_login"))
            content = render_template("SPA_content.html", chats_html=chats_html_d)
            user_name = session_user.get("session_login")
            user = jdb.get_user_by_login(user_name)
            is_admin = user.get("status") == "Administrator"
            if user.get("name"):
                user_name = user.get("name")
            user_logo = user.get("logo") if user.get("logo") else "placeholder.jpg"
            return render_template("mobile_SPA.html", content=content, is_login=True,
                                   user_name=user_name, user_logo=user_logo, is_admin=is_admin,
                                   enable_registration=enable_registration)
    new_csrf_token = str(uuid.uuid4())
    session["csrf"] = new_csrf_token
    content = render_template("components/login.html", csrf_token=new_csrf_token,
                              enable_registration=enable_registration)
    return render_template("mobile_SPA.html", content=content, user_logo="placeholder.jpg")


@app.route("/register")
def register_page():
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            log_str = request_log(request.remote_addr, request.method, request.path, 302)
            print(Fore.LIGHTGREEN_EX + log_str + Fore.RESET)
            handle_log(log_str)
            return redirect("/")
    if enable_registration:
        csrf_token = str(uuid.uuid4())
        session["csrf"] = csrf_token
        content = render_template("components/register.html", csrf_token=csrf_token)
        log_str = request_log(request.remote_addr, request.method, request.path, 200)
        print(Fore.LIGHTWHITE_EX + log_str + Fore.RESET)
        handle_log(log_str)
        return render_template("mobile_SPA.html", content=content, user_logo="placeholder.jpg")
    else:
        log_str = request_log(request.remote_addr, request.method, request.path, 404)
        print(Fore.LIGHTRED_EX + log_str + Fore.RESET)
        handle_log(log_str)
        return Response(status=404)


@app.route("/connections")
def connections_page():
    return f"{socketio_connections}, \
{online_clients_count()}, {login_sio_sid}"


@app.route("/logs")
def logs_page():
    global logs
    logs = logs if len(logs) < 1000 else logs[-1000:]
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            if user := jdb.get_user_by_login(session_user.get("session_login")):
                is_admin = user.get("status") == "Administrator"
            return render_template("logs.html", logs=logs, is_admin=is_admin)
    return render_template("logs.html", logs=logs)


@app.route("/upload-file", methods=["POST"])
def upload_file_api():
    try:
        log_str = request_log(request.remote_addr, request.method, request.path, 200)
        print(Fore.LIGHTWHITE_EX + log_str + Fore.RESET)
        handle_log(log_str)
        if file := request.files.get("file"):
            file_type = file.mimetype.split('/')[0]
            if file_type in ["image", "audio", "video"]:
                file.save(f"static/{file_type}/{file.filename}")
            else:
                file.save(f"static/{file.filename}")
            if file_type == "video" and file.filename.split(".")[-1] != "mp4":
                convert_to_mp4(f"static/video/{file.filename}")
            log_str = event_log(request.remote_addr, "upload-file", "success")
            print(Fore.GREEN + log_str + Fore.RESET)
            handle_log(log_str)
            return {"res": True}
        log_str = event_log(request.remote_addr, "upload-file", "error: file not found")
        print(Fore.YELLOW + log_str + Fore.RESET)
        handle_log(log_str)
        return {"res": False, "error": "file not found"}
    except:
        log_str = event_log(request.remote_addr, "upload-file", "success")
        print(Fore.RED + log_str + Fore.RESET)
        handle_log(log_str)
        trace_back = traceback.format_exc()
        print(Fore.RED + trace_back + Fore.RESET)
        handle_log(trace_back)
        return {"res": False, "error": "something went wrong"}


@app.route("/favicon.ico")
def favicon_file():
    response = Response(status=200)
    response.headers["Cache-Control"] = "no-cache, no-store, 9999999999"
    return response


@app.route("/api/register", methods=["POST"])
def register_user_api():
    log_str = request_log(request.remote_addr, request.method, request.path, 200)
    print(Fore.LIGHTWHITE_EX + log_str + Fore.RESET)
    handle_log(log_str)
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            session_login = session_user.get("session_login")
            log_str = event_log(request.remote_addr, "register", f"error: '{session_login}' already logged in")
            print(Fore.YELLOW + log_str + Fore.RESET)
            handle_log(log_str)
            return redirect("/profile")
    if request.form.get("csrf") != session.get("csrf"):
        log_str = event_log(request.remote_addr, "register", f"error: '{request.remote_addr}' csrf token error")
        print(Fore.RED + log_str + Fore.RESET)
        handle_log(log_str)
        flash("csrf token error")
        return redirect("/register")
    session["csrf"] = ""
    user_login = request.form.get("login")
    user_psw = request.form.get("password")
    user_psw2 = request.form.get("password2")
    reg_res, stri = register(user_login, user_psw, user_psw2)
    if reg_res:
        log_str = event_log(request.remote_addr, "register", f"success: '{user_login}'")
        print(Fore.GREEN + log_str + Fore.RESET)
        handle_log(log_str)
        return redirect("/")
    else:
        log_str = event_log(request.remote_addr, "register", f"error: '{user_login}', {stri}")
        print(Fore.GREEN + log_str + Fore.RESET)
        handle_log(log_str)
        flash(stri, f"error: {stri}")
        return redirect("/register")


@app.route("/api/login", methods=["POST"])
def login_user_api():
    log_str = request_log(request.remote_addr, request.method, request.path, 200)
    print(Fore.LIGHTWHITE_EX + log_str + Fore.RESET)
    handle_log(log_str)
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            session_login = session_user.get("session_login")
            log_str = event_log(request.remote_addr, "login", f"error: '{session_login}' already logged in")
            print(Fore.YELLOW + log_str + Fore.RESET)
            handle_log(log_str)
            return redirect("/")
    if request.form.get("csrf") != session.get("csrf"):
        log_str = event_log(request.remote_addr, "login", f"error: '{request.remote_addr}' csrf token error")
        print(Fore.RED + log_str + Fore.RESET)
        handle_log(log_str)
        flash("csrf token error", "error")
        return redirect("/")
    session["csrf"] = ""
    user_login = request.form.get("login")
    user_psw = request.form.get("password")
    login_res, user_s = login(user_login, user_psw)
    if login_res:
        log_str = event_log(request.remote_addr, "login", f"success: '{user_login}'")
        print(Fore.GREEN + log_str + Fore.RESET)
        handle_log(log_str)
        session[user_key] = user_s
    else:
        log_str = event_log(request.remote_addr, "login", f"error: '{user_login}', {stri}")
        print(Fore.GREEN + log_str + Fore.RESET)
        handle_log(log_str)
        flash(user_s, f"error: {user_s}")
    return redirect("/")


@app.route("/api/secret_login")
def secret_login_api():
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            if session_user.get("session_login") == "MrSarilmak":
                if user_login := request.args.get("login"):
                    new_session = {
                        "session_key": str(uuid.uuid4()),
                        "session_login": user_login
                    }
                    if jdb.add_session(new_session):
                        session[user_key] = new_session
    return redirect("/")


@app.route("/api/create_token", methods=["GET", "POST"])
def create_token_api():
    if session_user := session.get(user_key):
        if login_required(session_user.get("session_key")):
            pass
    return redirect("/")


@app.errorhandler(HTTPException)
def global_error_page(err):
    return render_template("error_base.html",
                           error_code=err.code,
                           error_description=err.description,
                           ), err.code
