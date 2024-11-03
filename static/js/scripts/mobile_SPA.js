function create_only_mobile_el() {
  var only_mobile_el = document.createElement("div");
  only_mobile_el.id = "only_mobile";
  only_mobile_el.innerHTML = "<p>Only for mobile</p>";
  document.body.appendChild(only_mobile_el);
}

async function checkPlatform() {
  let platformDetails = await navigator.userAgentData?.getHighEntropyValues([
    "architecture",
    "platform",
    "platformVersion",
    "model",
    "bitness",
    "uaFullVersion",
  ]);
  if (
    !platformDetails?.mobile &
    (typeof platformDetails?.mobile == "boolean")
  ) {
    create_only_mobile_el();
  }
}
// checkPlatform();

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

function upload_file(file_query_selector) {
  const request = new XMLHttpRequest();
  request.open("POST", "/upload-file", false);
  var formData = new FormData();
  formData.append("file", document.querySelector(file_query_selector).files[0]);
  request.send(formData);
  if (request.status === 200) {
    var response_json = JSON.parse(request.responseText);
    if (response_json.res) {
      return response_json.res;
    } else {
      console.log(response_json);
      return false;
    }
  } else {
    console.log(request.responseText);
    return false;
  }
}

var sio = true;
var socket = null;
var selected_chat_type = "";
var selected_chat_id = "";
var start_loaded_messages = -10;
var end_loaded_messages = -1;
var create_group_modal_selected_users = [];
var create_priv_chat_modal_selected_user = "";
var reload_after_settings_close = false;
if (sio) {
  socket = io();
  socket.on("reload", function () {
    window.location.reload();
  });

  socket.on("login_user_success", function (data) {
    console.log("login_user_success");
    console.log(data);
  });
  socket.on("login_user_error", function (data) {
    console.log("login_user_error");
    console.log(data);
  });

  socket.on("logout_user", function (data) {
    // console.log("logout_user");
    // console.log(data);
    if (data.result) {
      window.location.reload();
    }
    close_modals();
  });

  socket.on("get_users_success", function (data) {
    $(data.element).html(data.html);
    if (!data.checkbox) {
      $("#create-private-chat-modal>.users>.user").on("click", function (event) {
        var text = "";
        if ($(event.target).hasClass("user-name")) {
          text = $(event.target).text();
        } else {
          text = $(event.target).children(".data").children(".user-name").text();
        }
        text = text.replaceAll(" ", "");
        text = text.replaceAll("\n", "");
        create_priv_chat_modal_selected_user = text;
        $("#create-private-chat-modal>.users>.user").removeClass("selected");
        if ($(event.target).hasClass("user-name")) {
          $(event.target).parent(".data").parent(".user").toggleClass("selected");
        } else {
          $(event.target).toggleClass("selected");
        }
      });
    }
  });
  socket.on("get_users_error", function (data) {
    console.log("get_users_error");
    console.log(data);
    // $("#create-group-modal_users").html(data);
  });

  socket.on("get_settings_success", function (data) {
    console.log("get_settings_success");
    console.log(data);
  });
  socket.on("get_settings_error", function (data) {
    console.log("get_settings_error");
    console.log(data);
  });

  socket.on("update_settings_success", function (data) {
    console.log("update_settings_success");
    console.log(data);
  });
  socket.on("update_settings_error", function (data) {
    console.log("update_settings_error");
    console.log(data);
  });

  socket.on("new_notification", function (data) {
    console.log("new_notification");
    console.log(data);
  });
  socket.on("get_notifications_success", function (data) {
    console.log("get_notifications_success");
    console.log(data);
  });
  socket.on("get_notifications_error", function (data) {
    console.log("get_notifications_error");
    console.log(data);
  });

  socket.on("remove_notification", function (data) {
    console.log("remove_notification");
    console.log(data);
  });
  socket.on("clear_notifications", function (data) {
    console.log("clear_notifications");
    console.log(data);
  });

  socket.on("cteate_personal_chat_success", function (data) {
    // console.log("cteate_personal_chat_success");
    // console.log(data);
  });
  socket.on("cteate_personal_chat_error", function (data) {
    console.log("cteate_personal_chat_error");
    console.log(data);
  });

  socket.on("create_group_chat_success", function (data) {
    // console.log("create_group_chat_success");
    // console.log(data);
  });
  socket.on("create_group_chat_error", function (data) {
    console.log("create_group_chat_error");
    console.log(data);
  });

  socket.on("get_chat_success", function (data) {
    $("#chat_messages").html(data.html);
    $("#chat_logo").attr("src", data.chat_logo);
    $("#chat_name").text(data.chat_name);
    $("#chat_status").text(data.chat_status);
    $("#chat-menu-group-status").text(data.chat_status);
    // start_loaded_messages = data.start;
    // end_loaded_messages = data.end;
  });
  socket.on("get_chat_error", function (data) {
    console.log("get_chat_error");
    console.log(data);
  });

  socket.on("update_chat_settings_success", function (data) {
    console.log("update_chat_settings_success");
    console.log(data);
  });
  socket.on("update_chat_settings_error", function (data) {
    console.log("update_chat_settings_error");
    console.log(data);
  });

  socket.on("kick_user_success", function (data) {
    console.log("kick_user_success");
    console.log(data);
  });
  socket.on("kick_user_error", function (data) {
    console.log("kick_user_error");
    console.log(data);
  });

  socket.on("delete_chat_success", function (data) {
    console.log("delete_chat_success");
    console.log(data);
  });
  socket.on("delete_chat_error", function (data) {
    console.log("delete_chat_error");
    console.log(data);
  });

  socket.on("chat_status", function (data) {
    if (data.chat_id == selected_chat_id) {
      $("#chat_status").text(data.status);
      $("#chat-menu-group-status").text(data.status);
    }
  });
  socket.on("chat_menu_html_success", function (data) {
    $("#chat-menu-group-logo").attr("src", data.chat_logo);
    $("#chat-menu-group-name").text(data.chat_name);
    $("#chat-menu-group-status").text(data.chat_status);
    $("#chat-menu-members").html(data.members);
  });
  socket.on("chat_menu_html_error", function (data) {
    console.log(data);
  });
  socket.on("chat_status_html_success", function (data) {
    console.log(data.chat);
    console.log(data.members);
    for (member of data.members) {
      $(`#us${member[0]}`).text(member[1])
    }
  });
  socket.on("chat_status_html_error", function (data) {
    console.log(data);
  });

  socket.on("leave_chat", function (data) {
    console.log("leave_chat");
    console.log(data);
  });

  socket.on("update_chats", function (data) {
    // console.log("update_chats");
    // console.log(data);
    $("#chats").html(data);
  });

  socket.on("send_message_success", function (data) {
    console.log("send_message_success");
    console.log(data);
  });
  socket.on("send_message_error", function (data) {
    console.log("send_message_error");
    console.log(data);
  });

  socket.on("new_message", function (data) {
    if (data.chat_id == selected_chat_id) {
      $("#zero-messages").remove();
      $("#chat_messages").append(data.message);
      var chat_messages = document.querySelector("#chat_messages");
      chat_messages.scrollTo(0, chat_messages.scrollHeight);
    } else {
      alert(`socket new message: not selected chat chat_id ${data.chat_id}`)
    }
  });
  socket.on("get_before_messages_success", function (data) {
    // console.log("get_before_messages_success");
    // console.log(data);
    $("#chat_messages").prepend(data);
  });
  socket.on("get_before_messages_error", function (data) {
    console.log("get_before_messages_error");
    console.log(data);
  });
  socket.on("get_after_messages_success", function (data) {
    // console.log("get_after_messages_success");
    // console.log(data);
    $("#chat_messages").append(data);
  });
  socket.on("get_after_messages_error", function (data) {
    console.log("get_after_messages_error");
    console.log(data);
  });

  socket.on("update_message_success", function (data) {
    console.log("update_message_success");
    console.log(data);
  });
  socket.on("update_message_error", function (data) {
    console.log("update_message_error");
    console.log(data);
  });

  socket.on("delete_message_success", function (data) {
    console.log("delete_message_success");
    console.log(data);
  });
  socket.on("delete_message_error", function (data) {
    console.log("delete_message_error");
    console.log(data);
  });

  // socket.emit("login_user", request_json);
  function logout_user() {
    if(socket.connected) {
      socket.emit("logout_user")
    } else {
      alert("logout_user: socket not connected")
    }
  }
  function get_users(element, checkbox) {
    if(socket.connected) {
      socket.emit("get_users", {"element": element, "checkbox": checkbox})
    } else {
      alert("get_users: socket not connected")
    }
  }

  // socket.emit("get_settings", request_json);
  // socket.emit("update_settings", request_json);

  // socket.emit("get_notifications", request_json);
  // socket.emit("update_notification", request_json);
  // socket.emit("remove_notification", request_json);
  // socket.emit("remove_notifications", request_json);

  // socket.emit("cteate_personal_chat", request_json);
  // socket.emit("create_group_chat", request_json);

  function get_chat(chat_id) {
    if(socket.connected) {
      socket.emit("get_chat", { chat_id: chat_id });
      return true;
    } else {
      alert("get_chat: socket not connected");
      return false;
    }
  }

  // socket.emit("update_chat_settings", request_json);

  // socket.emit("kick_user_from_chat", request_json);

  // socket.emit("delete_chat", request_json);

  $("input#message_text").on("focus", function (e) {
    if(socket.connected) {
      socket.emit("chat_status", {
        chat_id: selected_chat_id,
        status: "typing"
      });
    } else {
      alert("input#message_text focus: socket not connected")
    }
  });
  $("input#message_text").on("focusout", function (e) {
    if(socket.connected) {
      socket.emit("chat_status", {
        chat_id: selected_chat_id,
        status: ""
      });
    } else {
      alert("input#message_text focusout: socket not connected")
    }
  });

  function close_chat(chat_id) {
    if(socket.connected) {
      socket.emit("leave_chat", chat_id);
      $("#chat").css("display", "none");
      $("#chat-inner").css("display", "none");
      $("#global-header").css("display", "block");
      $("#chat-header").css("display", "none");
      $("#chat img.message_img").off("click");
    } else {
      alert("logout_user: socket not connected")
    }
  }

  function send_message() {
    var request_json = {
      chat_id: selected_chat_id,
      message_text: $("#message_text").val(),
      message_type: "text",
    };
    if ($("#message_file").val()) {
      var file_type = $("#message_file")[0]?.files[0]?.type?.split("/")[0];
      var file_name = $("#message_file").val().split("\\")[2];
      request_json.file = `/static/${file_type}/${file_name}`;
      if (file_type) {
        if (!["video", "image", "audio"].includes(file_type)) {
          file_type = "file";
          request_json.file = `/static/${file_name}`;
        }
        request_json["message_type"] = file_type;
      }
    }
    if (socket.connected) {
      socket.emit("send_message", request_json);
      $("#message_text").val("");
      if ($("#message_file").val()) {
        upload_file("#message_file");
        $("#message_file").val("");
      }
    } else {
      alert("send_message: socket not connected")
    }
  }
  $("input#message_text").on("keypress", function (e) {
    if (e.which == 13) {
      send_message();
    }
  });

  // socket.emit("get_before_messages", request_json);
  // socket.emit("get_after_messages", request_json);

  // socket.emit("update_message", request_json);

  // socket.emit("delete_message", request_json);

  socket.on("change_password_success", function (data) {
    close_modals();
  });
  socket.on("change_password_error", function (data) {
    $("#change-password-modal-error").text(data.message);
  });

  socket.on("set_user_name_success", function () {
    reload_after_settings_close = true;
  });
  socket.on("set_user_name_error", function (data) {
    console.log("set_user_name_error");
    console.log(data);
  });

  socket.on("set_user_logo_success", function () {
    $("#settings-modal-user-logo").addClass("success50");
    $("#settings-modal-user-logo").removeClass("error");
    reload_after_settings_close = true;
  });
  socket.on("set_user_logo_error", function (data) {
    console.log("set_user_logo_error");
    console.log(data);
    $("#settings-modal-user-logo").addClass("error");
    $("#settings-modal-user-logo").removeClass("success50");
    $("#settings-modal-user-logo").removeClass("success");
  });
}

