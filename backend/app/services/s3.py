import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings

UPLOAD_EXPIRES = 900  
DOWNLOAD_EXPIRES = 3600  


class S3NotConfiguredError(Exception):
    """El bucket no está configurado en las variables de entorno."""


class S3Error(Exception):
    """Falló una operación con S3."""


def _client():
    
    return boto3.client("s3", region_name=settings.AWS_REGION)


def _bucket_for(kind: str) -> str:
    bucket = (
        settings.AWS_S3_BUCKET if kind == "video" else settings.AWS_S3_THUMBNAILS_BUCKET
    )
    if not bucket:
        raise S3NotConfiguredError(
            f"S3 no está configurado para '{kind}'. Define el bucket en el archivo .env"
        )
    return bucket


def build_object_key(user_id: int, filename: str, kind: str) -> str:
    """Genera la ruta del archivo: videos/{user}/{uuid}_{nombre}"""
    folder = "videos" if kind == "video" else "thumbnails"
    safe_name = filename.replace(" ", "_")
    return f"{folder}/{user_id}/{uuid.uuid4().hex}_{safe_name}"


def generate_upload_url(object_key: str, content_type: str, kind: str = "video") -> dict:
    bucket = _bucket_for(kind)
    try:
        url = _client().generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": object_key, "ContentType": content_type},
            ExpiresIn=UPLOAD_EXPIRES,
        )
    except (BotoCoreError, ClientError) as e:
        raise S3Error(str(e))
    return {"upload_url": url, "object_key": object_key, "expires_in": UPLOAD_EXPIRES}


def generate_download_url(object_key: str, kind: str = "video") -> dict:
    bucket = _bucket_for(kind)
    try:
        url = _client().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_key},
            ExpiresIn=DOWNLOAD_EXPIRES,
        )
    except (BotoCoreError, ClientError) as e:
        raise S3Error(str(e))
    return {"url": url, "expires_in": DOWNLOAD_EXPIRES}


def delete_object(object_key: str, kind: str = "video") -> None:
    bucket = _bucket_for(kind)
    try:
        _client().delete_object(Bucket=bucket, Key=object_key)
    except (BotoCoreError, ClientError) as e:
        raise S3Error(str(e))