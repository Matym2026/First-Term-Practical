from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User, Video
from app.schemas import (
    DownloadUrlResponse,
    UploadUrlRequest,
    UploadUrlResponse,
    VideoCreate,
    VideoOut,
    VideoUpdate,
)
from app.services import s3

router = APIRouter(prefix="/videos", tags=["Videos"])


def get_video_or_404(video_id: int, db: Session) -> Video:
    """Busca un video por id o responde 404."""
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado"
        )
    return video



@router.post("/upload-url", response_model=UploadUrlResponse)
def get_upload_url(
    data: UploadUrlRequest,
    current_user: User = Depends(get_current_user),
):
    object_key = s3.build_object_key(current_user.id, data.filename, data.kind)
    try:
        return s3.generate_upload_url(object_key, data.content_type, data.kind)
    except s3.S3NotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except s3.S3Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar la URL de subida",
        )


@router.post("", response_model=VideoOut, status_code=status.HTTP_201_CREATED)
def create_video(
    data: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    prefix = f"videos/{current_user.id}/"
    if not data.s3_key.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"s3_key inválida: debe empezar con '{prefix}'",
        )

    thumb_prefix = f"thumbnails/{current_user.id}/"
    if data.thumbnail_key and not data.thumbnail_key.startswith(thumb_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"thumbnail_key inválida: debe empezar con '{thumb_prefix}'",
        )

    video = Video(**data.model_dump(), owner_id=current_user.id)
    db.add(video)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un video con ese s3_key",
        )
    db.refresh(video)
    return video


@router.get("", response_model=list[VideoOut])
def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Video).order_by(Video.id.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{video_id}", response_model=VideoOut)
def get_video(video_id: int, db: Session = Depends(get_db)):
    return get_video_or_404(video_id, db)


@router.put("/{video_id}", response_model=VideoOut)
def update_video(
    video_id: int,
    data: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = get_video_or_404(video_id, db)

    
    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este video",
        )

    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(video, field, value)

    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = get_video_or_404(video_id, db)

    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este video",
        )

    s3_key, thumbnail_key = video.s3_key, video.thumbnail_key

    db.delete(video)  
    db.commit()

    
    try:
        s3.delete_object(s3_key, "video")
        if thumbnail_key:
            s3.delete_object(thumbnail_key, "thumbnail")
    except (s3.S3NotConfiguredError, s3.S3Error):
        pass


@router.post("/{video_id}/views", response_model=VideoOut)
def increment_views(video_id: int, db: Session = Depends(get_db)):
    
    get_video_or_404(video_id, db)

    
    db.execute(update(Video).where(Video.id == video_id).values(views=Video.views + 1))
    db.commit()

    
    video = db.get(Video, video_id)
    db.refresh(video)
    return video


@router.get("/{video_id}/download-url", response_model=DownloadUrlResponse)
def get_download_url(video_id: int, db: Session = Depends(get_db)):
    video = get_video_or_404(video_id, db)
    try:
        result = s3.generate_download_url(video.s3_key, "video")
    except s3.S3NotConfiguredError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except s3.S3Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar la URL de descarga",
        )
    return DownloadUrlResponse(video_id=video.id, **result)