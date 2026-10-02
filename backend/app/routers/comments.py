from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Comment, User, Video
from app.schemas import CommentCreate, CommentOut, CommentUpdate

router = APIRouter(tags=["Comentarios"])


def get_comment_or_404(comment_id: int, db: Session) -> Comment:
    """Busca un comentario por id o responde 404."""
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado"
        )
    return comment


@router.post(
    "/videos/{video_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    video_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # El video debe existir
    if db.get(Video, video_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado"
        )

    comment = Comment(content=data.content, user_id=current_user.id, video_id=video_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/videos/{video_id}/comments", response_model=list[CommentOut])
def list_comments(
    video_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if db.get(Video, video_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado"
        )

    stmt = (
        select(Comment)
        .where(Comment.video_id == video_id)
        .order_by(Comment.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.scalars(stmt).all()


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_or_404(comment_id, db)

    # Solo el autor puede editar
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este comentario",
        )

    comment.content = data.content
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_or_404(comment_id, db)

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este comentario",
        )

    db.delete(comment)
    db.commit()