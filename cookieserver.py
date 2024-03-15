import gzip
from typing import Annotated, Callable, Union, Optional, Dict, Any

from fastapi import APIRouter, Body, FastAPI, HTTPException, Path, Query, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel
import urllib.request
import json
import os

from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5


def bytes_to_key(data: bytes, salt: bytes, output=48) -> bytes:
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]


def encrypt(message: bytes, passphrase: bytes) -> bytes:
    """
    CryptoJS 加密原文
    
    This is a modified copy of https://stackoverflow.com/questions/36762098/how-to-decrypt-password-from-javascript-cryptojs-aes-encryptpassword-passphras
    """
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    length = 16 - (len(message) % 16)
    data = message + (chr(length) * length).encode()
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(data))


def decrypt(encrypted: str | bytes, passphrase: bytes) -> bytes:
    """
    CryptoJS 解密密文
    
    来源同encrypt
    """
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    data = aes.decrypt(encrypted[16:])
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


def get_decrypted_data(uuid: str, password: str,
                       encrypted: str) -> Optional[Dict[str, Any]]:
    key_md5 = md5()
    key_md5.update((uuid + '-' + password).encode('utf-8'))
    aes_key = (key_md5.hexdigest()[:16]).encode('utf-8')

    if encrypted is not None:
        try:
            decrypted_data = decrypt(encrypted, aes_key).decode('utf-8')
            decrypted_data = json.loads(decrypted_data)
            if 'cookie_data' in decrypted_data:
                return decrypted_data
        except Exception as e:
            return None
    else:
        return None


class GzipRequest(Request):

    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = gzip.decompress(body)
            self._body = body
        return self._body


class GzipRoute(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = GzipRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


router = APIRouter(route_class=GzipRoute)


class UpdateCookieRequest(BaseModel):
    uuid: str = Query(min_length=5, pattern="^[a-zA-Z0-9]+$")
    encrypted: str = Query(min_length=1, max_length=1024 * 1024 * 50)


class PostCookieRequest(BaseModel):
    password: str


class Message(BaseModel):
    test: Union[str, None] = None
    encrypted: Union[str, None] = None


ROOT = "/cookiecloud"

PATH_ROOT = os.path.join(os.path.dirname(__file__), "/cookie_data")

if not os.path.exists(PATH_ROOT):
    os.makedirs(PATH_ROOT)


@router.get("/", response_class=PlainTextResponse)
def get_root():
    return "Hello World! API ROOT = " + ROOT


@router.post("/", response_class=PlainTextResponse)
def post_root():
    return "Hello World! API ROOT = " + ROOT


@router.post("/update")
async def update_cookie(req: UpdateCookieRequest):
    file_path = os.path.join(PATH_ROOT, os.path.basename(req.uuid) + ".json")
    content = json.dumps({"encrypted": req.encrypted})
    with open(file_path, encoding="utf-8", mode="w") as file:
        file.write(content)
    read_content = None
    with open(file_path, encoding="utf-8", mode="r") as file:
        read_content = file.read()
    if (read_content == content):
        return {"action": "done"}
    else:
        return {"action": "error"}


def load_encrypt_data(uuid: str) -> Dict[str, Any]:
    file_path = os.path.join(PATH_ROOT, os.path.basename(uuid) + ".json")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Item not found")

    # 读取文件
    with open(file_path, encoding="utf-8", mode="r") as file:
        read_content = file.read()
    data = json.loads(read_content)
    return data


@router.get("/get/{uuid}")
async def get_cookie(
        uuid: Annotated[str, Path(min_length=5, pattern="^[a-zA-Z0-9]+$")]):
    return load_encrypt_data(uuid)


@router.post("/get/{uuid}")
async def post_cookie(
        uuid: Annotated[str, Path(min_length=5, pattern="^[a-zA-Z0-9]+$")],
        request: PostCookieRequest):
    data = load_encrypt_data(uuid)
    return get_decrypted_data(uuid, request.password, data["encrypted"])
