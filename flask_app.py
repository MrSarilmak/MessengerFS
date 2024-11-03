# import threading
from views import socketio, app, ErrorTestingWSGIRequestHandler
# from api import app as api_app, uvicorn


# def api_thread():
#     uvicorn.run(api_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # threading.Thread(target=api_thread).start()
    socketio.run(app, "0.0.0.0", 80, allow_unsafe_werkzeug=True, request_handler=ErrorTestingWSGIRequestHandler)
    # socketio.run(app, "0.0.0.0", 80)
