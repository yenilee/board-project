from flask import Blueprint

from app.views.user import UserView
from app.views.board import BoardView
from app.views.post import PostView
from app.views.comment import CommentView

def register_api(app):
    UserView.register(app, route_base='/users', trailing_slash=False)
    BoardView.register(app, route_base='/', trailing_slash=False)
    PostView.register(app, route_base='/<board_name>', trailing_slash=False)
    CommentView.register(app, route_base='/<board_name>/<int:post_id>/comment', trailing_slash=False)