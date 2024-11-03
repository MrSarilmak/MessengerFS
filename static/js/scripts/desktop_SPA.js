// async function checkPlatform() {
//     let platformDetails = await navigator.userAgentData?.getHighEntropyValues(["architecture",
//     "platform", "platformVersion", "model", "bitness", "uaFullVersion"]);
//     if (platformDetails?.mobile & typeof platformDetails?.mobile == "boolean") {
//         location.href = `http://${window.location.host}:8000/`;
//     }
// }
// checkPlatform();
spf.init();

// const registerServiceWorker = async () => {
//   if ("serviceWorker" in navigator) {
//     try {
//       const registration = await navigator.serviceWorker.register("/sw.js");
//       if (registration.installing) {
//         // console.log("Service worker installing");
//       } else if (registration.waiting) {
//         // console.log("Service worker installed");
//       } else if (registration.active) {
//         // console.log("Service worker active");
//       }
//     } catch (error) {
//       console.error(`Registration failed with ${error}`);
//     }
//   }
// };

function add_file_key(file_type, file_name) {
  const request = new XMLHttpRequest();
  request.open("POST", "/add-file-key", false);
  request.setRequestHeader("Content-Type", "application/json");
  request.send(JSON.stringify({"file_path": `static/${file_type}/${file_name}`}));
  if (request.status === 200) {
    var response_json = JSON.parse(request.responseText);
    if (response_json.res) {
      console.log(response_json.key);
      return response_json.key;
    } else {
      console.log(response_json);
    }
  } else {
    console.log(request.responseText);
  }
}

function upload_file(file_key) {
  const request = new XMLHttpRequest();
  request.open("POST", `/upload-file?key=${file_key}`, false);
  var formData = new FormData();
  formData.append("key", file_key);
  formData.append("file",
    document.querySelector("#message_file").files[0]);
  request.send(formData);
  if (request.status === 200) {
    var response_json = JSON.parse(request.responseText);
    if (response_json.res) {
    } else {
      console.log(response_json);
    }
  } else {
    console.log(request.responseText);
  }
}

// $(".chat").on("click", function (event) {
//   $(".chat").css("background-color", "");
//   event.target.style.backgroundColor = "#b7d4ff";
// });

var selected_chat_type = "";
var selected_chat_id = "";
var sio = true;
if (sio) {
  var socket = io();
  socket.on("new_message", function (data) {
    $("#zero-messages").remove();
    $("#chat_messages").append(data);
    // window.scrollTo(window.screenY);
    // window.scrollTo(0, document.body.scrollHeight);
    var chat_messages = document.querySelector("#chat_messages");
    chat_messages.scrollTo(0, chat_messages.scrollHeight);
  });

  socket.on("save_draft", function (data) {
    console.log("save_draft");
    console.log(data);
  });

  function save_draft(data) {
    var message_text = parseInt($("#message_text").val());
    data.text = message_text;
    socket.emit("save_draft", data);
  }

  socket.on("before_load", function (data) {
    console.log("before_load");
    console.log(data);
  });

  socket.on("after_load", function (data) {
    console.log("after_load");
    console.log(data);
  });

  function get_chat(chat_id) {
    socket.emit("get_chat", { chat_id: chat_id });
  }
  socket.on("get_chat", function (data) {
    console.log("get_chat");
    console.log(data);
  });

  socket.on("send_message", function (data) {
    console.log("send_message");
    console.log(data);
  });
  function send_message() {
    var file_key = "";
    var request_json = {
      chat_id: selected_chat_id,
      message_text: $("#message_text").val(),
      message_type: "text",
    };
    if ($("#message_file").val()) {
      var file_type = $("#message_file")[0]?.files[0]?.type?.split("/")[0];
      var file_name = $("#message_file").val().split("\\")[2];
      file_key = add_file_key(file_type, file_name);
      request_json.file = `/get-file?key=${file_key}`;
      if (file_type) {
        request_json["message_type"] = file_type;
      }
    }
    if (socket.connected) {
      socket.emit("send_message", request_json);
    }
    if ($("#message_file").val()) {
      upload_file(file_key);
      $("#message_file").val("");
    }
  }
}

function is_logged() {
  const request = new XMLHttpRequest();
  request.open("GET", "/api/is_logged", false);
  request.send(null);
  if (request.status === 200) {
    if (request.responseText === "True") {
      return true;
    } else if (request.responseText === "False") {
      return false;
    } else {
      console.log(request.responseText);
      return false;
    }
  } else {
    console.log(request.responseText);
    return false;
  }
}

function open_chat(chat_id) {
  window.location.href = `/chat/${chat_id}`;
}

$(document).ready(function () {
    selected_chat_id = window.location.href.split("/")[4];
});
