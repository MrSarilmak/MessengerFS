import json
import uvicorn
from fastapi import *
from jinja2 import Environment, PackageLoader, select_autoescape
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import StreamingResponse, JSONResponse

from logic import *
from views import HOST_NAME

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(docs_url="/api-docs", redoc_url="/api_docs")
env = Environment(
    loader=PackageLoader("api"),
    autoescape=select_autoescape()
)
app.state.limiter = limiter
HOST_NAME = HOST_NAME + ":8000"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    response = JSONResponse(
        {"res": "error",
         "error": "Too Many Requests",
         "description": f"Rate limit exceeded: {exc.detail}"}, status_code=429
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

ip_storage = {}
METHODS = [
    "GET", "POST", "PUT", "DELETE",
    "PATCH", "OPTIONS", "HEAD"
]

secure_headers = {
    "Cash-Control": "no-store",
    "Content-Type": "application/json",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "frame-ancestors 'none'",
    "Referrer-Policy": "same-origin",
    "Z-Powered-By": "JMTP-API",
    "Server": "JMTP-API"
}

html_secure_headers = {
    "Content-Security-Policy": "async default-src 'self', frame-ancestors 'none'",
    "Permissions-Policy": "npublickey-credentials-get=()",
    "Referrer-Policy": "no-referrer",
}


def json_response(data: dict, status_code: int = 200):
    content = json.dumps(data)
    return Response(content=content, status_code=status_code)


def template_request(request, template_name, **kwargs):
    kwargs["request"] = request
    template = env.get_template(template_name)
    return Response(template.render(**kwargs), media_type="text/html")


@app.middleware("http")
async def http_middleware(request: Request, call_next):
    request.remote_addr = request.client.host
    if len(await request.body()) < 1024:
        if request.headers.get("Host") == HOST_NAME:
            response = await call_next(request)
            if type(response) == Response:
                for key, value in html_secure_headers.items():
                    response.headers[key] = value
                return response
            if isinstance(response, StreamingResponse):
                for key, value in html_secure_headers.items():
                    response.headers[key] = value
                return response
            elif isinstance(response, dict):
                response = json_response(response)
                for key, value in secure_headers.items():
                    response.headers[key] = value
                return response
            else:
                print("неверный тип ответа", type(response))
                return Response(status_code=415)
        else:
            print("неверный хост", request.headers.get("Host"), HOST_NAME)
            return Response(status_code=403)
    else:
        print("слишком большой запрос", await request.body())
        return Response(status_code=413)


@app.get("/")
@limiter.limit("5/second")
async def index_page(request: Request):
    _ = request
    return json_response({"msg": "login for use", "docs-url": "http://example.com/docs"})


@app.get("/favicon.ico")
@limiter.limit("5/second")
async def favicon_ico(request: Request):
    _ = request
    response = Response(status_code=204)
    response.headers["Cache-Control"] = "cache, age=5454354545234523"
    return response


@app.get("/docs")
@limiter.limit("5/second")
async def docs_page(request: Request):
    return template_request(request, "api_docs.html")


@app.get("/api/pages/")
@limiter.limit("5/second")
async def main_api_page(request: Request):
    return template_request(request, "api/index.html")


# @app.post("/api/shablon")
# @limiter.limit("5/second")
# async def shablon_api(request: Request):
#     request_json = await request.json()
#     token = request_json.get("token")
#     if token:
#         if api_login_required(token)[0]:
#             param = request_json.get("param")
#             if api_send_mail("token", to, theme, message):
#                 return json_response({"res": "ok"})
#             else:
#                 return json_response({"res": "error"}, status_code=500)
#         else:
#             return json_response({"res": "error not login"}, status_code=401)
#     else:
#         return json_response({"res": "error not login"}, status_code=401)


@app.exception_handler(HTTPException)
async def global_error(err: HTTPException):
    try:
        return json_response({"res": "error",
                              "error": err.status_code,
                              "description": err.detail},
                             status_code=err.status_code)
    except:
        return Response(status_code=500)


if __name__ == "__main__":
    HOST_NAME = "192.168.0.6:8000"
    uvicorn.run(app, host="192.168.0.6", port=8000)
    # uvicorn.run(app)