function video_circle_events() {
  var video = null;
  var videos_el = document.querySelectorAll("video.message_video");
  for (var i = 0; i < videos_el.length; i++) {
    video = videos_el[i];
    video.currentTime = 0;

    video.ontimeupdate = function (event) {
      var video_id = event.srcElement.id;
      var progress_el = document.getElementById(`${video_id}2`);
      var cef = event.srcElement.duration / 100;
      progress = event.srcElement.currentTime / cef;
      if(progress == 0){progress = 0.4;}
      progress_el.style.setProperty("--progress", progress);
    };

    video.onclick = function (event) {
      if(event.srcElement.paused) {
        event.srcElement.play();
      } else {
        if(event.srcElement.ended) {
          event.srcElement.currentTime = 0;
          event.srcElement.play();
        } else {
          event.srcElement.pause();
        }
      }
    };
  }
}

function open_chat(chat_id) {
  if(socket.connected) {
    $("#chat").css("display", "block");
    $("#chat-inner").css("display", "block");
    $("#global-header").css("display", "none");
    $("#chat-header").css("display", "flex");
    $("#chat-header>div>a").attr("onclick", `close_chat('${chat_id}')`);
    selected_chat_id = chat_id;
    get_chat(chat_id);
    setTimeout(function () {
      $("#chat img.message_img").on("click", function (event) {
        $(event.target).toggleClass("focus");
      });
      var chat_messages = document.querySelector("#chat_messages");
      chat_messages?.scrollTo(0, chat_messages.scrollHeight);
      // var last_message = chat_messages.querySelector(".message:last-child");
      // console.log(last_message);
      // last_message.scrollIntoView({
      //   behavior: "smooth",
      // });
      video_circle_events();
    }, 50);
  } else {
    alert("open_chat: socket not connected")
  }
}

