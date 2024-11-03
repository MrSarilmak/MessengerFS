import json
from logic import *


with open("bufer.json", "r") as file_io:
    chats = json.load(file_io)
new_chats = []
for chat in chats:
    new_messages = []
    for message in chat.get("messages", []):
        # print(message)
        if isinstance(message.get("time"), str):
            msg_time = message.get("time")
            if len(msg_time) == 5:
                msg_time = "19-09-2024 " + msg_time + ":00"
            print(msg_time)
            message["time"] = dt_to_timestamp(msg_time)
            if message.get("date"):
                message.pop("date")
        new_messages.append(message)
    chat["messages"] = new_messages
    new_chats.append(chat)
with open("bufer.json", "w") as file_io:
    json.dump(new_chats, file_io, indent=2, ensure_ascii=False)
# jdb.save_table("chats", new_chats)
# for i in range(1, 9):
#     print(f"00:0{i} = {dt_to_timestamp('19-09-2022 00:08:00')}")
# 00:01 = 1640970060.0
# 00:02 = 1640970120.0
# 00:03 = 1640970180.0
# 00:04 = 1640970240.0
# 00:05 = 1640970300.0
# 00:06 = 1640970360.0
# 00:07 = 1640970420.0
# 00:08 = 1640970480.0
