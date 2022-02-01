from fastapi import FastAPI, Request, Response, Depends,  HTTPException
from fastapi_socketio import SocketManager
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from uuid import UUID, uuid4

from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters


app = FastAPI()
current_user = ""
# # app.config['SECRET_KEY'] = '12345678'
socketio = SocketManager(app=app, cors_allowed_origins="*")

@socketio.on('messagego')
async def handle_msg(*args):
    # print(args[1]['user'])
    global current_user 
    current_user = args[1]['user']
    data = {'user':args[1]['user'], 'msg':args[1]['data']}
    await socketio.emit('message', data)


home = ""
with open('templates/index.html', 'r') as f:
    home = f.read()

@app.get("/")
async def get():
    return HTMLResponse(home)

chat_page = ""
with open('templates/chat.html', 'r') as f:
    chat_page = f.read()
@app.get("/chat")
async def get():
    return HTMLResponse(chat_page)

# @socketio.on('disconnect')
# async def handle_leave(*args):
#     try:
#         await socketio.on('ping')
#     except:
#         print("User left")
#         data = {'user':current_user, 'msg':"left"}
#         await socketio.emit('message', data)


# session management
# API's

class SessionData(BaseModel):
    username: str


cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)


@app.post("/create_session")
async def create_session(name: SessionData, response: Response):

    session = uuid4()
    # data = SessionData(username=name)

    await backend.create(session, name)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"