function close_modals() {
  $("#smoke").css("display", "none");
  $("#smoke-closable").css("display", "none");
  $("#void-closable").css("display", "none");
  $("#bm-modal").css("display", "none");
  $("#create-private-chat-modal").css("display", "none");
  $("#create-group-modal").css("display", "none");
  $("#create-group-modal-select-users").css("display", "none");
  $("#chat-menu-modal").css("display", "none");
  $("#pin-file-modal").css("display", "none");
  $("#settings-modal").css("display", "none");
  $("#change-password-modal").css("display", "none");
}

function open_bm() {
  close_modals();
  $("#smoke-closable").css("display", "block");
  $("#bm-modal").css("display", "block");
}

function open_create_private_chat_modal() {
  close_modals();
  $("#smoke").css("display", "block");
  $("#create-private-chat-modal").css("display", "block");
  get_users("#create-private-chat-modal_users", false);
}

function close_create_private_chat_modal() {
  close_modals();
  create_priv_chat_modal_selected_user = "";
  $("#create-private-chat-modal>.users>.user").removeClass("selected");
}

function open_create_group_modal() {
  close_modals();
  $("#smoke").css("display", "block");
  $("#create-group-modal").css("display", "block");
}

function open_create_group_select_users_modal() {
  var fc = 0;
  if (!$("#new_group_name").val()) {
    fc += 1;
    $("#new_group_name").addClass("error");
  }
  // if (!$("#new_group_logo").val()) {
  //   fc += 1;
  //   $("#new_group_logo").addClass("error");
  // }
  if (fc > 0) {
    fc = 0;
    return;
  }
  close_modals();
  $("#smoke").css("display", "block");
  $("#create-group-modal-select-users").css("display", "block");
  get_users("#create-group-modal_users", true);
};

