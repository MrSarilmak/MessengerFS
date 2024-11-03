import json
import traceback


class JsonDb:
    def __init__(self):
        pass

    @staticmethod
    def load_table(table_name: str) -> list[dict] | None:
        json_db_file_io = None
        try:
            json_db_file_io = open(f"db/db_data/{table_name}.json", "r", encoding="utf-8")
            return json.load(json_db_file_io)
        except:
            print(traceback.format_exc())
            return None
        finally:
            if json_db_file_io:
                json_db_file_io.close()

    @staticmethod
    def save_table(table_name: str, data: dict) -> bool:
        json_db_file_io = None
        try:
            json_db_file_io = open(f"db/db_data/{table_name}.json", "w", encoding="utf-8")
            json.dump(data, json_db_file_io, ensure_ascii=False, indent=2)
            return True
        except:
            print(traceback.format_exc())
            return False
        finally:
            if json_db_file_io:
                json_db_file_io.close()

    # user
    def add_user(self, user: dict) -> bool:
        try:
            table_users = self.load_table("users")
            table_users.append(user)
            self.save_table("users", table_users)
            return True
        except:
            return False

    def get_all_users(self) -> list[dict]:
        return self.load_table("users")

    def user_in_chat(self, user_login: str, chat_id: int) -> bool:
        for user_logini in self.get_chat_by_id(chat_id).get("users"):
            if user_logini == user_login:
                return True
        return False

    def get_user_by_login(self, user_login: str) -> dict | None:
        if user_login:
            if users := self.load_table("users"):
                for user in users:
                    if user.get("login") == user_login:
                        return user
        return None

    def get_user_by_session_key(self, session_key: str) -> dict | None:
        for session in self.load_table("sessions"):
            if session.get("session_key") == session_key:
                return self.get_user_by_login(session.get("login"))
        return None

    def get_user_index_by_login(self, user_login: str) -> int | None:
        for index, user in enumerate(self.load_table("users")):
            if user.get("login") == user_login:
                return index
        return None

    def get_key_value_from_user_by_login(self, user_login: str, key: str) -> str | int | bool | list | dict | None:
        for user in self.load_table("users"):
            if user.get("login") == user_login:
                return user.get(key)
        return None

    def set_key_value_to_user_by_login(self, user_login: str, key: str,
                                       value: str | int | bool | list | dict) -> bool:
        users = self.load_table("users")
        if users:
            for i, user in enumerate(users):
                if user.get("login") == user_login:
                    user[key] = value
            users[i] = user
            if self.save_table("users", users):
                return True
        return False

    def change_password(self, user_login: str, new_password_hash: str) -> None:
        self.set_key_value_to_user_by_login(user_login, "password", new_password_hash)

    def remove_user(self, user: dict) -> bool:
        try:
            users = self.load_table("users")
            if users:
                users.remove(user)
                if self.save_table("users", users):
                    return True
        except:
            return False

    # session
    def add_session(self, session: dict) -> bool:
        try:
            sessions = self.load_table("sessions")
            if sessions is not None:
                sessions.append(session)
                if self.save_table("sessions", sessions):
                    return True
                else:
                    print("save table error")
                    return False
            else:
                print("no sessions")
                return False
        except:
            print(traceback.format_exc())
            return False

    def get_all_sessions(self) -> list:
        return self.load_table("sessions")

    def get_session_by_login(self, email: str) -> dict | None:
        for session in self.load_table("sessions"):
            if session.get("login") == email:
                return session
        return None

    def get_session_by_key(self, session_key: str) -> dict | None:
        if sessions := self.load_table("sessions"):
            for session in sessions:
                if session.get("session_key") == session_key:
                    if session.get("user_ip"):
                        session.pop("user_ip")
                    return session
        return None

    def remove_session(self, session: dict) -> bool:
        try:
            sessions = self.load_table("sessions")
            if sessions:
                sessions.remove(session)
                if self.save_table("sessions", sessions):
                    return True
            return False
        except:
            return False

    # token
    def add_token(self, token: dict) -> bool:
        try:
            tokens = self.load_table("tokens")
            if tokens:
                tokens.append(token)
                if self.save_table("tokens", tokens):
                    return True
            return False
        except:
            return False

    def get_all_tokens(self) -> list:
        return self.load_table("tokens")

    def exist_token(self, token: str) -> bool:
        for tokeni in self.load_table("tokens"):
            if tokeni == token:
                return True
        return False

    def remove_token(self, token: dict) -> bool:
        try:
            tokens = self.load_table("tokens")
            if tokens:
                tokens.remove(token)
                if self.save_table("tokens", tokens):
                    return True
            return False
        except:
            return False

    # chats
    def add_chat(self, chat: dict) -> bool:
        try:
            chats = self.load_table("chats")
            if chats:
                chats.append(chat)
                if self.save_table("chats", chats):
                    return True
            return False
        except:
            return False

    def get_chat_by_id(self, chat_id: str) -> dict | None:
        chats = self.load_table("chats")
        if chats:
            for chat in chats:
                if chat.get("id") == chat_id:
                    # print(type(chat))
                    # print(chat)
                    return chat
        return None

    def get_chat_by_key_and_value(self, chat_key: str, chat_value: str) -> dict | None:
        chats = self.load_table("chats")
        if chats:
            for chat in chats:
                if chat.get(chat_key) == chat_value:
                    return chat
        return None

    def add_user_to_chat(self, chat_id: str, user_login: str) -> bool:
        try:
            chats = self.load_table("chats")
            users = self.load_table("users")
            transaction = False
            new_chats = []
            new_users = []
            if chats and users:
                for chat in chats:
                    if chat.get("id") == chat_id:
                        chat["users"].append(user_login)
                        transaction = True
                    new_chats.append(chat)
                if transaction:
                    for user in users:
                        if user.get("login") == user_login:
                            user["chats"].append(chat_id)
                        new_users.append(user)
                    if self.save_table("chats", chats):
                        if self.save_table("users", users):
                            return True
            return False
        except:
            return False

    def add_chat_to_user(self, chat_id: str, user_login: str) -> bool:
        try:
            new_users = []
            users = self.load_table("users")
            if users:
                for user in users:
                    if user.get("login") == user_login:
                        user["chats"].append(chat_id)
                    new_users.append(user)
                if self.save_table("users", new_users):
                    return True
            return False
        except:
            return False

    # message
    def add_message(self, chat_id: str, message: dict) -> bool:
        try:
            chats = self.load_table("chats")
            for i, chat in enumerate(chats):
                if chat.get("id") == chat_id:
                    chats[i]["messages"].append(message)
                    break
            self.save_table("chats", chats)
            return True
        except:
            return False

    def get_messages(self, chat_id: str) -> list:
        for chat in self.load_table("chats"):
            if chat.get("id") == chat_id:
                return chat.get("messages")
        return []

    def get_message_by_id(self, chat_id: str, reply_to_msg_id) -> dict | None:
        for chat in self.load_table("chats"):
            if chat.get("id") == chat_id:
                for message in chat.get("messages"):
                    if message.get("id") == reply_to_msg_id:
                        return message
        return None

    def remove_message(self, chat_id: str, message: dict) -> bool:
        try:
            chats = self.load_table("chats")
            for i, chat in enumerate(chats):
                if chat.get("id") == chat_id:
                    chats[i]["messages"].remove(message)
                    break
            self.save_table("chats", chats)
            return True
        except:
            return False
