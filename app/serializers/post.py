from marshmallow import fields, Schema, post_load
from .user import UserSchema
from .board import BoardCategorySchema
from app.models import Post, Comment, Board, User


class PostCreateSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    tags = fields.List(fields.Str)

    @post_load
    def make_post(self, data, **kwargs):
        post = Post(**data)
        return post


class PostUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()
    tags = fields.List(fields.Str)


class PostDetailSchema(Schema):
    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema, dump_only=("id", "email"))
    title = fields.Str()
    content = fields.Str()
    total_likes_count = fields.Method('count_likes')
    total_comments_count = fields.Method('count_comments')
    tags = fields.List(fields.String)
    created_at = fields.DateTime(dump_only=True)

    def count_likes(self, obj):
        return len(obj.likes)

    def count_comments(self, obt):
        return len(Comment.objects(post=obt.id))


class PostListSchema(Schema):
    id = fields.Str(dump_only=True)
    board = fields.Nested(BoardCategorySchema, dump_only=("id", "name"))
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    title = fields.Str()
    total_likes_count = fields.Method('count_likes')
    total_comments_count = fields.Method('count_comments')
    created_at = fields.DateTime(dump_only=True)

    def count_likes(self, obj):
        return len(obj.likes)

    def count_comments(self, obt):
        return len(Comment.objects(post=obt.id))


class PostListInBoardSchema(PostListSchema):
    class Meta:
        fields = ['id', 'author', 'title', 'total_likes_count', 'total_comments_count', 'created_at']


class PaginatedPostsSchema(Schema):
    total = fields.Integer()
    items = fields.Nested(PostListSchema, many=True)


class PaginatedPostsInBoardSchema(Schema):
    total = fields.Integer()
    items = fields.Nested(PostListInBoardSchema, many=True)


class HighRankingPostListSchema(Schema):
    id = fields.String(attribute="_id")
    board = fields.Method('get_board_id_and_name')
    author = fields.Method('get_author_id_and_name')
    title = fields.Str()
    total_likes_count = fields.Integer()
    total_comments_count = fields.Integer()
    created_at = fields.DateTime(dump_only=True)

    def get_board_id_and_name(self, obj):
        board_id = obj['board']
        return {"id": str(board_id),
                "name": Board.objects(id=board_id).get().name}

    def get_author_id_and_name(self, obj):
        author_id = obj['author']
        return {"id": str(author_id),
                "account": User.objects(id=author_id).get().account}


class PostFilterSchema(Schema):
    tags = fields.Str()
    author = fields.Str()
    title = fields.Str()
    page = fields.Str()

    @post_load
    def filter_post(self, data, page=1,**kwargs):
        post = Post.objects()
        if 'tags' in data:
            post = post(tags__in=data['tags'].split())

        if 'title' in data:
            post = post(title__contains=data['title'])

        if 'author' in data:
            post = post(author__exact=User.objects(account=data['author']).get().id)

        if 'page' in data:
            page = int(data.get('page'))

        return post, page