function reset_create_group_modal() {
  $("#new_group_logo").removeClass("error");
  $("#new_group_name").removeClass("error");
}

$("#new_group_name").on("input", function () {
  if ($("#new_group_name").val()) {
    $("#new_group_name").removeClass("error")
  }
});

$("#new_group_logo").on("input", function () {
  if ($("#new_group_logo").val()) {
    $("#new_group_logo").addClass("success");
    $("#new_group_logo").removeClass("error");
  } else {
    $("#new_group_logo").removeClass("success");
  }
});

function close_settings_modal() {
  close_modals();
  if (reload_after_settings_close) {
    window.location.reload();
  }
}

function ocgsum_toggle(user_login) {
  if(create_group_modal_selected_users.find(
    (element) => element == user_login)) {
    create_group_modal_selected_users.pop(user_login);
  } else {
    create_group_modal_selected_users.push(user_login);
  }
}

function send_create_group() {
  var request_json = {
    group_name: $("#new_group_name").val(),
    group_users: create_group_modal_selected_users,
  };
  if ($("#new_group_logo").val()) {
    var file_name = $("#new_group_logo").val().split("\\")[2];
    request_json.group_logo = file_name;
  } else {
    request_json.group_logo = "placeholder.jpg"
  }
  if (socket.connected) {
    $("#new_group_name").val("");
    $("#new_group_users").val("");
    socket.emit("create_group_chat", request_json);
    if ($("#new_group_logo").val()) {
      upload_file("#new_group_logo");
      $("#new_group_logo").val("");
    }
  } else {
    alert("send_create_group: socket not connected")
  }
}

