from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.permissions import is_moderator_or_admin
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.post import PostCreate, PostResponse
from app.services.audit_service import log_action
from app.utils.helpers import clean_text


router = APIRouter(
    prefix="/community",
    tags=["Community"],
)


def authors_map(db: Session, user_ids: set[int]) -> dict[int, str]:
    """লেখকের আইডি -> ইউজারনেম। একবার কুয়েরিতে সব নাম আনে।"""
    if not user_ids:
        return {}

    rows = db.query(User.id, User.username).filter(User.id.in_(user_ids)).all()

    return {row.id: row.username for row in rows}


def post_out(post: Post, names: dict[int, str]) -> dict:
    return {
        "id": post.id,
        "user_id": post.user_id,
        "author_username": names.get(post.user_id),
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
    }


def comment_out(comment: Comment, names: dict[int, str]) -> dict:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "author_username": names.get(comment.user_id),
        "content": comment.content,
        "created_at": comment.created_at,
    }


def can_manage(user: User, owner_id: int) -> bool:
    """নিজের লেখা, অথবা মডারেটর/অ্যাডমিন হলে যে কোনোটা"""
    return user.id == owner_id or is_moderator_or_admin(user.role)


@router.get("/posts", response_model=list[PostResponse])
def get_posts(
    response: Response,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    response.headers["X-Total-Count"] = str(query.count())

    posts = query.order_by(Post.id.desc()).offset(offset).limit(limit).all()
    names = authors_map(db, {post.user_id for post in posts})

    return [post_out(post, names) for post in posts]


@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = Post(
        user_id=current_user.id,
        title=clean_text(data.title),
        content=data.content.strip(),
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    log_action(db, current_user.id, "post.create", "posts", post.id)

    return post_out(post, {current_user.id: current_user.username})


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(404, "Post not found")

    if not can_manage(current_user, post.user_id):
        raise HTTPException(403, "Permission denied")

    db.delete(post)
    db.commit()

    log_action(db, current_user.id, "post.delete", "posts", post_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/comments/{post_id}", response_model=list[CommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db),
):
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.id.asc())
        .all()
    )
    names = authors_map(db, {comment.user_id for comment in comments})

    return [comment_out(comment, names) for comment in comments]


@router.post(
    "/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == data.post_id).first()

    if not post:
        raise HTTPException(404, "Post not found")

    text = data.content.strip()
    if not text:
        raise HTTPException(400, "Comment cannot be empty")

    comment = Comment(
        post_id=data.post_id,
        user_id=current_user.id,
        content=text,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment_out(comment, {current_user.id: current_user.username})


@router.delete(
    "/comments/item/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(404, "Comment not found")

    if not can_manage(current_user, comment.user_id):
        raise HTTPException(403, "Permission denied")

    db.delete(comment)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
