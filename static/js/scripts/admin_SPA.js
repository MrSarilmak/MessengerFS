if (typeof socket == "undefined") {
    socket = io();
}

socket.on("get_users", function (data) {
    console.log("get_users");
    console.log(data);
});

socket.on("log", function (data) {
    if(window.location.pathname == "/logs") {
        document.body.innerHTML += "<p>" + data + "</p>";
    }
});

function enable_register() {
    socket.emit("enable_register");
}

function disable_register() {
    socket.emit("disable_register");
}

function reload_all() {
    socket.emit("reload_all");
}