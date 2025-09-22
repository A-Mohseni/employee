import io
import os
from fastapi.testclient import TestClient
from bson import ObjectId

from backend.main import app
from utils.jwt import create_access_token


client = TestClient(app)


def _make_token(user_id: str, role: str = "employee") -> str:
    payload = {"user_id": user_id, "role": role}
    return create_access_token(payload, subject=user_id)


def test_avatar_endpoints_upload_get_delete():
    # Arrange: create a fake user id and token
    user_id = str(ObjectId())
    token = _make_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create an in-memory PNG file (minimal PNG header + IHDR chunk is enough for content-type checks)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR"  # IHDR chunk start
        b"\x00\x00\x00\x01\x00\x00\x00\x01"  # 1x1 px
        b"\x08\x02\x00\x00\x00"  # 8-bit, truecolor
        b"\x90wS\xde"  # CRC
    )
    file = ("avatar.png", io.BytesIO(png_bytes), "image/png")

    # Act: upload
    resp_upload = client.post("/avatar/me", headers=headers, files={"file": file})
    assert resp_upload.status_code == 201, resp_upload.text
    data = resp_upload.json()
    assert data["user_id"] == user_id
    assert data["id"]
    assert data["avatar_url"].startswith("./uploads/avatars/")

    # Act: get
    resp_get = client.get(f"/avatar/{user_id}", headers=headers)
    assert resp_get.status_code == 200, resp_get.text
    data_get = resp_get.json()
    assert data_get["user_id"] == user_id

    # Act: delete
    resp_del = client.delete(f"/avatar/{user_id}", headers=headers)
    assert resp_del.status_code == 200, resp_del.text
    assert resp_del.json().get("message")


def test_avatar_upload_invalid_content_type_returns_400():
    user_id = str(ObjectId())
    token = _make_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Prepare a text file pretending to be an image
    txt_bytes = b"not an image"
    file = ("avatar.txt", io.BytesIO(txt_bytes), "text/plain")

    resp_upload = client.post("/avatar/me", headers=headers, files={"file": file})
    assert resp_upload.status_code == 400


def test_avatar_get_forbidden_for_other_user():
    # First user uploads an avatar
    user1 = str(ObjectId())
    token1 = _make_token(user1, role="employee")
    headers1 = {"Authorization": f"Bearer {token1}"}

    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
    )
    file = ("avatar.png", io.BytesIO(png_bytes), "image/png")
    resp_upload = client.post("/avatar/me", headers=headers1, files={"file": file})
    assert resp_upload.status_code == 201

    # Second non-admin tries to GET first user's avatar -> 403
    user2 = str(ObjectId())
    token2 = _make_token(user2, role="employee")
    headers2 = {"Authorization": f"Bearer {token2}"}
    resp_get = client.get(f"/avatar/{user1}", headers=headers2)
    assert resp_get.status_code == 403


