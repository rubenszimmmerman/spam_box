from unicodedata import name
from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.websockets import WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
import database
from pydantic import BaseModel
from json import dumps
from ConnectionManager import ConnectionManager
from starlette.staticfiles import StaticFiles
from json import loads
import binascii
import os

app = FastAPI(name="tempmail", title="tempmail", description="tempmail", version="1.0")
auth_schema = HTTPBearer(auto_error=False)
app.mount("/home", StaticFiles(directory="hacksec-webmail",
          html=True), name="hacksec-webmail")
database = database.db()
manager = ConnectionManager()

config = {}
try:
    with open("/opt/hacksec_tempmail/hacksec_tempmail/config.json", "r") as config:
        config = loads(config.read())
except:
    print('No config file found. Please create a config.json file.')
    exit()

auth = config['auth']
origins = ["*"]
#app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return RedirectResponse("/home")

@app.websocket('/mailbox')
async def websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_text(dumps({"success": True, "email": database.view()}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get('/mailbox')
async def mailbox():
    try:
        return JSONResponse(dumps({"success": True, "email": database.view()}))
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err)})


@app.websocket('/mailbox/{id}')
async def websocket(websocket: WebSocket, id: int):
    await websocket.accept()
    try:
        await websocket.send_text(dumps({"success": True, "email": database.view_single(id)}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get('/mailbox/{id}')
async def mailbox_id(id: int):
    try:
        return JSONResponse(dumps({"success": True, "email": database.view_single(id)}))
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err)})


@app.websocket('/mailbox/search/{search_term}')
async def websocket(websocket: WebSocket, search_term: str):
    await websocket.accept()
    try:
        await websocket.send_text(dumps({"success": True, "email": database.search(search_term)}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get('/mailbox/search/{search_term}')
async def mailbox_search(search_term: str):
    try:
        return JSONResponse(dumps({"success": True, "email": database.search(search_term)}))
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err)})


@app.websocket('/mailbox/delete/{id}')
async def websocket(websocket: WebSocket, id: int):
    await websocket.accept()
    try:
        await websocket.send_text(dumps({"success": True, "email": database.delete(id)}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get('/mailbox/delete/{id}')
async def mailbox_del(id: int):
    try:
        return JSONResponse(dumps({"success": True, "email": database.delete(id)}))
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err)})


@app.websocket('/mailbox/delete')
async def websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_text(dumps({"success": True, "email": database.delete_all()}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get('/mailbox/delete')
async def mailbox_delete_all():
    try:
        return JSONResponse(dumps({"success": True, "email": database.delete_all()}))
    except Exception as err:
        return JSONResponse({"success": False, "error": str(err)})