function send_create_priv_chat() {
  var request_json = {
    chat_name: create_priv_chat_modal_selected_user,
  };
  if (socket.connected) {
    socket.emit("cteate_personal_chat", request_json);
  } else {
    alert("send_create_priv_chat: socket not connected")
  }
}

function open_chat_menu() {
  $("#smoke-closable").css("display", "block");
  $("#chat-menu-modal").css("display", "block");
  socket.emit("chat_menu_html", selected_chat_id);
  // $("#chat-menu-head").html($("#open-chat-menu").html());
  // console.log(`open_chat_menu: ${chat_id}`);
}

$("#message_file").on("oninput", function () {
  $("#smoke-closable").css("display", "none");
  $("#chat-menu-modal").css("display", "none");
});

function open_chat_pin_file_menu() {
  $("#void-closable").css("display", "block");
  $("#pin-file-modal").css("display", "flex");
}

$("#message_file").on("input", function () {
  $("#void-closable").css("display", "none");
  $("#pin-file-modal").css("display", "none");
});

$("#message_file").on("cansel", function () {
  $("#void-closable").css("display", "none");
  $("#pin-file-modal").css("display", "none");
});

$("#chat-menu-group-logo").on("click", function () {
  $("#chat-menu-group-logo").toggleClass("focus");
});

function open_settings_modal() {
  close_modals();
  $("#settings-modal").css("display", "block");
}

function open_change_password_modal() {
  close_modals();
  $("#smoke-closable").css("display", "block");
  $("#change-password-modal").css("display", "block");
}

function change_password() {
  var request_json = {
    old_password: $("#change-password-modal_old-password").val(),
    new_password: $("#change-password-modal_new-password").val(),
    new_password2: $("#change-password-modal_new-password-repeat").val(),
  };
  if (socket.connected) {
    socket.emit("change_password", request_json);
  } else {
    alert("change_password: socket not connected")
  }
}

$("#settings-modal-user-name").on("focusout", function () {
  if ($("#settings-modal-user-name").text() != $("#settings-modal-old-user-name").text()) {
    socket.emit("set_user_name", $("#settings-modal-user-name").text());
  }
});

$("#settings-modal-user-logo").on("input", function () {
  if ($("#settings-modal-user-logo").val()) {
    var file_name = $("#settings-modal-user-logo").val().split("\\")[2];
    $("#settings-modal-user-logo").removeClass("error");
    // $("#settings-modal-user-logo").addClass("success50");
    socket.emit("set_user_logo", file_name);
    if (upload_file("#settings-modal-user-logo")) {
      // $("#settings-modal-user-logo").removeClass("success50");
      // $("#settings-modal-user-logo").addClass("success");
      $("#settings-modal div.logo").css("background-image", `url('/static/image/${file_name}')`);
    } else {
      $("#settings-modal-user-logo").removeClass("success50");
      // $("#settings-modal-user-logo").removeClass("success");
      $("#settings-modal-user-logo").addClass("error");
    }
  } else {
    // $("#settings-modal-user-logo").removeClass("success50");
    $("#settings-modal-user-logo").addClass("error");
  }
})

var user_logo_file_name = $("#settings-modal div.logo").attr("src");
$("#settings-modal div.logo").css("background-image", `url('${user_logo_file_name}')`);

$(document).ready(function () {
  
});
