from fastapi import status, HTTPException, Response, Depends, APIRouter
from typing import List, Optional
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


# @app.get('/posts')
# def get_posts():
#     cursor.execute("""SELECT * FROM posts; """)
#     posts = cursor.fetchall()
#     return {'data': posts}


@router.get('/', response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ''):

    # see only posts associated with a user
    # posts = db.query(models.Post).filter(
    #     models.Post.owner_id == current_user.id).all()

    # see all posts
    # posts = db.query(models.Post).filter(
    #     models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


# @app.post('/posts', status_code=status.HTTP_201_CREATED)
# def create_posts(post: Post):
#     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
#                    (post.title, post.content, post.published))
#     new_post = cursor.fetchone()
#     conn.commit()
#     return {'data': new_post}

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=current_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# @app.get('/posts/{id}')
# def get_post(id: int):
#     cursor.execute(
#         """SELECT * FROM posts WHERE id = %s returning *""", (str(id),))
#     post = cursor.fetchone()

#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Post with id: {id} was not found')
#     return {'post_detail': post}

@router.get('/{id}', response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} was not found')

    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail=f'Not authorized to perform requested action')

    return post


# @app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cursor.execute(
#         """DELETE FROM posts WHERE id= %s returning *""", (str(id),))
#     deleted_post = cursor.fetchone()
#     conn.commit()

#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Post with id: {id} does not exist')
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} does not exist')

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not authorized to perform requested action')

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# @app.put('/posts/{id}')
# def update_post(id: int, post: Post):
#     cursor.execute("""UPDATE posts SET title = %s, content= %s, published= %s WHERE id =%s returning *""",
#                    (post.title, post.content, post.published, str(id)))
#     updated_post = cursor.fetchone()
#     conn.commit()

#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Post with id: {id} does not exist')

#     return {'data': updated_post}


@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} does not exist')

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not authorized to perform requested action')

    post_query.update(updated_post.model_dump(), synchronize_session=False)

    db.commit()

    return post_query.first()
