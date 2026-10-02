from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


ALLOWED_CONTENT_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_THUMBNAIL_TYPES = {"image/jpeg", "image/png", "image/webp"}



class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_max_bytes(cls, v: str) -> str:
        
        if len(v.encode("utf-8")) > 72:
            raise ValueError("La contraseña es demasiado larga (máximo 72 bytes)")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()


class UserOut(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



class VideoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    filename: str = Field(min_length=1, max_length=255)
    s3_key: str = Field(min_length=1, max_length=500)
    thumbnail_key: str | None = Field(default=None, max_length=500)


class VideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    filename: str
    s3_key: str
    thumbnail_key: str | None
    owner_id: int
    views: int
    created_at: datetime
    updated_at: datetime


class UploadUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str
    kind: str = "video"  

    @field_validator("filename")
    @classmethod
    def filename_safe(cls, v: str) -> str:
        if "/" in v or "\\" in v or ".." in v:
            raise ValueError("Nombre de archivo inválido")
        return v

    @field_validator("kind")
    @classmethod
    def kind_valid(cls, v: str) -> str:
        if v not in ("video", "thumbnail"):
            raise ValueError("kind debe ser 'video' o 'thumbnail'")
        return v

    @model_validator(mode="after")
    def content_type_matches_kind(self):
        allowed = (
            ALLOWED_CONTENT_TYPES if self.kind == "video" else ALLOWED_THUMBNAIL_TYPES
        )
        if self.content_type not in allowed:
            raise ValueError(
                f"Tipo no permitido para {self.kind}. "
                f"Usa uno de: {', '.join(sorted(allowed))}"
            )
        return self


class UploadUrlResponse(BaseModel):
    upload_url: str
    object_key: str
    expires_in: int


class DownloadUrlResponse(BaseModel):
    video_id: int
    url: str
    expires_in: int



class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    user_id: int
    video_id: int
    created_at: datetime
    updated_at: datetime